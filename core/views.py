from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.db.models import Count, Q
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from accounts.mixins import BranchPermissionMixin, filter_by_branch
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator

from accounts.models import Person
from students.models import Student
from courses.models import Course
from registrations.models import Account
from offers.models import StudentOffer
from core.models import Branch, Company, Bank  # Bank: الصفحة اتشالت، بس بيتمسح مع الفرع
from .forms import CompanyForm, BranchForm


def custom_page_not_found_view(request, exception):
    return render(request, '404.html', status=404)


def custom_permission_denied_view(request, exception=None):
    return render(request, '403.html', status=403)


def _check_perm(user, perm):
    """Raise PermissionDenied if the user does not have a permission on any branch."""
    if user.is_executive():
        return
    if not user.get_branches_for_perm(perm):
        raise PermissionDenied('غير مسموح لك دخول هنا')


def _check_branch_perm(user, perm, branch=None):
    """Raise PermissionDenied if the user lacks the permission (optionally on a branch)."""
    if user.is_executive():
        return
    allowed_ids = {b.pk for b in user.get_branches_for_perm(perm)}
    if not allowed_ids:
        raise PermissionDenied('غير مسموح لك دخول هنا')
    if branch is not None and branch.pk not in allowed_ids:
        raise PermissionDenied('غير مسموح لك دخول هنا')


def _dashboard_charts(request, student_qs, account_qs, studentoffer_qs):
    """الرسوم البيانية وآخر النشاطات المشتركة بين لوحة التحكم ولوحة الفرع."""
    # عروض الطلاب الشهرية (آخر 6 أشهر)
    six_months_ago = timezone.now() - timezone.timedelta(days=180)
    monthly_offers = studentoffer_qs.filter(
        created_at__gte=six_months_ago
    ).annotate(month=TruncMonth('created_at')).values('month').annotate(
        total=Count('id')
    ).order_by('month')

    # حالة العروض
    offer_statuses = studentoffer_qs.values('status').annotate(count=Count('id')).order_by('-count')

    # أنواع الدفع في التسجيلات
    payment_types = account_qs.values('course_payment_type').annotate(count=Count('id')).order_by('-count')

    activities = []
    for s in student_qs.select_related('contact').order_by('-created_at')[:50]:
        activities.append({
            'title': f'طالب جديد: {s.get_full_name()}',
            'desc': s.contact.mobile or '',
            'time': s.created_at,
            'css_class': 'success',
        })
    for r in account_qs.select_related('student', 'course').order_by('-created_at')[:50]:
        activities.append({
            'title': f'تسجيل جديد: {r.student.get_full_name()}',
            'desc': r.course.get_display_name(),
            'time': r.created_at,
            'css_class': 'purple',
        })
    for o in studentoffer_qs.select_related('branch').order_by('-created_at')[:50]:
        activities.append({
            'title': f'عرض: {o.title}',
            'desc': o.branch.name,
            'time': o.created_at,
            'css_class': 'info',
        })
    activities.sort(key=lambda x: x['time'], reverse=True)

    return {
        'months_labels': [m['month'].strftime('%Y-%m') for m in monthly_offers],
        'months_data': [m['total'] for m in monthly_offers],
        'offer_status_labels': [o['status'] for o in offer_statuses],
        'offer_status_data': [o['count'] for o in offer_statuses],
        'payment_type_labels': [p['course_payment_type'] for p in payment_types],
        'payment_type_data': [p['count'] for p in payment_types],
        'recent_activities': Paginator(activities, 10).get_page(request.GET.get('activity_page', 1)),
        'recent_student_offers': studentoffer_qs.select_related('branch', 'course').order_by('-created_at')[:6],
    }


MANAGER_PERM = 'view_branch_dashboard'


