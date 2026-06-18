from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Sum, Count, Q
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
from finance.models import Payment, Offer, Call
from offers.models import StudentOffer
from core.models import Branch, Company, Bank, MasterCategory
from .forms import CompanyForm, BranchForm, BankForm, MasterCategoryForm


def custom_page_not_found_view(request, exception):
    return render(request, '404.html', status=404)


def custom_permission_denied_view(request, exception=None):
    return render(request, '403.html', status=403)


@login_required
def dashboard(request):
    # Optional branch filter from URL ?branch=<id>
    selected_branch_id = request.GET.get('branch')
    selected_branch = None
    if selected_branch_id:
        selected_branch = get_object_or_404(Branch, pk=selected_branch_id)

    # Base querysets (filtered by branch if selected)
    student_qs = Student.objects.all()
    course_qs = Course.objects.all()
    account_qs = Account.objects.all()
    payment_qs = Payment.objects.all()
    offer_qs = Offer.objects.all()
    studentoffer_qs = StudentOffer.objects.all()
    call_qs = Call.objects.all()

    if selected_branch:
        student_qs = Student.objects.filter(
            accounts__course__master__branch=selected_branch
        ).distinct()
        course_qs = Course.objects.filter(master__branch=selected_branch)
        account_qs = Account.objects.filter(course__master__branch=selected_branch)
        payment_qs = Payment.objects.filter(account__course__master__branch=selected_branch)
        offer_qs = Offer.objects.filter(master__branch=selected_branch)
        studentoffer_qs = StudentOffer.objects.filter(branch=selected_branch)
        call_qs = Call.objects.filter(offer__master__branch=selected_branch)

    # Base stats
    students_count = student_qs.count()
    courses_count = course_qs.count()
    registrations_count = account_qs.count()
    payments_total = payment_qs.aggregate(total=Sum('amount_number'))['total'] or 0
    offers_count = offer_qs.count()
    branches_count = Branch.objects.count()
    student_offers_count = studentoffer_qs.count()
    calls_count = call_qs.count()

    # Branch stats with annotations
    branches = Branch.objects.select_related('company').all()
    branch_stats = []
    for branch in branches:
        branch_stats.append({
            'branch': branch,
            'registrations': Account.objects.filter(course__master__branch=branch).count(),
            'payments_total': Payment.objects.filter(account__course__master__branch=branch).aggregate(
                total=Sum('amount_number'))['total'] or 0,
            'offers': Offer.objects.filter(master__branch=branch).count(),
            'student_offers': StudentOffer.objects.filter(branch=branch).count(),
            'courses': Course.objects.filter(master__branch=branch).count(),
            'masters': Course.objects.filter(master__branch=branch).values('master').distinct().count(),
        })

    # Monthly payments chart (last 6 months)
    six_months_ago = timezone.now() - timezone.timedelta(days=180)
    monthly_payments_qs = payment_qs.filter(
        created_at__gte=six_months_ago
    ).annotate(month=TruncMonth('created_at')).values('month').annotate(
        total=Sum('amount_number')
    ).order_by('month')

    months_labels = []
    months_data = []
    for mp in monthly_payments_qs:
        months_labels.append(mp['month'].strftime('%Y-%m'))
        months_data.append(float(mp['total'] or 0))

    # Registrations by branch chart
    regs_by_branch = []
    regs_by_branch_labels = []
    for bs in branch_stats:
        regs_by_branch_labels.append(bs['branch'].name)
        regs_by_branch.append(bs['registrations'])

    # Offers status distribution
    offer_statuses = offer_qs.values('master_payment_type').annotate(
        count=Count('id')
    ).order_by('-count')
    offer_status_labels = [os['master_payment_type'] for os in offer_statuses]
    offer_status_data = [os['count'] for os in offer_statuses]

    # Payment methods distribution
    payment_methods = payment_qs.values('payment_method').annotate(
        count=Count('id')
    ).order_by('-count')
    payment_method_labels = [pm['payment_method'] for pm in payment_methods]
    payment_method_data = [pm['count'] for pm in payment_methods]

    # Recent everything (activity feed) — merged + paginated
    activities = []

    for s in student_qs.select_related('contact').order_by('-created_at')[:50]:
        activities.append({
            'type': 'student',
            'title': f'طالب جديد: {s.get_full_name()}',
            'desc': s.contact.mobile or '',
            'time': s.created_at,
            'css_class': 'success',
        })

    for p in payment_qs.select_related('account').order_by('-created_at')[:50]:
        activities.append({
            'type': 'payment',
            'title': f'سند قبض: {p.amount_number}',
            'desc': p.account.get_key(),
            'time': p.created_at,
            'css_class': 'warning',
        })

    for o in offer_qs.select_related('master').order_by('-created_at')[:50]:
        activities.append({
            'type': 'offer',
            'title': f'عرض سعر: {o.customer_name}',
            'desc': o.master.name,
            'time': o.created_at,
            'css_class': 'info',
        })

    for r in account_qs.select_related('student', 'course').order_by('-created_at')[:50]:
        activities.append({
            'type': 'registration',
            'title': f'تسجيل جديد: {r.student.get_full_name()}',
            'desc': r.course.master.name,
            'time': r.created_at,
            'css_class': 'purple',
        })

    for c in call_qs.select_related('offer', 'person').order_by('-created_at')[:50]:
        activities.append({
            'type': 'call',
            'title': f'مكالمة {c.get_call_type_display()}: {c.offer.customer_name}',
            'desc': f'بواسطة {c.person.get_short_name()}',
            'time': c.created_at,
            'css_class': 'danger',
        })

    activities.sort(key=lambda x: x['time'], reverse=True)

    paginator = Paginator(activities, 10)
    activity_page = request.GET.get('activity_page', 1)
    recent_activities = paginator.get_page(activity_page)

    # Keep separate small lists for other dashboard sections
    recent_offers = offer_qs.select_related('master').order_by('-created_at')[:6]
    recent_student_offers = studentoffer_qs.select_related('branch', 'course').order_by('-created_at')[:6]

    # Top 5 branches by revenue
    top_branches = sorted(branch_stats, key=lambda x: x['payments_total'], reverse=True)[:5]

    context = {
        'students_count': students_count,
        'courses_count': courses_count,
        'registrations_count': registrations_count,
        'payments_total': payments_total,
        'offers_count': offers_count,
        'branches_count': branches_count,
        'student_offers_count': student_offers_count,
        'calls_count': calls_count,
        'branch_stats': branch_stats,
        'recent_activities': recent_activities,
        'recent_offers': recent_offers,
        'recent_student_offers': recent_student_offers,
        'months_labels': months_labels,
        'months_data': months_data,
        'regs_by_branch_labels': regs_by_branch_labels,
        'regs_by_branch': regs_by_branch,
        'offer_status_labels': offer_status_labels,
        'offer_status_data': offer_status_data,
        'payment_method_labels': payment_method_labels,
        'payment_method_data': payment_method_data,
        'top_branches': top_branches,
        'selected_branch': selected_branch,
        'all_branches': branches,
    }
    return render(request, 'core/dashboard.html', context)


