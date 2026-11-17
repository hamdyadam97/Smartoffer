"""نقل بيانات برنامج المشاهد القديم (ElmashahedBackend) لـ Smart Offer.

بيقرا ملف الـ SQLite بتاع البرنامج القديم مباشرة (من غير ما يحتاج كوده):
  المعاهد -> الفروع (بالاسم، أو --map)
  الدبلومات والدورات -> التخصصات (بالنوع والاسم)
  العملاء -> الطلاب (برقم الهوية، وبعدين بالجوال)
  المشاهد -> المشاهد (بنفس الأرقام) + قوالب الـ PDF والصور

من غير --commit بيعمل تجربة كاملة ويرجع في كل حاجة (مفيش أي تغيير).
تشغيله أكتر من مرة آمن: المشهد اللي رقمه موجود بيتخطى.

مثال:
  python manage.py import_mashahed --source /opt/ElmashahedBackend/db.sqlite3 \
      --media /opt/ElmashahedBackend/media
  python manage.py import_mashahed ... --map 7=3 --commit
"""
import os
import re
import shutil
import sqlite3
from datetime import date, datetime, timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from accounts.models import Person
from core.models import Branch, Company
from courses.models import Course
from permits.models import Permit, PermitTemplate
from students.models import Contact, Student


class DryRun(Exception):
    pass


# الحقول اللي هي ForeignKey في البرنامج القديم (في JSON بتيجي «institute»: 5 ← عمود institute_id)
JSON_FOREIGN_KEYS = {'institute', 'client', 'diploma', 'course', 'issued_by', 'referral_employee',
                     'registration_officer', 'registered_by', 'category', 'managed_institute'}
# ManyToMany اللي محتاجينها: (الموديل، الحقل) -> جدول الربط
JSON_M2M = {('programs.diploma', 'institutes'): ('programs_diploma_institutes', 'diploma_id'),
            ('programs.course', 'institutes'): ('programs_course_institutes', 'course_id')}


def sqlite_from_dumpdata(path):
    """ملف dumpdata (JSON) من البرنامج القديم -> SQLite في الذاكرة بنفس أسماء الجداول والأعمدة.
    كده الأمر بيشتغل مهما كانت داتابيز البرنامج القديم (Postgres أو SQLite)."""
    import json
    with open(path, encoding='utf-8') as f:
        objects = json.load(f)
    tables, links = {}, {}
    for obj in objects:
        label = obj['model']
        row = {'id': obj['pk']}
        for name, value in obj['fields'].items():
            if (label, name) in JSON_M2M:
                table, own_col = JSON_M2M[(label, name)]
                links.setdefault(table, []).extend((obj['pk'], other) for other in value)
            elif isinstance(value, list):
                continue  # M2M مش محتاجينها (groups، صلاحيات...)
            else:
                row[f'{name}_id' if name in JSON_FOREIGN_KEYS else name] = value
        tables.setdefault(label.replace('.', '_'), []).append(row)
    db = sqlite3.connect(':memory:')
    for table, rows in tables.items():
        columns = sorted({c for r in rows for c in r})
        db.execute(f'create table {table} ({", ".join(columns)})')
        db.executemany(f'insert into {table} ({", ".join(columns)}) values ({", ".join("?" * len(columns))})',
                       [[r.get(c) for c in columns] for r in rows])
    for (label, _), (table, own_col) in JSON_M2M.items():
        db.execute(f'create table if not exists {table} (id integer primary key, {own_col}, institute_id)')
        db.executemany(f'insert into {table} ({own_col}, institute_id) values (?, ?)', links.get(table, []))
    return db


TYPE_PREFIXES = [('دبلومة', 'دبلوم'), ('دبلوم', 'دبلوم'), ('دورة', 'دورة'), ('دوره', 'دورة')]