class DashboardScope:
    """مين يشوف إيه في لوحة التحكم:
    - مدير النظام: كل حاجة.
    - المدير (صلاحية «متابعة كل بيانات الفرع»): كل بيانات الفروع اللي الصلاحية دي عليها في دوره،
      + شغله هو في أي فرع.
    - الموظف العادي: شغله هو بس (العروض اللي عملها، المشاهد اللي أصدرها أو جت من لينكه، وطلابهم)."""

    def __init__(self, user, branch=None):
        self.user = user
        self.is_all = user.is_executive()
        self.managed = Branch.objects.all() if self.is_all else Branch.objects.filter(
            pk__in=[b.pk for b in user.get_branches_for_perm(MANAGER_PERM)])
        self.is_manager = self.is_all or self.managed.exists()
        self.branch = branch

    def _limit(self, qs, branch_field, own_q):
        if not self.is_all:
            # بـ pk__in بدل distinct(): عشان العدّ والتجميع في الرسوم مايتكررش من الـ joins
            visible = qs.model.objects.filter(Q(**{f'{branch_field}__in': self.managed}) | own_q).values('pk')
            qs = qs.filter(pk__in=visible)
        if self.branch is not None:
            qs = qs.filter(**{branch_field: self.branch})
        return qs

    def offers(self):
        return self._limit(StudentOffer.objects.all(), 'branch', Q(created_by=self.user))

    def permits(self):
        from permits.models import Permit
        return self._limit(Permit.objects.all(), 'branch',
                           Q(issued_by=self.user) | Q(referral_employee=self.user))

    def students(self):
        return self._limit(Student.objects.all(), 'branch',
                           Q(offer_recipients__offer__created_by=self.user) | Q(permits__issued_by=self.user)
                           | Q(permits__referral_employee=self.user))

    def accounts(self):
        own_students = Student.objects.filter(
            Q(offer_recipients__offer__created_by=self.user) | Q(permits__issued_by=self.user)
            | Q(permits__referral_employee=self.user))
        return self._limit(Account.objects.all(), 'student__branch', Q(student__in=own_students))


def _permit_stats(permits_qs):
    from permits.models import Permit
    today = timezone.localdate()
    active = permits_qs.filter(status=Permit.STATUS_ACTIVE, expiry_date__gte=today)
    return {
        'permits_count': permits_qs.count(),
        'permits_active': active.count(),
        'permits_this_month': permits_qs.filter(issue_date__gte=today.replace(day=1)).count(),
        'permits_public': permits_qs.filter(issued_from_public=True).count(),
        'recent_permits': permits_qs.select_related('student__contact', 'branch').order_by('-created_at')[:6],
    }


@login_required
def dashboard(request):
    scope = DashboardScope(request.user)
    selected_branch = None
    if request.GET.get('branch'):
        selected_branch = get_object_or_404(Branch, pk=request.GET.get('branch'))
        if not scope.managed.filter(pk=selected_branch.pk).exists():
            raise PermissionDenied('غير مسموح لك دخول هنا')
        scope.branch = selected_branch

    student_qs, account_qs = scope.students(), scope.accounts()
    studentoffer_qs, permits_qs = scope.offers(), scope.permits()
    course_qs = filter_by_branch(Course.objects.all(), request.user, 'branch', 'view_course', include_shared=True)
    if selected_branch:
        course_qs = course_qs.filter(Q(branch=selected_branch) | Q(branch__isnull=True))

    # تفاصيل الفروع للمديرين بس (الموظف العادي بيشوف شغله هو)
    branches = scope.managed.select_related('company') if scope.is_manager else Branch.objects.none()
    branch_stats = []
    for branch in branches:
        branch_stats.append({
            'branch': branch,
            'registrations': account_qs.filter(student__branch=branch).count(),
            'courses': course_qs.filter(branch=branch).count(),
            'student_offers': studentoffer_qs.filter(branch=branch).count(),
            'permits': permits_qs.filter(branch=branch).count(),
        })

    context = {
        'is_manager_view': scope.is_manager,
        'students_count': student_qs.count(),
        'courses_count': course_qs.count(),
        'registrations_count': account_qs.count(),
        'branches_count': branches.count(),
        'student_offers_count': studentoffer_qs.count(),
        'branch_stats': branch_stats,
        'regs_by_branch_labels': [bs['branch'].name for bs in branch_stats],
        'regs_by_branch': [bs['registrations'] for bs in branch_stats],
        'top_branches': sorted(branch_stats, key=lambda x: x['registrations'], reverse=True)[:5],
        'selected_branch': selected_branch,
        'all_branches': branches,
        **_permit_stats(permits_qs),
        **_dashboard_charts(request, student_qs, account_qs, studentoffer_qs),
    }
    return render(request, 'core/dashboard.html', context)


