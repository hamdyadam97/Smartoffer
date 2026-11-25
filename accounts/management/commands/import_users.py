"""إضافة موظفين من شيت إكسل (أو CSV) فيه: الاسم | اسم المستخدم | الفرع.

الإيميل = اسم المستخدم@الدومين. كل واحد بياخد كلمة المرور اللي تحددها ودور «موظف» على فرعه.
الموجود قبل كده مابيتلمسش (ولا كلمة المرور بتاعته بتتغير).
من غير --commit بيعمل تجربة ويطبع اللي هيحصل بس.

  python manage.py import_users users.xlsx --domain ahli-fao-grp.com
  python manage.py import_users users.xlsx --domain ahli-fao-grp.com --map "الثقة الدائمة=12" --commit
"""
import csv
import re
from collections import Counter, defaultdict
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from accounts.models import EmployeeRole, Person, Role
from core.models import Branch

from .import_employees import split_name

NAME_COLS = ('الاسم', 'اسم الموظف', 'name')
USER_COLS = ('اسم المستخدم', 'username', 'البريد الإلكتروني', 'الإيميل', 'email')
BRANCH_COLS = ('الفرع', 'branch')
USERNAME_RE = re.compile(r'^[a-z0-9][a-z0-9._-]*$')
NOISE_WORDS = {'فرع', 'معهد', '(رجال)', '(نساء)', 'رجال', 'نساء'}


def normalize(text):
    text = str(text or '').strip()
    for a, b in (('أ', 'ا'), ('إ', 'ا'), ('آ', 'ا'), ('ة', 'ه'), ('ى', 'ي'), ('ـ', '')):
        text = text.replace(a, b)
    return re.sub(r'\s+', ' ', text)


def branch_words(name):
    return [w for w in re.split(r'[\s()\-]+', normalize(name)) if w and w not in NOISE_WORDS]


def match_branch(sheet_name, branches):
    """فرع البرنامج اللي كل كلماته موجودة في اسم الفرع اللي في الشيت (أكتر واحد كلمات يكسب).
    «فرع الفاو المتقدم بالرياض» -> «الفاو الرياض». لو اتنين متعادلين: None."""
    target = normalize(sheet_name)
    scored = []
    for branch in branches:
        words = branch_words(branch.name)
        if words and all(w in target for w in words):
            scored.append((len(words), branch))
    if not scored:
        return None
    scored.sort(key=lambda x: -x[0])
    if len(scored) > 1 and scored[0][0] == scored[1][0]:
        return None
    return scored[0][1]


def read_rows(path):
    path = Path(path)
    if not path.exists():
        raise CommandError(f'الملف مش موجود: {path}')
    if path.suffix.lower() in ('.xlsx', '.xlsm'):
        from openpyxl import load_workbook
        sheet = load_workbook(path, read_only=True, data_only=True).active
        table = [[('' if c is None else str(c).strip()) for c in row] for row in sheet.iter_rows(values_only=True)]
    else:
        with open(path, encoding='utf-8-sig', newline='') as f:
            table = [[c.strip() for c in row] for row in csv.reader(f)]

    for i, header in enumerate(table):
        def col(names):
            return next((header.index(n) for n in names if n in header), None)
        name_i, user_i, branch_i = col(NAME_COLS), col(USER_COLS), col(BRANCH_COLS)
        if user_i is not None:
            break
    else:
        raise CommandError('مالقيتش عمود «اسم المستخدم» في الملف')

    def cell(row, idx):
        return row[idx] if idx is not None and idx < len(row) else ''

    return [{'line': n, 'name': cell(row, name_i), 'username': cell(row, user_i), 'branch': cell(row, branch_i)}
            for n, row in enumerate(table[i + 1:], start=i + 2) if any(row)]


