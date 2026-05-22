from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
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


@login_required
def dashboard(request):
    # Base stats
    students_count = Student.objects.count()
    courses_count = Course.objects.count()
    registrations_count = Account.objects.count()
    payments_total = Payment.objects.aggregate(total=Sum('amount_number'))['total'] or 0
    offers_count = Offer.objects.count()
    branches_count = Branch.objects.count()
    student_offers_count = StudentOffer.objects.count()
    calls_count = Call.objects.count()

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
    monthly_payments_qs = Payment.objects.filter(
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
    offer_statuses = Offer.objects.values('master_payment_type').annotate(
        count=Count('id')
    ).order_by('-count')
    offer_status_labels = [os['master_payment_type'] for os in offer_statuses]
    offer_status_data = [os['count'] for os in offer_statuses]

    # Payment methods distribution
    payment_methods = Payment.objects.values('payment_method').annotate(
        count=Count('id')
    ).order_by('-count')
    payment_method_labels = [pm['payment_method'] for pm in payment_methods]
    payment_method_data = [pm['count'] for pm in payment_methods]

    # Recent everything (activity feed) — merged + paginated
    activities = []

    for s in Student.objects.select_related('contact').order_by('-created_at')[:50]:
        activities.append({
            'type': 'student',
            'title': f'طالب جديد: {s.get_full_name()}',
            'desc': s.contact.mobile or '',
            'time': s.created_at,
            'css_class': 'success',
        })

    for p in Payment.objects.select_related('account').order_by('-created_at')[:50]:
        activities.append({
            'type': 'payment',
            'title': f'سند قبض: {p.amount_number}',
            'desc': p.account.get_key(),
            'time': p.created_at,
            'css_class': 'warning',
        })

    for o in Offer.objects.select_related('master').order_by('-created_at')[:50]:
        activities.append({
            'type': 'offer',
            'title': f'عرض سعر: {o.customer_name}',
            'desc': o.master.name,
            'time': o.created_at,
            'css_class': 'info',
        })

    for r in Account.objects.select_related('student', 'course').order_by('-created_at')[:50]:
        activities.append({
            'type': 'registration',
            'title': f'تسجيل جديد: {r.student.get_full_name()}',
            'desc': r.course.master.name,
            'time': r.created_at,
            'css_class': 'purple',
        })

    for c in Call.objects.select_related('offer', 'person').order_by('-created_at')[:50]:
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
    recent_offers = Offer.objects.select_related('master').order_by('-created_at')[:6]
    recent_student_offers = StudentOffer.objects.select_related('branch', 'course').order_by('-created_at')[:6]

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
    }
    return render(request, 'core/dashboard.html', context)


# ============================================================
# Company Views
# ============================================================

class CompanyListView(LoginRequiredMixin, ListView):
    model = Company
    template_name = 'core/company_list.html'
    context_object_name = 'companies'
    paginate_by = 20


class CompanyDetailView(LoginRequiredMixin, DetailView):
    model = Company
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    template_name = 'core/company_detail.html'
    context_object_name = 'company'


class CompanyCreateView(LoginRequiredMixin, CreateView):
    model = Company
    form_class = CompanyForm
    template_name = 'core/company_form.html'
    success_url = reverse_lazy('company-list')

    def form_valid(self, form):
        messages.success(self.request, 'تم إنشاء الشركة بنجاح')
        return super().form_valid(form)


class CompanyUpdateView(LoginRequiredMixin, UpdateView):
    model = Company
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    form_class = CompanyForm
    template_name = 'core/company_form.html'
    success_url = reverse_lazy('company-list')

    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث الشركة بنجاح')
        return super().form_valid(form)


