"""تقارير مباشرة (من غير ما تتخزن): الفروع، الموظفين، العروض، المشاهد، وحسب الشهر.
كل تقرير بيرجّع Table فيه العناوين والصفوف وصف الإجمالي، ونفس الجدول بيتعرض في الصفحة وبيطلع Excel."""
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, timedelta

from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from django.utils import timezone

from accounts.models import Person
from core.models import Branch
from offers.models import OfferRecipient, StudentOffer
from permits.models import Permit
from students.models import Student

REPORT_TYPES = [
    ('branches', 'الفروع'),
    ('employees', 'الموظفين'),
    ('offers', 'العروض (تفصيلي)'),
    ('permits', 'المشاهد (تفصيلي)'),
    ('monthly', 'حسب الشهر'),
]

PERIODS = [
    ('this_month', 'الشهر ده'),
    ('last_month', 'الشهر اللي فات'),
    ('last_30', 'آخر 30 يوم'),
    ('this_year', 'السنة دي'),
    ('all', 'كل الفترات'),
    ('custom', 'فترة محددة'),
]

SUBSCRIBED = 'اشترك'
MONTHS_AR = ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو', 'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر',
             'نوفمبر', 'ديسمبر']


@dataclass
class Table:
    title: str
    headers: list
    rows: list = field(default_factory=list)
    totals: list = None


def period_range(period, start=None, end=None):
    """(من، إلى) شاملين. None = من غير حد."""
    today = timezone.localdate()
    if period == 'this_month':
        return today.replace(day=1), today
    if period == 'last_month':
        last_day = today.replace(day=1) - timedelta(days=1)
        return last_day.replace(day=1), last_day
    if period == 'last_30':
        return today - timedelta(days=29), today
    if period == 'this_year':
        return today.replace(month=1, day=1), today
    if period == 'custom':
        return start, end
    return None, None


def _dates(field_name, start, end, is_datetime=True):
    """فلتر الفترة على حقل تاريخ (date) أو وقت (datetime)."""
    lookup = f'{field_name}__date' if is_datetime else field_name
    q = Q()
    if start:
        q &= Q(**{f'{lookup}__gte': start})
    if end:
        q &= Q(**{f'{lookup}__lte': end})
    return q


def _pct(part, whole):
    return f'{round(part * 100 / whole)}%' if whole else '-'


def _totals_row(rows, label, numeric_from=1):
    if not rows:
        return None
    totals = [label] + [''] * (len(rows[0]) - 1)
    for i in range(numeric_from, len(rows[0])):
        if all(isinstance(r[i], int) for r in rows):
            totals[i] = sum(r[i] for r in rows)
    return totals


# ---------------------------------------------------------------- التقارير

def branches_report(branches, start, end):
    offers = StudentOffer.objects.filter(branch__in=branches).filter(_dates('created_at', start, end))
    recipients = OfferRecipient.objects.filter(offer__in=offers)
    permits = Permit.objects.filter(branch__in=branches).filter(_dates('issue_date', start, end, False))
    students = Student.objects.filter(branch__in=branches).filter(_dates('created_at', start, end))

    def by_branch(qs, **extra):
        return dict(qs.values_list('branch').annotate(n=Count('pk', **extra)))

    offer_n = by_branch(offers)
    rec_n = dict(recipients.values_list('offer__branch').annotate(n=Count('pk')))
    sub_n = dict(recipients.filter(status=SUBSCRIBED).values_list('offer__branch').annotate(n=Count('pk')))
    permit_n = by_branch(permits)
    cancelled_n = by_branch(permits.filter(status=Permit.STATUS_CANCELLED))
    public_n = by_branch(permits.filter(issued_from_public=True))
    student_n = by_branch(students)

    table = Table('تقرير الفروع', ['الفرع', 'العروض', 'المستلمين', 'اشتركوا', 'نسبة الاشتراك',
                                    'المشاهد', 'ملغية', 'من البوابة', 'طلاب جدد'])
    for b in branches.order_by('code'):
        table.rows.append([
            b.name, offer_n.get(b.pk, 0), rec_n.get(b.pk, 0), sub_n.get(b.pk, 0),
            _pct(sub_n.get(b.pk, 0), rec_n.get(b.pk, 0)), permit_n.get(b.pk, 0),
            cancelled_n.get(b.pk, 0), public_n.get(b.pk, 0), student_n.get(b.pk, 0),
        ])
    table.totals = _totals_row(table.rows, 'الإجمالي')
    if table.totals:
        table.totals[4] = _pct(table.totals[3], table.totals[2])
    return table