class Command(BaseCommand):
    help = 'إضافة موظفين من شيت إكسل: الاسم | اسم المستخدم | الفرع'

    def add_arguments(self, parser):
        parser.add_argument('file', help='ملف xlsx أو csv')
        parser.add_argument('--domain', required=True, help='اللي بعد @ في الإيميل، مثلاً ahli-fao-grp.com')
        parser.add_argument('--password', default='Smart@123')
        parser.add_argument('--role', default='موظف', help='اسم الدور اللي كل واحد هياخده على فرعه')
        parser.add_argument('--map', action='append', default=[], metavar='"اسم الفرع في الشيت=كود"',
                            help='لو فرع ماتعرفش عليه أوتوماتيك')
        parser.add_argument('--allow-other-domain', action='store_true',
                            help='اعمل حساب جديد حتى لو نفس اسم المستخدم موجود بإيميل تاني')
        parser.add_argument('--commit', action='store_true', help='نفّذ فعلاً (من غيرها تجربة بس)')

    def handle(self, *args, **opts):
        domain = opts['domain'].strip().lstrip('@').lower()
        if '.' not in domain:
            raise CommandError(f'الدومين «{domain}» ناقص الامتداد (.com مثلاً)')
        role = Role.objects.filter(name=opts['role']).first()
        if role is None:
            raise CommandError(f'مفيش دور اسمه «{opts["role"]}». الموجود: '
                               + '، '.join(Role.objects.values_list('name', flat=True)))
        manual = self.parse_map(opts['map'])
        rows = read_rows(opts['file'])
        branches = list(Branch.objects.all())

        # ---------------------------------------------------- مطابقة الفروع
        sheet_branches = Counter(r['branch'] for r in rows if r['branch'])
        branch_for, unmatched = {}, []
        self.stdout.write(self.style.MIGRATE_HEADING('الفروع:'))
        for name, count in sheet_branches.most_common():
            branch = manual.get(normalize(name)) or match_branch(name, branches)
            branch_for[name] = branch
            if branch:
                self.stdout.write(f'  {name} ({count})  ->  {branch.code}-{branch.name}')
            else:
                unmatched.append(name)
                self.stdout.write(self.style.ERROR(f'  {name} ({count})  ->  مش معروف'))
        if unmatched:
            self.stdout.write('\nالفروع اللي في البرنامج:')
            for b in sorted(branches, key=lambda b: b.code):
                self.stdout.write(f'  {b.code}  {b.name}')
            raise CommandError('في فروع مش معروفة. زوّد لكل واحد: --map "اسمه في الشيت=كود الفرع"')

        # ---------------------------------------------------- الموظفين
        existing = {e.lower() for e in Person.objects.values_list('email', flat=True)}
        by_local = defaultdict(list)
        for e in existing:
            by_local[e.split('@')[0]].append(e)

        created, report, seen = 0, defaultdict(list), set()
        with transaction.atomic():
            for r in rows:
                username = r['username'].strip().lower()
                if '@' in username:
                    username = username.split('@')[0]
                label = f'سطر {r["line"]}: {r["name"]} ({r["username"]})'
                if not USERNAME_RE.match(username):
                    report['اسم مستخدم مش صالح (اتساب)'].append(label)
                    continue
                email = f'{username}@{domain}'
                if email in seen:
                    report['مكرر في الشيت (اتساب)'].append(label)
                    continue
                seen.add(email)
                if email in existing:
                    report['موجود قبل كده (ماتغيرش)'].append(label)
                    continue
                others = by_local.get(username)
                if others and not opts['allow_other_domain']:
                    report['موجود بإيميل تاني (اتساب)'].append(f'{label} -> {", ".join(others)}')
                    continue

                branch = branch_for.get(r['branch'])
                first, second, third, forth = split_name(r['name'] or username)
                person = Person.objects.create_user(
                    email=email, password=opts['password'], first_name=first, second_name=second,
                    third_name=third, forth_name=forth, branch=branch, is_active=True)
                if branch:
                    EmployeeRole.objects.get_or_create(person=person, role=role, branch=branch)
                else:
                    report['اتضاف من غير فرع (مالوش دور لحد ما تحدده)'].append(f'{label} -> {email}')
                created += 1

            for title, lines in report.items():
                self.stdout.write(self.style.WARNING(f'\n{title}: {len(lines)}'))
                for line in lines:
                    self.stdout.write(f'  {line}')
            self.stdout.write(self.style.SUCCESS(f'\nهيتضاف: {created}  (الإيميل: اسم المستخدم@{domain}، '
                                                 f'كلمة المرور: {opts["password"]}، الدور: {role.name})'))
            if not opts['commit']:
                transaction.set_rollback(True)
                self.stdout.write(self.style.WARNING('دي كانت تجربة: مفيش حاجة اتغيرت. لو تمام زوّد --commit'))
            else:
                self.stdout.write(self.style.SUCCESS('تم.'))

    def parse_map(self, items):
        result = {}
        for item in items:
            name, _, code = item.rpartition('=')
            branch = Branch.objects.filter(code=code.strip()).first() if code.strip().isdigit() else None
            if not name.strip() or branch is None:
                raise CommandError(f'--map غلط: {item}  (لازم: "اسم الفرع في الشيت=كود موجود")')
            result[normalize(name)] = branch
        return result