class CompanyDeleteView(LoginRequiredMixin, DeleteView):
    model = Company
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    template_name = 'core/company_confirm_delete.html'
    success_url = reverse_lazy('company-list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'تم حذف الشركة بنجاح')
        return super().delete(request, *args, **kwargs)


# ============================================================
# Branch Views
# ============================================================

class BranchListView(LoginRequiredMixin, ListView):
    model = Branch
    template_name = 'core/branch_list.html'
    context_object_name = 'branches'
    paginate_by = 20

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


class BranchDetailView(LoginRequiredMixin, DetailView):
    model = Branch
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    template_name = 'core/branch_detail.html'
    context_object_name = 'branch'


class BranchCreateView(LoginRequiredMixin, CreateView):
    model = Branch
    form_class = BranchForm
    template_name = 'core/branch_form.html'
    success_url = reverse_lazy('branch-list')

    def form_valid(self, form):
        messages.success(self.request, 'تم إنشاء الفرع بنجاح')
        return super().form_valid(form)


class BranchUpdateView(LoginRequiredMixin, UpdateView):
    model = Branch
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    form_class = BranchForm
    template_name = 'core/branch_form.html'
    success_url = reverse_lazy('branch-list')

    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث الفرع بنجاح')
        return super().form_valid(form)


class BranchDeleteView(LoginRequiredMixin, DeleteView):
    model = Branch
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    template_name = 'core/branch_confirm_delete.html'
    success_url = reverse_lazy('branch-list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'تم حذف الفرع بنجاح')
        return super().delete(request, *args, **kwargs)


# ============================================================
# Bank Views
# ============================================================

class BankListView(LoginRequiredMixin, ListView):
    model = Bank
    template_name = 'core/bank_list.html'
    context_object_name = 'banks'
    paginate_by = 20


class BankDetailView(LoginRequiredMixin, DetailView):
    model = Bank
    template_name = 'core/bank_detail.html'
    context_object_name = 'bank'


class BankCreateView(LoginRequiredMixin, CreateView):
    model = Bank
    form_class = BankForm
    template_name = 'core/bank_form.html'
    success_url = reverse_lazy('bank-list')

    def form_valid(self, form):
        messages.success(self.request, 'تم إنشاء البنك بنجاح')
        return super().form_valid(form)


class BankUpdateView(LoginRequiredMixin, UpdateView):
    model = Bank
    form_class = BankForm
    template_name = 'core/bank_form.html'
    success_url = reverse_lazy('bank-list')

    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث البنك بنجاح')
        return super().form_valid(form)


class BankDeleteView(LoginRequiredMixin, DeleteView):
    model = Bank
    template_name = 'core/bank_confirm_delete.html'
    success_url = reverse_lazy('bank-list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'تم حذف البنك بنجاح')
        return super().delete(request, *args, **kwargs)


# ============================================================
# MasterCategory Views
# ============================================================

class MasterCategoryListView(LoginRequiredMixin, ListView):
    model = MasterCategory
    template_name = 'core/mastercategory_list.html'
    context_object_name = 'categories'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['branches'] = Branch.objects.all()
        return context


class MasterCategoryDetailView(LoginRequiredMixin, DetailView):
    model = MasterCategory
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    template_name = 'core/mastercategory_detail.html'
    context_object_name = 'category'


class MasterCategoryCreateView(LoginRequiredMixin, CreateView):
    model = MasterCategory
    form_class = MasterCategoryForm
    template_name = 'core/mastercategory_form.html'
    success_url = reverse_lazy('mastercategory-list')

    def form_valid(self, form):
        messages.success(self.request, 'تم إنشاء التصنيف بنجاح')
        return super().form_valid(form)


class MasterCategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = MasterCategory
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    form_class = MasterCategoryForm
    template_name = 'core/mastercategory_form.html'
    success_url = reverse_lazy('mastercategory-list')

    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث التصنيف بنجاح')
        return super().form_valid(form)


class MasterCategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = MasterCategory
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    template_name = 'core/mastercategory_confirm_delete.html'
    success_url = reverse_lazy('mastercategory-list')

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
