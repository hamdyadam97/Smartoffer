"""دمج الفروع المتقسمة رجال ونساء في فرع واحد.

«الفاو الرياض (رجال)» + «الفاو الرياض (نساء)»  ->  «الفاو الرياض»
كل حاجة متربطة بفرع النساء (طلاب، عروض، مشاهد، موظفين وأدوارهم، تخصصات، بنوك، تقارير...) بتتنقل لفرع الرجال،
وبعدين فرع النساء بيتمسح والاسم بيتشال منه «(رجال)». التخصصات اللي بقت متكررة في نفس الفرع بتتدمج.

من غير --commit بيعمل تجربة كاملة ويرجع في كل حاجة.
  python manage.py merge_branches              # كل الأزواج أوتوماتيك (تجربة)
  python manage.py merge_branches --commit
  python manage.py merge_branches --pair 9,10  # فرع 10 يتدمج في 9 بس
"""
import re
from collections import defaultdict

from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError, transaction

from core.models import Branch
from courses.models import Course

TAGS = {'male': ['(رجال)', 'رجال', '(بنين)', 'بنين'], 'female': ['(نساء)', 'نساء', '(بنات)', 'بنات']}


class DryRun(Exception):
    pass


def split_name(name):
    """('الفاو الرياض', 'male'|'female'|None)"""
    for gender, tags in TAGS.items():
        for tag in tags:
            if tag in name:
                return re.sub(r'\s+', ' ', name.replace(tag, ' ')).strip(' -'), gender
    return name.strip(), None


def reverse_relations(model):
    return [f for f in model._meta.get_fields()
            if f.is_relation and f.auto_created and not f.concrete and (f.one_to_many or f.one_to_one)]


class Command(BaseCommand):
    help = 'دمج فروع الرجال والنساء في فرع واحد'

    def add_arguments(self, parser):
        parser.add_argument('--pair', action='append', default=[], metavar='KEEP_CODE,MERGE_CODE',
                            help='الفرع التاني يتدمج في الأول (ممكن تتكرر). من غيرها: كل الأزواج أوتوماتيك')
        parser.add_argument('--keep-names', action='store_true', help='ماتشيلش «(رجال)» من اسم الفرع')
        parser.add_argument('--commit', action='store_true', help='نفّذ فعلاً (من غيرها تجربة بس)')

    def handle(self, *args, **opts):
        pairs = self.manual_pairs(opts['pair']) if opts['pair'] else self.auto_pairs()
        if not pairs:
            self.stdout.write('مفيش فروع متقسمة رجال ونساء.')
            return
        try:
            with transaction.atomic():
                for keep, merge in pairs:
                    self.merge(keep, merge, rename=not opts['keep_names'])
                if not opts['commit']:
                    raise DryRun
        except DryRun:
            self.stdout.write(self.style.WARNING(
                '\nدي كانت تجربة: مفيش أي حاجة اتغيرت. لو النتيجة تمام شغّل نفس الأمر وزوّد --commit'))
        else:
            self.stdout.write(self.style.SUCCESS('\nتم الدمج.'))

    # ------------------------------------------------------------------ pairs
    def manual_pairs(self, items):
        pairs = []
        for item in items:
            try:
                keep_code, merge_code = (int(x) for x in item.split(','))
            except ValueError:
                raise CommandError(f'--pair لازم يبقى كده: 9,10 . اللي اتكتب: {item}')
            keep, merge = Branch.objects.filter(code=keep_code).first(), Branch.objects.filter(code=merge_code).first()
            if not keep or not merge or keep == merge:
                raise CommandError(f'كود فرع مش موجود أو مكرر في --pair {item}')
            pairs.append((keep, merge))
        return pairs

    def auto_pairs(self):
        groups = defaultdict(dict)
        for branch in Branch.objects.order_by('code'):
            base, gender = split_name(branch.name)
            if gender:
                groups[base].setdefault(gender, []).append(branch)
        pairs, singles = [], []
        for base, by_gender in groups.items():
            men, women = by_gender.get('male', []), by_gender.get('female', [])
            if len(men) == 1 and len(women) == 1:
                pairs.append((men[0], women[0]))
            elif len(men) + len(women) == 1:
                singles.append((men + women)[0])
            else:
                self.stdout.write(self.style.WARNING(
                    f'«{base}»: مش واضح ({", ".join(f"{b.code}-{b.name}" for b in men + women)}) -> استخدم --pair'))
        # فرع عليه «(رجال)» أو «(نساء)» من غير التاني: بنشيل الكلمة من الاسم بس
        for branch in singles:
            pairs.append((branch, None))
        return pairs

    # ------------------------------------------------------------------ merge
    def merge(self, keep, merge, rename=True):
        base, _ = split_name(keep.name)
        title = f'{keep.code}-{keep.name}' + (f'  <-  {merge.code}-{merge.name}' if merge else '')
        self.stdout.write(self.style.MIGRATE_HEADING(f'\n{title}'))
        if merge:
            moved = self.move_relations(merge, keep)
            for line in moved:
                self.stdout.write(f'  {line}')
            self.fill_empty_fields(keep, merge)
            merge.delete()
        if rename and keep.name != base:
            keep.name = base
            self.stdout.write(f'  الاسم الجديد: {base}')
        keep.save()
        merged_courses = self.merge_duplicate_courses(keep)
        if merged_courses:
            self.stdout.write(f'  تخصصات متكررة اتدمجت: {merged_courses}')

    def move_relations(self, source, target):
        lines = []
        for rel in reverse_relations(Branch):
            model, field = rel.related_model, rel.field.name
            rows = list(model.objects.filter(**{field: source}))
            if not rows:
                continue
            moved = dropped = 0
            for obj in rows:
                if rel.one_to_one and model.objects.filter(**{field: target}).exists():
                    obj.delete()  # الفرع الأساسي عنده واحد بالفعل (مثلاً قالب المشهد)
                    dropped += 1
                    continue
                try:
                    with transaction.atomic():
                        model.objects.filter(pk=obj.pk).update(**{field: target})
                    moved += 1
                except IntegrityError:
                    obj.delete()  # موجود بالفعل على الفرع الأساسي (مثلاً نفس الدور لنفس الموظف)
                    dropped += 1
            label = model._meta.verbose_name_plural
            lines.append(f'{label}: {moved} اتنقلوا' + (f'، {dropped} مكررين اتشالوا' if dropped else ''))
        return lines

    def fill_empty_fields(self, target, source):
        for f in Branch._meta.concrete_fields:
            if f.name in ('id', 'slug', 'code', 'name', 'company', 'created_at', 'updated_at'):
                continue
            if not getattr(target, f.attname) and getattr(source, f.attname):
                setattr(target, f.attname, getattr(source, f.attname))

    def merge_duplicate_courses(self, branch):
        groups = defaultdict(list)
        for course in Course.objects.filter(branch=branch).order_by('code', 'pk'):
            groups[(course.program_type, course.name.strip().lower())].append(course)
        merged = 0
        for courses in groups.values():
            keep, *duplicates = courses
            for dup in duplicates:
                for rel in reverse_relations(Course):
                    try:
                        with transaction.atomic():
                            rel.related_model.objects.filter(**{rel.field.name: dup}).update(**{rel.field.name: keep})
                    except IntegrityError:
                        rel.related_model.objects.filter(**{rel.field.name: dup}).delete()
                dup.delete()
                merged += 1
        return merged