@login_required
def branch_dashboard(request, slug):
    """لوحة تحكم مفصلة لفرع معين: لمدير الفرع (أو مدير النظام) بس."""
    branch = get_object_or_404(Branch, slug=slug)
    scope = DashboardScope(request.user, branch)
    if not scope.managed.filter(pk=branch.pk).exists():
        raise PermissionDenied('غير مسموح لك دخول هنا')

    students_qs, registrations_qs = scope.students(), scope.accounts()
    studentoffers_qs, permits_qs = scope.offers(), scope.permits()
    courses_qs = Course.objects.filter(branch=branch)

    context = {
        'branch': branch,
        'students_count': students_qs.count(),
        'courses_count': courses_qs.count(),
        'registrations_count': registrations_qs.count(),
        'student_offers_count': studentoffers_qs.count(),
        **_permit_stats(permits_qs),
        **_dashboard_charts(request, students_qs, registrations_qs, studentoffers_qs),
    }
    return render(request, 'core/branch_dashboard.html', context)


# ============================================================
# Company Views
# ============================================================

class CompanyListView(BranchPermissionMixin, ListView):
    model = Company
    template_name = 'core/company_list.html'
    context_object_name = 'companies'
    paginate_by = 20
    required_perm = 'view_company'
    branch_field = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company_currency_choices'] = Company.CURRENCY_CHOICES
        return context


class CompanyDetailView(BranchPermissionMixin, DetailView):
    model = Company
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    template_name = 'core/company_detail.html'
    context_object_name = 'company'
    required_perm = 'view_company'
    branch_field = None


class CompanyCreateView(BranchPermissionMixin, CreateView):
    model = Company
    form_class = CompanyForm
    template_name = 'core/company_form.html'
    success_url = reverse_lazy('company-list')
    required_perm = 'add_company'

    def form_valid(self, form):
        messages.success(self.request, 'تم إنشاء الشركة بنجاح')
        return super().form_valid(form)


class CompanyUpdateView(BranchPermissionMixin, UpdateView):
    model = Company
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    form_class = CompanyForm
    template_name = 'core/company_form.html'
    success_url = reverse_lazy('company-list')
    required_perm = 'change_company'

    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث الشركة بنجاح')
        return super().form_valid(form)


class CompanyDeleteView(BranchPermissionMixin, DeleteView):
    model = Company
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    template_name = 'core/company_confirm_delete.html'
    success_url = reverse_lazy('company-list')
    required_perm = 'delete_company'

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'تم حذف الشركة بنجاح')
        return super().delete(request, *args, **kwargs)


# ============================================================
# Branch Views
# ============================================================

class BranchListView(BranchPermissionMixin, ListView):
    model = Branch
    template_name = 'core/branch_list.html'
    context_object_name = 'branches'
    paginate_by = 20
    required_perm = 'view_branch'
    branch_field = None

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = filter_by_branch(queryset, self.request.user, 'id', 'view_branch')
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        company = self.request.GET.get('company')
        if company:
            queryset = queryset.filter(company_id=company)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['companies'] = Company.objects.all()
        return context


class BranchDetailView(BranchPermissionMixin, DetailView):
    model = Branch
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    template_name = 'core/branch_detail.html'
    context_object_name = 'branch'
    required_perm = 'view_branch'
    branch_field = None


class BranchCreateView(BranchPermissionMixin, CreateView):
    model = Branch
    form_class = BranchForm
    template_name = 'core/branch_form.html'
    success_url = reverse_lazy('branch-list')
    required_perm = 'add_branch'

    def form_valid(self, form):
        messages.success(self.request, 'تم إنشاء الفرع بنجاح')
        return super().form_valid(form)


class BranchUpdateView(BranchPermissionMixin, UpdateView):
    model = Branch
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    form_class = BranchForm
    template_name = 'core/branch_form.html'
    success_url = reverse_lazy('branch-list')
    required_perm = 'change_branch'

    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث الفرع بنجاح')
        return super().form_valid(form)


