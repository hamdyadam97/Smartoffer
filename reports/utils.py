from django.db.models import Count, Sum, Q
from django.utils import timezone

from core.models import Branch
from students.models import Student
from registrations.models import Account
from finance.models import Payment, Offer
from accounts.models import Person


def generate_report_data(report_type, branch=None, start_date=None, end_date=None):
    """Generate report data based on type and filters."""
    data = {}

    # Build date filters
    date_filter = Q()
    if start_date and end_date:
        date_filter = Q(created_at__date__gte=start_date, created_at__date__lte=end_date)
    elif start_date:
        date_filter = Q(created_at__date__gte=start_date)
    elif end_date:
        date_filter = Q(created_at__date__lte=end_date)

    if report_type == 'summary':
        students_qs = Student.objects.filter(date_filter) if start_date or end_date else Student.objects.all()
        accounts_qs = Account.objects.filter(date_filter) if start_date or end_date else Account.objects.all()
        payments_qs = Payment.objects.filter(date_filter) if start_date or end_date else Payment.objects.all()
        offers_qs = Offer.objects.filter(date_filter) if start_date or end_date else Offer.objects.all()
        persons_qs = Person.objects.filter(date_filter) if start_date or end_date else Person.objects.all()

        if branch:
            accounts_qs = accounts_qs.filter(course__master__branch=branch)
            payments_qs = payments_qs.filter(account__course__master__branch=branch)
            offers_qs = offers_qs.filter(master__branch=branch)

        data['إجمالي الطلاب'] = students_qs.count()
        data['إجمالي التسجيلات'] = accounts_qs.count()
        data['إجمالي المدفوعات'] = payments_qs.count()
        data['إجمالي العروض'] = offers_qs.count()
        data['إجمالي الموظفين'] = persons_qs.count()

        total_paid = payments_qs.aggregate(total=Sum('amount_number'))['total'] or 0
        data['إجمالي المبالغ المحصلة'] = float(total_paid)

    elif report_type == 'students':
        qs = Student.objects.filter(date_filter) if start_date or end_date else Student.objects.all()
        if branch:
            qs = qs.filter(accounts__course__master__branch=branch).distinct()

        by_level = list(qs.values('level').annotate(count=Count('id')).order_by('level'))
        data['الطلاب حسب المستوى'] = [{item['level']: item['count']} for item in by_level]
        data['إجمالي الطلاب'] = qs.count()

    elif report_type == 'offers':
        qs = Offer.objects.filter(date_filter) if start_date or end_date else Offer.objects.all()
        if branch:
            qs = qs.filter(master__branch=branch)

        data['إجمالي العروض'] = qs.count()
        data['العروض المسجلة'] = qs.filter(registered=True).count()
        data['العروض غير المسجلة'] = qs.filter(registered=False).count()

    elif report_type == 'branches':
        branches = Branch.objects.all()
        branches_data = []
        for b in branches:
            students_count = Student.objects.filter(
                accounts__course__master__branch=b
            ).distinct().count()
            registrations_count = Account.objects.filter(
                course__master__branch=b
            ).count()
            payments_total = Payment.objects.filter(
                account__course__master__branch=b
            ).aggregate(total=Sum('amount_number'))['total'] or 0
            branches_data.append({
                'الفرع': b.name,
                'الطلاب': students_count,
                'التسجيلات': registrations_count,
                'إجمالي المدفوعات': float(payments_total),
            })
        data['مقارنة الفروع'] = branches_data

    elif report_type == 'employees':
        qs = Person.objects.filter(date_filter) if start_date or end_date else Person.objects.all()
        data['إجمالي الموظفين'] = qs.count()

    return data