@login_required
def branch_dashboard(request, slug):
    """لوحة تحكم مفصلة لفرع معين"""
    branch = get_object_or_404(Branch, slug=slug)

    # Stats filtered by this branch
    registrations_qs = Account.objects.filter(course__master__branch=branch)
    payments_qs = Payment.objects.filter(account__course__master__branch=branch)
    offers_qs = Offer.objects.filter(master__branch=branch)
    studentoffers_qs = StudentOffer.objects.filter(branch=branch)
    courses_qs = Course.objects.filter(master__branch=branch)
    calls_qs = Call.objects.filter(offer__master__branch=branch)
    students_qs = Student.objects.filter(accounts__course__master__branch=branch).distinct()

    students_count = students_qs.count()
    courses_count = courses_qs.count()
    registrations_count = registrations_qs.count()
    payments_total = payments_qs.aggregate(total=Sum('amount_number'))['total'] or 0
    offers_count = offers_qs.count()
    student_offers_count = studentoffers_qs.count()
    calls_count = calls_qs.count()

    # Monthly payments chart (last 6 months)
    six_months_ago = timezone.now() - timezone.timedelta(days=180)
    monthly_payments_qs = payments_qs.filter(
        created_at__gte=six_months_ago
    ).annotate(month=TruncMonth('created_at')).values('month').annotate(
        total=Sum('amount_number')
    ).order_by('month')

    months_labels = []
    months_data = []
    for mp in monthly_payments_qs:
        months_labels.append(mp['month'].strftime('%Y-%m'))
        months_data.append(float(mp['total'] or 0))

    # Offers status distribution
    offer_statuses = offers_qs.values('master_payment_type').annotate(
        count=Count('id')
    ).order_by('-count')
    offer_status_labels = [os['master_payment_type'] for os in offer_statuses]
    offer_status_data = [os['count'] for os in offer_statuses]

    # Payment methods distribution
    payment_methods = payments_qs.values('payment_method').annotate(
        count=Count('id')
    ).order_by('-count')
    payment_method_labels = [pm['payment_method'] for pm in payment_methods]
    payment_method_data = [pm['count'] for pm in payment_methods]

    # Activity feed for this branch
    activities = []

    for s in students_qs.select_related('contact').order_by('-created_at')[:50]:
        activities.append({
            'type': 'student',
            'title': f'طالب جديد: {s.get_full_name()}',
            'desc': s.contact.mobile or '',
            'time': s.created_at,
            'css_class': 'success',
        })

    for p in payments_qs.select_related('account').order_by('-created_at')[:50]:
        activities.append({
            'type': 'payment',
            'title': f'سند قبض: {p.amount_number}',
            'desc': p.account.get_key(),
            'time': p.created_at,
            'css_class': 'warning',
        })

    for o in offers_qs.select_related('master').order_by('-created_at')[:50]:
        activities.append({
            'type': 'offer',
            'title': f'عرض سعر: {o.customer_name}',
            'desc': o.master.name,
            'time': o.created_at,
            'css_class': 'info',
        })

    for r in registrations_qs.select_related('student', 'course').order_by('-created_at')[:50]:
        activities.append({
            'type': 'registration',
            'title': f'تسجيل جديد: {r.student.get_full_name()}',
            'desc': r.course.master.name,
            'time': r.created_at,
            'css_class': 'purple',
        })

    for c in calls_qs.select_related('offer', 'person').order_by('-created_at')[:50]:
        activities.append({
            'type': 'call',
            'title': f'مكالمة {c.get_call_type_display()}: {c.offer.customer_name}',
            'desc': f'بواسطة {c.person.get_short_name()}',
            'time': c.created_at,
            'css_class': 'danger',
        })

    activities.sort(key=lambda x: x['time'], reverse=True)

    paginator = Paginator(activities, 10)
    activity_page = request.GET.get('activity_page', 1)
    recent_activities = paginator.get_page(activity_page)

    # Recent items
    recent_offers = offers_qs.select_related('master').order_by('-created_at')[:6]
    recent_student_offers = studentoffers_qs.select_related('branch', 'course').order_by('-created_at')[:6]

    context = {
        'branch': branch,
        'students_count': students_count,
        'courses_count': courses_count,
        'registrations_count': registrations_count,
        'payments_total': payments_total,
        'offers_count': offers_count,
        'student_offers_count': student_offers_count,
        'calls_count': calls_count,
        'recent_activities': recent_activities,
        'recent_offers': recent_offers,
        'recent_student_offers': recent_student_offers,
        'months_labels': months_labels,
        'months_data': months_data,
        'offer_status_labels': offer_status_labels,
        'offer_status_data': offer_status_data,
        'payment_method_labels': payment_method_labels,
        'payment_method_data': payment_method_data,
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


class BranchDeleteView(BranchPermissionMixin, DeleteView):
    model = Branch
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    template_name = 'core/branch_confirm_delete.html'
    success_url = reverse_lazy('branch-list')
    required_perm = 'delete_branch'

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'تم حذف الفرع بنجاح')
        return super().delete(request, *args, **kwargs)


