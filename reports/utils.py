from django.db.models import Count, Q

from accounts.mixins import filter_by_branch
from core.models import Branch
from students.models import Student
from registrations.models import Account
from offers.models import StudentOffer
from accounts.models import Person


def generate_report_data(report_type, user=None, branch=None, start_date=None, end_date=None):
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
        students_qs = filter_by_branch(Student.objects.filter(date_filter), user, 'branch', 'view_student')
        accounts_qs = filter_by_branch(Account.objects.filter(date_filter), user, 'student__branch', 'view_account')
        offers_qs = filter_by_branch(StudentOffer.objects.filter(date_filter), user, 'branch', 'view_studentoffer')
        persons_qs = filter_by_branch(Person.objects.filter(date_filter), user, 'branch', 'view_person')

        if branch:
            students_qs = students_qs.filter(branch=branch)
            accounts_qs = accounts_qs.filter(student__branch=branch)
            offers_qs = offers_qs.filter(branch=branch)
            persons_qs = persons_qs.filter(branch=branch)

        data['إجمالي الطلاب'] = students_qs.count()
        data['إجمالي التسجيلات'] = accounts_qs.count()
        data['إجمالي العروض'] = offers_qs.count()
        data['العروض المرسلة'] = offers_qs.filter(status='مرسلة').count()
        data['إجمالي الموظفين'] = persons_qs.count()

    elif report_type == 'students':
        qs = filter_by_branch(Student.objects.filter(date_filter), user, 'branch', 'view_student')
        if branch:
            qs = qs.filter(branch=branch)

        by_level = list(qs.values('level').annotate(count=Count('id')).order_by('level'))
        data['الطلاب حسب المستوى'] = [{item['level']: item['count']} for item in by_level]
        data['إجمالي الطلاب'] = qs.count()

    elif report_type == 'offers':
        qs = filter_by_branch(
            StudentOffer.objects.filter(date_filter).select_related('branch', 'course', 'created_by'),
            user, 'branch', 'view_studentoffer'
        )
        if branch:
            qs = qs.filter(branch=branch)

        offers_data = []
        for offer in qs:
            offers_data.append({
                'العنوان': offer.title,
                'التخصص': offer.course.get_display_name() if offer.course else '-',
                'الفرع': offer.branch.name,
                'السعر': float(offer.price),
                'الحالة': offer.get_status_display(),
                'المستلمين': offer.recipients.count(),
                'بواسطة': offer.created_by.get_short_name(),
                'التاريخ': offer.created_at.strftime('%Y-%m-%d'),
            })
        data['العروض'] = offers_data
        data['إجمالي العروض'] = qs.count()
        data['العروض المرسلة'] = qs.filter(status='مرسلة').count()

    elif report_type == 'branches':
        branches = Branch.objects.all()
        if user is not None and not user.is_executive():
            allowed_ids = [b.pk for b in user.get_branches_for_perm('view_branch')]
            branches = branches.filter(pk__in=allowed_ids)
        branches_data = []
        for b in branches:
            branches_data.append({
                'الفرع': b.name,
                'الطلاب': filter_by_branch(Student.objects.filter(branch=b), user, 'branch', 'view_student').count(),
                'التسجيلات': filter_by_branch(
                    Account.objects.filter(student__branch=b), user, 'student__branch', 'view_account'
                ).count(),
                'العروض': filter_by_branch(
                    StudentOffer.objects.filter(branch=b), user, 'branch', 'view_studentoffer'
                ).count(),
            })
        data['مقارنة الفروع'] = branches_data

    elif report_type == 'employees':
        qs = filter_by_branch(Person.objects.filter(date_filter), user, 'branch', 'view_person')
        data['إجمالي الموظفين'] = qs.count()

    return data


def get_dashboard_data(user=None, branch=None):
    """Get comprehensive dashboard data scoped by user permissions."""
    data = {}

    student_qs = filter_by_branch(Student.objects.all(), user, 'branch', 'view_student')
    account_qs = filter_by_branch(Account.objects.all(), user, 'student__branch', 'view_account')
    offer_qs = filter_by_branch(StudentOffer.objects.all(), user, 'branch', 'view_studentoffer')
    person_qs = filter_by_branch(Person.objects.all(), user, 'branch', 'view_person')

    if branch:
        student_qs = student_qs.filter(branch=branch)
        account_qs = account_qs.filter(student__branch=branch)
        offer_qs = offer_qs.filter(branch=branch)
        person_qs = person_qs.filter(branch=branch)

    # KPIs
    data['students_total'] = student_qs.count()
    data['registrations_total'] = account_qs.count()
    data['offers_total'] = offer_qs.count()
    data['offers_sent'] = offer_qs.filter(status='مرسلة').count()
    data['employees_total'] = person_qs.count()

    # Breakdowns
    data['students_by_level'] = list(student_qs.values('level').annotate(count=Count('id')))
    data['registrations_by_payment_type'] = list(account_qs.values('course_payment_type').annotate(count=Count('id')))
    data['offers_by_status'] = list(offer_qs.values('status').annotate(count=Count('id')))

    # Branch comparison
    branches = Branch.objects.all()
    if user is not None and not user.is_executive():
        allowed_ids = [b.pk for b in user.get_branches_for_perm('view_branch')]
        branches = branches.filter(pk__in=allowed_ids)

    data['branches_comparison'] = [
        {
            'name': b.name,
            'students': student_qs.filter(branch=b).count(),
            'registrations': account_qs.filter(student__branch=b).count(),
            'offers': offer_qs.filter(branch=b).count(),
        }
        for b in branches
    ]
    return data
