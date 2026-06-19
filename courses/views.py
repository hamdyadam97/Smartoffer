from django.db import IntegrityError
from django.db.models import Q, Max
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from accounts.mixins import BranchPermissionMixin, filter_by_branch

from .models import Master, Course
from .forms import MasterForm, CourseForm


class MasterListView(BranchPermissionMixin, ListView):
    model = Master
    template_name = 'courses/master_list.html'
    context_object_name = 'masters'
    paginate_by = 20
    required_perm = 'view_master'
    branch_field = 'branch'

    def get_queryset(self):
        queryset = Master.objects.select_related('branch', 'master_category').all()
        queryset = filter_by_branch(
            queryset,
            self.request.user,
            'branch',
            perm=self.required_perm,
        )
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        branch = self.request.GET.get('branch')
        if branch:
            queryset = queryset.filter(branch_id=branch)
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(master_category_id=category)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from core.models import Branch, MasterCategory
        if self.request.user.is_executive():
            context['branches'] = Branch.objects.all().order_by('code', 'name')
            context['categories'] = MasterCategory.objects.all().order_by('name')
        else:
            allowed_ids = [b.pk for b in self.request.user.get_branches_for_perm(self.required_perm)]
            context['branches'] = Branch.objects.filter(pk__in=allowed_ids).order_by('code', 'name')
            context['categories'] = MasterCategory.objects.filter(
                Q(branch__pk__in=allowed_ids) | Q(branch__isnull=True)
            ).order_by('name')
        return context


class MasterDetailView(BranchPermissionMixin, DetailView):
    required_perm = 'view_master'
    branch_field = 'branch'
    model = Master
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    template_name = 'courses/master_detail.html'
    context_object_name = 'master'


class MasterCreateView(BranchPermissionMixin, CreateView):
    required_perm = 'add_master'
    branch_field = 'branch'
    model = Master
    form_class = MasterForm
    template_name = 'courses/master_form.html'
    success_url = reverse_lazy('master-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.last_person = self.request.user
        return super().form_valid(form)


class MasterUpdateView(BranchPermissionMixin, UpdateView):
    required_perm = 'change_master'
    branch_field = 'branch'
    model = Master
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    form_class = MasterForm
    template_name = 'courses/master_form.html'
    success_url = reverse_lazy('master-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.last_person = self.request.user
        return super().form_valid(form)


class MasterDeleteView(BranchPermissionMixin, DeleteView):
    required_perm = 'delete_master'
    branch_field = 'branch'
    model = Master
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    template_name = 'courses/master_confirm_delete.html'
    success_url = reverse_lazy('master-list')


class CourseListView(BranchPermissionMixin, ListView):
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'
    paginate_by = 20
    required_perm = 'view_course'
    branch_field = 'master__branch'

    def get_queryset(self):
        queryset = Course.objects.select_related('master', 'master__branch').all()
        queryset = filter_by_branch(
            queryset,
            self.request.user,
            'master__branch',
            perm=self.required_perm,
        )
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(instructor__icontains=search) | Q(company_name__icontains=search)
            )
        master = self.request.GET.get('master')
        if master:
            queryset = queryset.filter(master_id=master)
        level = self.request.GET.get('target_level')
        if level:
            queryset = queryset.filter(target_level=level)
        start_after = self.request.GET.get('start_after')
        if start_after:
            queryset = queryset.filter(start_date__gte=start_after)
        return queryset


class CourseDetailView(BranchPermissionMixin, DetailView):
    required_perm = 'view_course'
    branch_field = 'master__branch'
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'


class CourseCreateView(BranchPermissionMixin, CreateView):
    required_perm = 'add_course'
    branch_field = 'master__branch'
    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'
    success_url = reverse_lazy('course-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from core.models import Branch, MasterCategory
        user = self.request.user
        if user.is_executive():
            context['branches'] = Branch.objects.all().order_by('code', 'name')
            context['categories'] = MasterCategory.objects.all().order_by('name')
        else:
            allowed_ids = [b.pk for b in user.get_branches_for_perm('add_master')]
            context['branches'] = Branch.objects.filter(pk__in=allowed_ids).order_by('code', 'name')
            context['categories'] = MasterCategory.objects.filter(
                Q(branch__pk__in=allowed_ids) | Q(branch__isnull=True)
            ).order_by('name')
        return context

    def form_valid(self, form):
        form.instance.last_person = self.request.user
        return super().form_valid(form)


class CourseUpdateView(BranchPermissionMixin, UpdateView):
    required_perm = 'change_course'
    branch_field = 'master__branch'
    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'
    success_url = reverse_lazy('course-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from core.models import Branch, MasterCategory
        user = self.request.user
        if user.is_executive():
            context['branches'] = Branch.objects.all().order_by('code', 'name')
            context['categories'] = MasterCategory.objects.all().order_by('name')
        else:
            allowed_ids = [b.pk for b in user.get_branches_for_perm('add_master')]
            context['branches'] = Branch.objects.filter(pk__in=allowed_ids).order_by('code', 'name')
            context['categories'] = MasterCategory.objects.filter(
                Q(branch__pk__in=allowed_ids) | Q(branch__isnull=True)
            ).order_by('name')
        return context

    def form_valid(self, form):
        form.instance.last_person = self.request.user
        return super().form_valid(form)


class CourseDeleteView(BranchPermissionMixin, DeleteView):
    required_perm = 'delete_course'
    branch_field = 'master__branch'
    model = Course
    template_name = 'courses/course_confirm_delete.html'
    success_url = reverse_lazy('course-list')


# ============================================================
# AJAX Views
# ============================================================

@login_required
@require_POST
def master_create_ajax(request):
    """إنشاء تخصص جديد عبر AJAX (للـ Modal)"""
    if not request.user.has_perm_on_any_branch('add_master'):
        raise PermissionDenied('غير مسموح لك دخول هنا')

    form = MasterForm(request.POST, user=request.user)
    if form.is_valid():
        try:
            master = form.save(commit=False)
            master.last_person = request.user
            master.save()
            return JsonResponse({
                'success': True,
                'message': 'تم إنشاء التخصص بنجاح',
                'master': {
                    'id': master.id,
                    'name': master.name,
                    'code': master.code,
                    'slug': master.slug,
                }
            })
        except IntegrityError:
            return JsonResponse({
                'success': False,
                'errors': {'code': ['هذا الكود مستخدم بالفعل في نفس الفرع. جرب كود تاني.']}
            }, status=400)
    return JsonResponse({
        'success': False,
        'errors': form.errors
    }, status=400)


@login_required
def master_info_ajax(request, pk):
    """جلب معلومات التخصص لإنشاء دورة (الشركة + الكود التالي)"""
    master = get_object_or_404(Master, pk=pk)
    # التحقق من صلاحية رؤية التخصص
    if not request.user.is_executive():
        allowed_ids = [b.pk for b in request.user.get_branches_for_perm('add_course')]
        if master.branch_id not in allowed_ids:
            raise PermissionDenied('غير مسموح لك دخول هنا')

    company_name = master.branch.company.name if master.branch and master.branch.company else ''
    last_code = Course.objects.filter(master=master).aggregate(Max('code'))['code__max'] or 0
    next_code = int(last_code) + 1

    return JsonResponse({
        'success': True,
        'company_name': company_name,
        'next_code': next_code,
        'master': {
            'id': master.id,
            'name': master.name,
            'code': master.code,
        }
    })
