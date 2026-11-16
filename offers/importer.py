"""استيراد عروض قديمة من ملف إكسل: كل صف = عرض + الشخص اللي اتبعتله."""
import re
from dataclasses import dataclass, field
from datetime import date, datetime, time
from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.utils import timezone

from courses.models import Course
from students.models import Contact, Student
from .models import OfferRecipient, StudentOffer

# عنوان العمود في الملف -> المفتاح. العمود اللي عليه * إجباري.
COLUMNS = [
    ('الاسم *', 'name'),
    ('الجوال *', 'phone'),
    ('الإيميل', 'email'),
    ('الفرع', 'branch'),
    ('التخصص', 'course'),
    ('السعر', 'price'),
    ('وصف السعر', 'price_description'),
    ('تاريخ العرض', 'date'),
    ('الحالة', 'status'),
    ('القناة', 'channel'),
    ('البيان / وصف العرض', 'content'),
]
EXAMPLE_ROW = ['محمد أحمد علي', '966501234567', '', '', 'دبلوم موارد بشرية', 3500, 'خصم 10%', '2025-03-15', 'مرسلة', 'واتساب', '']

STATUS_VALUES = {label: value for value, label in StudentOffer.STATUS_CHOICES} | {v: v for v, _ in StudentOffer.STATUS_CHOICES}
CHANNEL_VALUES = {label: value for value, label in OfferRecipient.CHANNEL_CHOICES} | {
    v: v for v, _ in OfferRecipient.CHANNEL_CHOICES} | {'واتس': 'whatsapp', 'ايميل': 'email', 'إيميل': 'email', 'بريد': 'email'}


@dataclass
class ImportResult:
    errors: list = field(default_factory=list)
    offers: int = 0
    linked_students: int = 0
    new_students: int = 0
    unknown_courses: set = field(default_factory=set)


def build_template():
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.title = 'العروض'
    ws.sheet_view.rightToLeft = True
    ws.append([title for title, _ in COLUMNS])
    ws.append(EXAMPLE_ROW)
    for i, (title, _) in enumerate(COLUMNS, start=1):
        ws.column_dimensions[ws.cell(row=1, column=i).column_letter].width = max(14, len(title) + 6)
    return wb


def _digits(value):
    return re.sub(r'\D', '', str(value or ''))


def _same_phone(a, b):
    a, b = _digits(a), _digits(b)
    if not a or not b:
        return False
    # 0501234567 و 966501234567 نفس الرقم: بنقارن آخر 9 أرقام
    return a[-9:] == b[-9:]


def _parse_date(value):
    if value in (None, ''):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d', '%m/%d/%Y'):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    raise ValueError(f'تاريخ مش مفهوم: «{text}» (اكتبه كده 2025-03-15)')


def _parse_price(value):
    if value in (None, ''):
        return Decimal('0')
    try:
        return Decimal(str(value).replace(',', '').strip())
    except InvalidOperation:
        raise ValueError(f'السعر لازم يبقى رقم: «{value}»')


def _find_branch(value, branches, default_branch):
    if value in (None, ''):
        return default_branch
    text = str(value).strip()
    for b in branches:
        if text == b.name or text == str(b.code):
            return b
    return None


def _find_course(text, branch):
    program_type, name = Course.split_type_prefix(text)
    courses = Course.objects.filter(name__iexact=name)
    if program_type:
        courses = courses.filter(program_type=program_type)
    # تخصص الفرع الأول، وبعدين اللي لكل الفروع
    return courses.filter(branch=branch).first() or courses.filter(branch__isnull=True).first()


def _find_student(phone, branch):
    for student in Student.objects.select_related('contact').filter(branch=branch).exclude(contact__mobile=''):
        if _same_phone(student.contact.mobile, phone):
            return student
    return None


def _create_student(name, phone, branch):
    parts = name.split()
    contact = Contact.objects.create(
        first_name=parts[0],
        second_name=parts[1] if len(parts) > 2 else '',
        third_name=' '.join(parts[2:-1]) if len(parts) > 3 else '',
        forth_name=parts[-1] if len(parts) > 1 else '',
        mobile=_digits(phone),
    )
    return Student.objects.create(contact=contact, branch=branch)