def employees_report(branches, start, end):
    offers = StudentOffer.objects.filter(branch__in=branches).filter(_dates('created_at', start, end))
    recipients = OfferRecipient.objects.filter(offer__in=offers)
    permits = Permit.objects.filter(branch__in=branches).filter(_dates('issue_date', start, end, False))

    offer_n = dict(offers.values_list('created_by').annotate(n=Count('pk')))
    rec_n = dict(recipients.values_list('offer__created_by').annotate(n=Count('pk')))
    sub_n = dict(recipients.filter(status=SUBSCRIBED).values_list('offer__created_by').annotate(n=Count('pk')))
    issued_n = dict(permits.exclude(issued_by=None).values_list('issued_by').annotate(n=Count('pk')))
    referred_n = dict(permits.exclude(referral_employee=None).values_list('referral_employee').annotate(n=Count('pk')))

    people_ids = set(offer_n) | set(issued_n) | set(referred_n)
    people = Person.objects.filter(Q(pk__in=people_ids) | Q(branch__in=branches, is_active=True)).select_related('branch')

    table = Table('تقرير الموظفين', ['الموظف', 'الفرع', 'العروض', 'المستلمين', 'اشتركوا', 'نسبة الاشتراك',
                                     'مشاهد أصدرها', 'مشاهد من لينكه'])
    for p in people:
        row = [p.get_full_name() or p.email, p.branch.name if p.branch else '-', offer_n.get(p.pk, 0),
               rec_n.get(p.pk, 0), sub_n.get(p.pk, 0), _pct(sub_n.get(p.pk, 0), rec_n.get(p.pk, 0)),
               issued_n.get(p.pk, 0), referred_n.get(p.pk, 0)]
        table.rows.append(row)
    # الأكتر شغل الأول
    table.rows.sort(key=lambda r: (r[2] + r[6] + r[7], r[2]), reverse=True)
    table.totals = _totals_row(table.rows, 'الإجمالي', numeric_from=2)
    if table.totals:
        table.totals[5] = _pct(table.totals[4], table.totals[3])
    return table


def offers_report(branches, start, end):
    offers = (StudentOffer.objects.filter(branch__in=branches).filter(_dates('created_at', start, end))
              .select_related('branch', 'course', 'created_by').prefetch_related('recipients__student__contact')
              .order_by('-created_at'))
    table = Table('تقرير العروض', ['التاريخ', 'العرض', 'الفرع', 'التخصص', 'السعر', 'الحالة', 'المستلمين',
                                   'الجوال', 'حالة المستلم', 'أنشأه'])
    for o in offers:
        recipients = list(o.recipients.all())
        names = '، '.join(r.student.contact.get_full_name() if r.student else (r.contact_name or '-') for r in recipients)
        phones = '، '.join((r.student.contact.mobile if r.student else r.contact_phone) or '-' for r in recipients)
        statuses = '، '.join(sorted({r.get_status_display() for r in recipients}))
        table.rows.append([
            timezone.localtime(o.created_at).date(), o.title, o.branch.name,
            o.course.get_display_name() if o.course else '-', float(o.price), o.get_status_display(),
            names or '-', phones or '-', statuses or '-',
            (o.created_by.get_full_name() or o.created_by.email) if o.created_by else '-',
        ])
    return table


def permits_report(branches, start, end):
    permits = (Permit.objects.filter(branch__in=branches).filter(_dates('issue_date', start, end, False))
               .select_related('student__contact', 'branch', 'issued_by', 'referral_employee').order_by('-issue_date', '-pk'))
    table = Table('تقرير المشاهد', ['رقم المشهد', 'تاريخ الإصدار', 'صالح حتى', 'الطالب', 'رقم الهوية', 'الجوال',
                                    'البرنامج', 'الفرع', 'الحالة', 'أصدره', 'عن طريق لينك'])
    for p in permits:
        c = p.student.contact
        issuer = p.issued_by.get_full_name() if p.issued_by else ('البوابة العامة' if p.issued_from_public else '-')
        table.rows.append([
            p.number, p.issue_date, p.expiry_date, c.get_full_name(), c.identity_number or '-', c.mobile or '-',
            p.program_name or '-', p.branch.name, p.get_effective_status_display(), issuer,
            p.referral_employee.get_full_name() if p.referral_employee else '-',
        ])
    return table