# ============================================================
# Bank Views
# ============================================================

class BankListView(BranchPermissionMixin, ListView):
    model = Bank
    template_name = 'core/bank_list.html'
    context_object_name = 'banks'
    paginate_by = 20
    required_perm = 'view_bank'
    branch_field = 'branch'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = filter_by_branch(queryset, self.request.user, self.branch_field)
        return queryset


class BankDetailView(BranchPermissionMixin, DetailView):
    model = Bank
    template_name = 'core/bank_detail.html'
    context_object_name = 'bank'
    required_perm = 'view_bank'
    branch_field = None


class BankCreateView(BranchPermissionMixin, CreateView):
    model = Bank
    form_class = BankForm
    template_name = 'core/bank_form.html'
    success_url = reverse_lazy('bank-list')
    required_perm = 'add_bank'

    def form_valid(self, form):
        messages.success(self.request, 'تم إنشاء البنك بنجاح')
        return super().form_valid(form)


class BankUpdateView(BranchPermissionMixin, UpdateView):
    model = Bank
    form_class = BankForm
    template_name = 'core/bank_form.html'
    success_url = reverse_lazy('bank-list')
    required_perm = 'change_bank'

    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث البنك بنجاح')
        return super().form_valid(form)


class BankDeleteView(BranchPermissionMixin, DeleteView):
    model = Bank
    template_name = 'core/bank_confirm_delete.html'
    success_url = reverse_lazy('bank-list')
    required_perm = 'delete_bank'

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'تم حذف البنك بنجاح')
        return super().delete(request, *args, **kwargs)