def read_rows(uploaded_file):
    """يرجّع [(رقم الصف, dict)] من أول شيت، والعناوين في أول صف."""
    from openpyxl import load_workbook
    try:
        wb = load_workbook(uploaded_file, read_only=True, data_only=True)
    except Exception:
        raise ValueError('الملف مش ملف إكسل صالح (.xlsx).')
    ws = wb.worksheets[0]
    rows = ws.iter_rows(values_only=True)
    header = next(rows, None) or []
    by_title = {re.sub(r'[\s*]', '', title): key for title, key in COLUMNS}
    keys = [by_title.get(re.sub(r'[\s*]', '', str(h or ''))) for h in header]
    if 'name' not in keys or 'phone' not in keys:
        raise ValueError('أول صف في الملف لازم يبقى عناوين الأعمدة زي القالب (على الأقل «الاسم» و«الجوال»).')
    result = []
    for number, values in enumerate(rows, start=2):
        if not any(v not in (None, '') for v in values):
            continue
        result.append((number, {k: v for k, v in zip(keys, values) if k}))
    return result


def import_offers(uploaded_file, user, default_branch, allowed_branches, register_students=False):
    """بيستورد كل الصفوف أو مفيش ولا صف (لو فيه أي غلط بيرجع الأغلاط من غير ما يسجل حاجة)."""
    result = ImportResult()
    try:
        rows = read_rows(uploaded_file)
    except ValueError as exc:
        result.errors.append(str(exc))
        return result
    if not rows:
        result.errors.append('الملف فاضي: مفيش صفوف تحت العناوين.')
        return result

    prepared = []
    for number, row in rows:
        try:
            name = str(row.get('name') or '').strip()
            phone = _digits(row.get('phone'))
            if not name:
                raise ValueError('الاسم فاضي')
            if not phone:
                raise ValueError('الجوال فاضي')
            branch = _find_branch(row.get('branch'), allowed_branches, default_branch)
            if branch is None:
                raise ValueError(f'الفرع «{row.get("branch")}» مش موجود أو مش مسموح لك' if row.get('branch') else 'اختار فرع افتراضي أو اكتب الفرع في الصف')
            status_text = str(row.get('status') or '').strip()
            status = STATUS_VALUES.get(status_text or 'مرسلة')
            if status is None:
                raise ValueError(f'الحالة «{status_text}» مش معروفة (مسودة / مجدولة / مرسلة / منتهية)')
            channel_text = str(row.get('channel') or '').strip()
            channel = CHANNEL_VALUES.get(channel_text or 'whatsapp')
            if channel is None:
                raise ValueError(f'القناة «{channel_text}» مش معروفة (واتساب / البريد الإلكتروني)')
            prepared.append({
                'name': name, 'phone': phone, 'email': str(row.get('email') or '').strip(),
                'branch': branch, 'course_text': str(row.get('course') or '').strip(),
                'price': _parse_price(row.get('price')),
                'price_description': str(row.get('price_description') or '').strip(),
                'date': _parse_date(row.get('date')), 'status': status, 'channel': channel,
                'content': str(row.get('content') or '').strip(),
            })
        except ValueError as exc:
            result.errors.append(f'صف {number}: {exc}')
    if result.errors:
        return result

    with transaction.atomic():
        for item in prepared:
            course = _find_course(item['course_text'], item['branch']) if item['course_text'] else None
            if item['course_text'] and course is None:
                result.unknown_courses.add(item['course_text'])
            title = course.get_display_name() if course else (item['course_text'] or 'عرض سعر')
            when = timezone.make_aware(datetime.combine(item['date'], time(12))) if item['date'] else timezone.now()

            student = _find_student(item['phone'], item['branch'])
            if student:
                result.linked_students += 1
            elif register_students:
                student = _create_student(item['name'], item['phone'], item['branch'])
                result.new_students += 1

            offer = StudentOffer.objects.create(
                title=title,
                content=item['content'] or item['branch'].offer_template or title,
                branch=item['branch'],
                course=course,
                price=item['price'],
                price_description=item['price_description'],
                status=item['status'],
                sent_at=when if item['status'] == 'مرسلة' else None,
                created_by=user,
            )
            recipient = OfferRecipient.objects.create(
                offer=offer, student=student, contact_name=item['name'], contact_phone=item['phone'],
                contact_email=item['email'], channel=item['channel'],
            )
            # العروض القديمة بتاخد تاريخها الحقيقي
            StudentOffer.objects.filter(pk=offer.pk).update(created_at=when)
            OfferRecipient.objects.filter(pk=recipient.pk).update(sent_at=when)
            result.offers += 1
    return result