def monthly_report(branches, start, end):
    offers = StudentOffer.objects.filter(branch__in=branches).filter(_dates('created_at', start, end))
    recipients = OfferRecipient.objects.filter(offer__in=offers)
    permits = Permit.objects.filter(branch__in=branches).filter(_dates('issue_date', start, end, False))

    data = defaultdict(lambda: [0, 0, 0, 0])

    def add(qs, date_field, index):
        for month, n in qs.annotate(m=TruncMonth(date_field)).values_list('m').annotate(n=Count('pk')):
            if month:
                data[(month.year, month.month)][index] += n

    add(offers, 'created_at', 0)
    add(recipients, 'offer__created_at', 1)
    add(recipients.filter(status=SUBSCRIBED), 'offer__created_at', 2)
    add(permits, 'issue_date', 3)

    table = Table('تقرير حسب الشهر', ['الشهر', 'العروض', 'المستلمين', 'اشتركوا', 'نسبة الاشتراك', 'المشاهد'])
    for (year, month) in sorted(data, reverse=True):
        o, r, s, p = data[(year, month)]
        table.rows.append([f'{MONTHS_AR[month - 1]} {year}', o, r, s, _pct(s, r), p])
    table.totals = _totals_row(table.rows, 'الإجمالي')
    if table.totals:
        table.totals[4] = _pct(table.totals[3], table.totals[2])
    return table


BUILDERS = {
    'branches': branches_report, 'employees': employees_report, 'offers': offers_report,
    'permits': permits_report, 'monthly': monthly_report,
}


def build(report_type, branches, start, end):
    return BUILDERS.get(report_type, branches_report)(branches, start, end)


def to_excel(table, subtitle_lines):
    """الجدول -> ملف xlsx (بيرجّع Workbook)."""
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    ws = wb.active
    ws.title = table.title[:31]
    ws.sheet_view.rightToLeft = True
    cols = len(table.headers)
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=cols)
    ws.cell(row=1, column=1, value=table.title).font = Font(size=14, bold=True, color='FFFFFF')
    ws.cell(row=1, column=1).fill = PatternFill('solid', start_color='1E3A8A')
    ws.cell(row=1, column=1).alignment = Alignment(horizontal='center')
    row = 2
    for line in subtitle_lines:
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=cols)
        ws.cell(row=row, column=1, value=line).font = Font(color='475569')
        row += 1
    row += 1

    border = Border(*(Side(style='thin', color='CBD5E1'),) * 4)
    header_row = row
    for i, h in enumerate(table.headers, 1):
        c = ws.cell(row=row, column=i, value=h)
        c.font = Font(bold=True)
        c.fill = PatternFill('solid', start_color='E2E8F0')
        c.border = border
        c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    for values in table.rows:
        row += 1
        for i, v in enumerate(values, 1):
            c = ws.cell(row=row, column=i, value=v)
            c.border = border
            if isinstance(v, date):
                c.number_format = 'yyyy-mm-dd'
    if table.totals:
        row += 1
        for i, v in enumerate(table.totals, 1):
            c = ws.cell(row=row, column=i, value=v)
            c.font = Font(bold=True)
            c.fill = PatternFill('solid', start_color='F1F5F9')
            c.border = border
    ws.freeze_panes = ws.cell(row=header_row + 1, column=1)
    if table.rows:
        ws.auto_filter.ref = f'A{header_row}:{get_column_letter(cols)}{header_row + len(table.rows)}'
    for i, h in enumerate(table.headers, 1):
        longest = max([len(str(h))] + [len(str(r[i - 1])) for r in table.rows[:500]])
        ws.column_dimensions[get_column_letter(i)].width = min(max(12, longest + 2), 60)
    return wb