def split_program(name, kind):
    """(النوع، الاسم من غير كلمة دبلوم/دورة في أوله)."""
    name = re.sub(r'\s+', ' ', (name or '').strip())
    program_type = 'دورة' if kind == 'course' else 'دبلوم'
    for prefix, _ in TYPE_PREFIXES:
        if name.startswith(prefix + ' ') and name[len(prefix):].strip():
            return program_type, name[len(prefix):].strip()
    return program_type, name


def digits(value):
    return re.sub(r'\D', '', str(value or ''))


def as_date(value):
    if not value:
        return None
    if isinstance(value, date):
        return value
    return datetime.fromisoformat(str(value)[:10]).date()


class Command(BaseCommand):
    help = 'نقل بيانات برنامج المشاهد القديم (SQLite) لـ Smart Offer'

    def add_arguments(self, parser):
        parser.add_argument('--source', required=True,
                            help='db.sqlite3 بتاع البرنامج القديم، أو ملف JSON من dumpdata بتاعه')
        parser.add_argument('--media', default='', help='فولدر media بتاع البرنامج القديم (للوجو والتوقيع والختم)')
        parser.add_argument('--map', action='append', default=[], metavar='INSTITUTE_ID=BRANCH_CODE',
                            help='ربط معهد بفرع يدوي (ممكن تتكرر)')
        parser.add_argument('--create-branches', action='store_true',
                            help='المعاهد اللي مالهاش فرع مطابق تتعمل فروع جديدة')
        parser.add_argument('--commit', action='store_true', help='نفّذ فعلاً (من غيرها تجربة بس)')

    # ------------------------------------------------------------------ helpers
    def rows(self, sql, *params):
        try:
            return [dict(r) for r in self.db.execute(sql, params)]
        except sqlite3.OperationalError as exc:
            if 'no such table' in str(exc):  # جدول فاضي في ملف الـ JSON (مثلاً مفيش قوالب)
                return []
            raise

    def log(self, msg, style=None):
        self.stdout.write(style(msg) if style else msg)

    def copy_media(self, rel_path, field):
        """بيعمل نسخة من صورة البرنامج القديم في media بتاع Smart Offer ويحطها في الحقل."""
        if not rel_path or not self.media_root:
            return False
        src = os.path.join(self.media_root, rel_path)
        if not os.path.exists(src):
            self.warnings.append(f'صورة مش موجودة: {src}')
            return False
        dest_rel = os.path.join('mashahed', rel_path).replace('\\', '/')
        dest = os.path.join(settings.MEDIA_ROOT, dest_rel)
        if self.commit:
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copy2(src, dest)
        field.name = dest_rel
        return True

    # ------------------------------------------------------------------ main
    def handle(self, *args, **opts):
        if not os.path.exists(opts['source']):
            raise CommandError(f'الملف مش موجود: {opts["source"]}')
        if opts['source'].endswith('.json'):
            self.db = sqlite_from_dumpdata(opts['source'])
        else:
            self.db = sqlite3.connect(f'file:{opts["source"]}?mode=ro', uri=True)
        self.db.row_factory = sqlite3.Row
        missing = {'institutes_institute', 'permissions_permissionslip'} - {
            r[0] for r in self.db.execute("select name from sqlite_master where type='table'")}
        if missing or not self.db.execute('select count(*) from institutes_institute').fetchone()[0]:
            self.db.close()
            raise CommandError('الملف ده مفيهوش بيانات البرنامج القديم (مفيش معاهد). لو البرنامج شغال على Postgres '
                               'طلّع البيانات بـ dumpdata واستخدم ملف الـ JSON.')
        self.media_root = opts['media']
        self.commit = opts['commit']
        self.warnings = []
        self.stats = dict.fromkeys(
            ['branches_new', 'courses_matched', 'courses_new', 'students_matched', 'students_new',
             'permits_new', 'permits_skipped', 'templates'], 0)
        manual = {}
        for item in opts['map']:
            try:
                inst_id, code = item.split('=')
                manual[int(inst_id)] = int(code)
            except ValueError:
                raise CommandError(f'--map لازم يبقى كده: 7=3 (رقم المعهد=كود الفرع). اللي اتكتب: {item}')

        try:
            with transaction.atomic():
                self.map_branches(manual, opts['create_branches'])
                self.users = self.map_users()
                self.programs = self.import_programs()
                self.clients = self.import_clients()
                self.import_permits()
                self.import_templates()
                self.report()
                if not self.commit:
                    raise DryRun
        except DryRun:
            self.log('\nدي كانت تجربة: مفيش أي حاجة اتسجلت. لو النتيجة تمام شغّل نفس الأمر وزوّد --commit',
                     self.style.WARNING)
        else:
            self.log('\nتم النقل.', self.style.SUCCESS)
        finally:
            self.db.close()

    # ------------------------------------------------------------------ branches
    def map_branches(self, manual, create):
        institutes = self.rows('select * from institutes_institute order by id')
        branches = list(Branch.objects.all())
        self.branch_of = {}
        problems = []
        self.log('المعاهد -> الفروع:')
        for inst in institutes:
            branch, how = None, ''
            if inst['id'] in manual:
                branch = Branch.objects.filter(code=manual[inst['id']]).first()
                if not branch:
                    raise CommandError(f'مفيش فرع كوده {manual[inst["id"]]} (--map {inst["id"]}=...)')
                how = 'يدوي'
            else:
                exact = [b for b in branches if b.name.strip() == inst['name'].strip()]
                partial = [b for b in branches if b.name.strip() and (b.name.strip() in inst['name']
                           or b.name.strip() == (inst['city'] or '').strip())]
                if exact:
                    branch, how = exact[0], 'نفس الاسم'
                elif len(partial) == 1:
                    branch, how = partial[0], 'الاسم/المدينة'
                elif len(partial) > 1:
                    problems.append(f'  [{inst["id"]}] {inst["name"]}: أكتر من فرع ممكن '
                                    f'({", ".join(f"{b.code}-{b.name}" for b in partial)}) -> استخدم --map {inst["id"]}=كود')
                    continue
            if branch is None and create:
                branch = self.create_branch(inst)
                how = 'فرع جديد'
            if branch is None:
                problems.append(f'  [{inst["id"]}] {inst["name"]}: مفيش فرع مطابق -> --map {inst["id"]}=كود '
                                'أو --create-branches')
                continue
            self.branch_of[inst['id']] = branch
            self.fill_branch(branch, inst)
            self.log(f'  [{inst["id"]}] {inst["name"]}  ->  {branch.code} - {branch.name}  ({how})')
        if problems:
            self.log('\nمعاهد محتاجة تتربط بفرع:', self.style.ERROR)
            for p in problems:
                self.log(p, self.style.ERROR)
            self.log('الفروع الموجودة: ' + ', '.join(f'{b.code}-{b.name}' for b in branches))
            raise CommandError('صلّح ربط المعاهد الأول (مفيش حاجة اتسجلت).')

    def create_branch(self, inst):
        company = Company.objects.first()
        if company is None:
            raise CommandError('مفيش شركة في Smart Offer عشان الفروع الجديدة تتبعها.')
        code = (Branch.objects.order_by('-code').values_list('code', flat=True).first() or 0) + 1
        self.stats['branches_new'] += 1
        return Branch.objects.create(company=company, code=code, name=inst['name'], licence_code=inst['license_number'] or '',
                                     phone1=inst['phone'] or '', email=inst['email'] or '', address=inst['address'] or '')

    def fill_branch(self, branch, inst):
        """بيكمل بيانات الفرع الفاضية بس من المعهد (مابيغيرش حاجة موجودة)."""
        changed = False
        if not branch.licence_code and inst['license_number']:
            branch.licence_code, changed = inst['license_number'], True
        if not branch.logo and self.copy_media(inst['logo'], branch.logo):
            changed = True
        if not branch.signature and self.copy_media(inst['signature_image'], branch.signature):
            changed = True
        if changed:
            branch.save()

    # ------------------------------------------------------------------ users
    def map_users(self):
        """موظفين البرنامج القديم -> موظفين Smart Offer بالإيميل (مابنعملش حسابات جديدة)."""
        result = {}
        for user in self.rows('select id, email, username, first_name, last_name from accounts_user'):
            person = Person.objects.filter(email__iexact=(user['email'] or '').strip()).first() if user['email'] else None
            name = f'{user["first_name"] or ""} {user["last_name"] or ""}'.strip() or user['username']
            result[user['id']] = (person, name)
        return result

    # ------------------------------------------------------------------ programs
    def import_programs(self):
        result = {}
        for kind, table in (('diploma', 'programs_diploma'), ('course', 'programs_course')):
            links = {}
            for row in self.rows(f'select {kind}_id as pid, institute_id from {table}_institutes'):
                links.setdefault(row['pid'], set()).add(row['institute_id'])
            for prog in self.rows(f'select * from {table}'):
                program_type, name = split_program(prog['name'], kind)
                branches = {self.branch_of[i] for i in links.get(prog['id'], ()) if i in self.branch_of}
                branch = branches.pop() if len(branches) == 1 else None  # أكتر من فرع = لكل الفروع
                existing = Course.objects.filter(program_type=program_type, name__iexact=name)
                course = existing.filter(branch=branch).first() or existing.filter(branch__isnull=True).first()
                if course is None and branch is None:
                    course = existing.first()
                if course:
                    self.stats['courses_matched'] += 1
                elif not prog['is_deleted']:
                    period = prog['duration'] or (f'{prog["duration_months"]} شهر' if prog['duration_months'] else '')
                    course = Course.objects.create(
                        program_type=program_type, name=name, branch=branch, period=period, hours=prog['hours'],
                        start_date=as_date(prog['start_date']), end_date=as_date(prog['end_date']))
                    self.stats['courses_new'] += 1
                result[(kind, prog['id'])] = (course, f'{program_type} {name}')
        return result

    # ------------------------------------------------------------------ clients
    def import_clients(self):
        result = {}
        for client in self.rows('select * from clients_client'):
            branch = self.branch_of.get(client['institute_id'])
            national_id = (client['national_id'] or '').strip()
            student = None
            if national_id:
                students = Student.objects.filter(contact__identity_number=national_id).select_related('contact')
                student = students.filter(branch=branch).first() or students.first()
            if student is None and client['phone'] and branch:
                phone = digits(client['phone'])[-9:]
                for s in Student.objects.filter(branch=branch).select_related('contact').exclude(contact__mobile=''):
                    if phone and digits(s.contact.mobile)[-9:] == phone:
                        student = s
                        break
            if student:
                self.stats['students_matched'] += 1
                if national_id and not student.contact.identity_number:
                    student.contact.identity_number = national_id
                    student.contact.save(update_fields=['identity_number'])
            elif branch:
                student = self.create_student(client, branch)
                self.stats['students_new'] += 1
            else:
                self.warnings.append(f'العميل {client["full_name"]} مالوش معهد معروف، اتخطى')
            result[client['id']] = student
        return result

    def create_student(self, client, branch):
        parts = (client['full_name'] or f'{client["first_name"]} {client["last_name"]}').split()
        contact = Contact.objects.create(
            first_name=parts[0] if parts else '-',
            second_name=parts[1] if len(parts) > 2 else '',
            third_name=' '.join(parts[2:-1]) if len(parts) > 3 else '',
            forth_name=parts[-1] if len(parts) > 1 else '',
            identity_number=(client['national_id'] or '').strip(), mobile=client['phone'] or '',
            birth_date=as_date(client['birth_date']), address=client['address'] or '',
        )
        return Student.objects.create(contact=contact, branch=branch)

    # ------------------------------------------------------------------ permits
    def import_permits(self):
        for row in self.rows('select * from permissions_permissionslip order by id'):
            if row['is_deleted']:
                self.stats['permits_skipped'] += 1
                continue
            if Permit.objects.filter(number=row['permission_number']).exists():
                self.stats['permits_skipped'] += 1
                continue
            student = self.clients.get(row['client_id'])
            branch = self.branch_of.get(row['institute_id'])
            if not student or not branch:
                self.warnings.append(f'المشهد {row["permission_number"]}: الطالب أو الفرع مش معروف، اتخطى')
                continue
            kind = 'course' if row['course_id'] else 'diploma'
            course, program_name = self.programs.get((kind, row['course_id'] or row['diploma_id']), (None, ''))
            issued_by, issuer_name = self.users.get(row['issued_by_id'], (None, ''))
            referral, _ = self.users.get(row['referral_employee_id'], (None, ''))
            notes = row['notes'] or ''
            if row['issued_by_id'] and not issued_by and issuer_name:
                notes = (notes + '\n' if notes else '') + f'أصدره في النظام القديم: {issuer_name}'
            issue_date = as_date(row['issue_date']) or timezone.localdate()
            permit = Permit.objects.create(
                number=row['permission_number'], student=student, branch=branch, course=course,
                program_name=program_name, study_mode=row['study_mode'] or '', issue_date=issue_date,
                expiry_date=as_date(row['expiry_date']) or issue_date + timedelta(days=365),
                status=row['status'] if row['status'] in dict(Permit.STATUS_CHOICES) else Permit.STATUS_ACTIVE,
                notes=notes, issued_by=issued_by, issued_from_public=bool(row['issued_from_public']),
                referral_employee=referral, referral_code=row['referral_code'] or '',
            )
            if row['created_at']:
                created = datetime.fromisoformat(str(row['created_at']).replace(' ', 'T')[:26])
                if timezone.is_naive(created):
                    created = timezone.make_aware(created, timezone.UTC)
                Permit.objects.filter(pk=permit.pk).update(created_at=created)
            self.stats['permits_new'] += 1

    # ------------------------------------------------------------------ templates
    def import_templates(self):
        institutes = {i['id']: i for i in self.rows('select * from institutes_institute')}
        officers = {user_id: name for user_id, (_, name) in self.users.items()}
        for row in self.rows('select * from permissions_permissiontemplate where is_deleted = 0'):
            branch = self.branch_of.get(row['institute_id'])
            if not branch:
                continue
            if PermitTemplate.objects.filter(branch=branch).exists():
                self.warnings.append(f'الفرع {branch.name} عنده قالب مشهد بالفعل، القالب القديم ما اتنقلش')
                continue
            inst = institutes.get(row['institute_id'], {})
            template = PermitTemplate(
                branch=branch, institute_name=inst.get('name', ''), header_content=row['header_content'] or '', body_content=row['body_content'] or '',
                footer_content=row['footer_content'] or '', custom_css=row['custom_css'] or '',
                font_family=row['font_family'] if row['font_family'] in dict(PermitTemplate.FONT_CHOICES) else 'arial',
                page_size=row['page_size'] or 'A4', orientation=row['orientation'] or 'portrait',
                registration_officer=officers.get(inst.get('registration_officer_id'), ''),
            )
            self.copy_media(inst.get('stamp_image'), template.stamp_image)
            self.copy_media(inst.get('background_img'), template.background_image)
            template.save()
            self.stats['templates'] += 1

    # ------------------------------------------------------------------ report
    def report(self):
        s = self.stats
        self.log('\nالنتيجة:', self.style.MIGRATE_HEADING)
        self.log(f'  فروع جديدة: {s["branches_new"]}')
        self.log(f'  تخصصات: {s["courses_matched"]} موجودة قبل كده، {s["courses_new"]} جديدة')
        self.log(f'  طلاب: {s["students_matched"]} موجودين قبل كده، {s["students_new"]} جداد')
        self.log(f'  مشاهد: {s["permits_new"]} اتنقلت، {s["permits_skipped"]} اتخطت (ممسوحة أو منقولة قبل كده)')
        self.log(f'  قوالب: {s["templates"]}')
        if self.warnings:
            self.log('\nملاحظات:', self.style.WARNING)
            for w in self.warnings:
                self.log('  - ' + w)