def branch_related_data(branch, user):
    """كل البيانات المرتبطة بالفرع بترتيب الحذف الصحيح: [(الاسم, queryset), ...].

    الموظفين اللي فرعهم الرئيسي هو الفرع ده بيتمسحوا، ما عدا المستخدم الحالي ومديري النظام.
    """
    from offers.models import OfferRecipient
    from students.models import Contact
    return [
        ('تسجيل', Account.objects.filter(Q(course__branch=branch) | Q(student__branch=branch))),
        ('تخصص', Course.objects.filter(branch=branch)),
        ('مستلم عرض', OfferRecipient.objects.filter(Q(offer__branch=branch) | Q(student__branch=branch))),
        ('عرض طالب', StudentOffer.objects.filter(branch=branch)),
        ('طالب', Contact.objects.filter(student__branch=branch)),
        ('بنك', Bank.objects.filter(branch=branch)),
        ('موظف', Person.objects.filter(branch=branch).exclude(is_superuser=True).exclude(pk=user.pk)),
    ]


class BranchDeleteView(BranchPermissionMixin, DeleteView):
    model = Branch
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    template_name = 'core/branch_confirm_delete.html'
    success_url = reverse_lazy('branch-list')
    required_perm = 'delete_branch'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        counts = [(label, qs.count()) for label, qs in branch_related_data(self.object, self.request.user)]
        context['related_counts'] = [(label, n) for label, n in counts if n]
        return context

    def form_valid(self, form):
        """حذف الفرع بكل البيانات المرتبطة بيه في عملية واحدة."""
        with transaction.atomic():
            for _label, qs in branch_related_data(self.object, self.request.user):
                qs.delete()
            response = super().form_valid(form)
        messages.success(self.request, 'تم حذف الفرع وكل البيانات المرتبطة به.')
        return response


# ============================================================
# AJAX Views
# ============================================================

@login_required
def companies_list_ajax(request):
    """جلب قائمة الشركات بصيغة JSON (للـ Modal)"""
    _check_perm(request.user, 'view_company')
    companies = list(Company.objects.values('id', 'name'))
    return JsonResponse({'companies': companies})


@login_required
@require_POST
def branch_create_ajax(request):
    """إنشاء فرع جديد عبر AJAX (للـ Modal العائم)"""
    _check_perm(request.user, 'add_branch')
    form = BranchForm(request.POST, request.FILES)
    if form.is_valid():
        try:
            branch = form.save()
            return JsonResponse({
                'success': True,
                'message': 'تم إنشاء الفرع بنجاح',
                'branch': {
                    'id': branch.id,
                    'name': branch.name,
                    'code': branch.code,
                }
            })
        except IntegrityError:
            return JsonResponse({
                'success': False,
                'errors': {'code': ['هذا الكود مستخدم بالفعل. جرب كود تاني.']}
            }, status=400)
    return JsonResponse({
        'success': False,
        'errors': form.errors
    }, status=400)


@login_required
@require_POST
def branch_update_ajax(request, pk):
    """تحديث فرع عبر AJAX (للـ Modal العائم)"""
    branch = get_object_or_404(Branch, pk=pk)
    _check_branch_perm(request.user, 'change_branch', branch)
    form = BranchForm(request.POST, request.FILES, instance=branch)
    if form.is_valid():
        form.save()
        return JsonResponse({
            'success': True,
            'message': 'تم تحديث الفرع بنجاح',
        })
    return JsonResponse({
        'success': False,
        'errors': form.errors
    }, status=400)


@login_required
@require_POST
def company_create_ajax(request):
    """إنشاء شركة جديدة عبر AJAX (للـ Modal العائم)"""
    _check_perm(request.user, 'add_company')
    form = CompanyForm(request.POST, request.FILES)
    if form.is_valid():
        company = form.save()
        return JsonResponse({
            'success': True,
            'message': 'تم إنشاء الشركة بنجاح',
            'company': {
                'id': company.id,
                'name': company.name,
            }
        })
    return JsonResponse({
        'success': False,
        'errors': form.errors
    }, status=400)


@login_required
@require_POST
def company_update_ajax(request, pk):
    """تحديث شركة عبر AJAX (للـ Modal العائم)"""
    company = get_object_or_404(Company, pk=pk)
    _check_perm(request.user, 'change_company')
    form = CompanyForm(request.POST, request.FILES, instance=company)
    if form.is_valid():
        form.save()
        return JsonResponse({
            'success': True,
            'message': 'تم تحديث الشركة بنجاح',
        })
    return JsonResponse({
        'success': False,
        'errors': form.errors
    }, status=400)