# ============================================================
# MasterCategory Views
# ============================================================

class MasterCategoryListView(BranchPermissionMixin, ListView):
    model = MasterCategory
    template_name = 'core/mastercategory_list.html'
    context_object_name = 'categories'
    paginate_by = 20
    required_perm = 'view_mastercategory'
    branch_field = 'branch'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = filter_by_branch(queryset, self.request.user, self.branch_field)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['branches'] = Branch.objects.all()
        return context


class MasterCategoryDetailView(BranchPermissionMixin, DetailView):
    model = MasterCategory
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    template_name = 'core/mastercategory_detail.html'
    context_object_name = 'category'
    required_perm = 'view_mastercategory'
    branch_field = None


class MasterCategoryCreateView(BranchPermissionMixin, CreateView):
    model = MasterCategory
    form_class = MasterCategoryForm
    template_name = 'core/mastercategory_form.html'
    success_url = reverse_lazy('mastercategory-list')
    required_perm = 'add_mastercategory'

    def form_valid(self, form):
        messages.success(self.request, 'تم إنشاء التصنيف بنجاح')
        return super().form_valid(form)


class MasterCategoryUpdateView(BranchPermissionMixin, UpdateView):
    model = MasterCategory
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    form_class = MasterCategoryForm
    template_name = 'core/mastercategory_form.html'
    success_url = reverse_lazy('mastercategory-list')
    required_perm = 'change_mastercategory'

    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث التصنيف بنجاح')
        return super().form_valid(form)


class MasterCategoryDeleteView(BranchPermissionMixin, DeleteView):
    model = MasterCategory
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    template_name = 'core/mastercategory_confirm_delete.html'
    success_url = reverse_lazy('mastercategory-list')
    required_perm = 'delete_mastercategory'

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'تم حذف التصنيف بنجاح')
        return super().delete(request, *args, **kwargs)


# ============================================================
# AJAX Views
# ============================================================

@login_required
def companies_list_ajax(request):
    """جلب قائمة الشركات بصيغة JSON (للـ Modal)"""
    companies = list(Company.objects.values('id', 'name'))
    return JsonResponse({'companies': companies})


@login_required
@require_POST
def branch_create_ajax(request):
    """إنشاء فرع جديد عبر AJAX (للـ Modal العائم)"""
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
def mastercategory_create_ajax(request):
    """إنشاء تصنيف جديد عبر AJAX (للـ Modal العائم)"""
    form = MasterCategoryForm(request.POST)
    if form.is_valid():
        category = form.save()
        return JsonResponse({
            'success': True,
            'message': 'تم إنشاء التصنيف بنجاح',
            'category': {
                'id': category.id,
                'name': category.name,
            }
        })
    return JsonResponse({
        'success': False,
        'errors': form.errors
    }, status=400)


@login_required
@require_POST
def mastercategory_update_ajax(request, pk):
    """تحديث تصنيف عبر AJAX (للـ Modal العائم)"""
    category = get_object_or_404(MasterCategory, pk=pk)
    form = MasterCategoryForm(request.POST, instance=category)
    if form.is_valid():
        form.save()
        return JsonResponse({
            'success': True,
            'message': 'تم تحديث التصنيف بنجاح',
        })
    return JsonResponse({
        'success': False,
        'errors': form.errors
    }, status=400)


@login_required
@require_POST
def company_create_ajax(request):
    """إنشاء شركة جديدة عبر AJAX (للـ Modal العائم)"""
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
