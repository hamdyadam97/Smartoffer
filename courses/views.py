from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required

from .models import Master, Course
from .forms import MasterForm, CourseForm


class MasterListView(LoginRequiredMixin, ListView):
    model = Master
    template_name = 'courses/master_list.html'
    context_object_name = 'masters'
    paginate_by = 20

    def get_queryset(self):
        queryset = Master.objects.select_related('branch', 'master_category').all()
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
        context['branches'] = Branch.objects.all()
        context['categories'] = MasterCategory.objects.all()
        return context


class MasterDetailView(LoginRequiredMixin, DetailView):
    model = Master
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    template_name = 'courses/master_detail.html'
    context_object_name = 'master'


class MasterCreateView(LoginRequiredMixin, CreateView):
    model = Master
    form_class = MasterForm
    template_name = 'courses/master_form.html'
    success_url = reverse_lazy('master-list')

    def form_valid(self, form):
        form.instance.last_person = self.request.user
        return super().form_valid(form)


class MasterUpdateView(LoginRequiredMixin, UpdateView):
    model = Master
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    form_class = MasterForm
    template_name = 'courses/master_form.html'
    success_url = reverse_lazy('master-list')

    def form_valid(self, form):
        form.instance.last_person = self.request.user
        return super().form_valid(form)


class MasterDeleteView(LoginRequiredMixin, DeleteView):
    model = Master
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    template_name = 'courses/master_confirm_delete.html'
    success_url = reverse_lazy('master-list')


class CourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'
    paginate_by = 20

    def get_queryset(self):
        queryset = Course.objects.select_related('master', 'master__branch').all()
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


class CourseDetailView(LoginRequiredMixin, DetailView):
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'


class CourseCreateView(LoginRequiredMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'
    success_url = reverse_lazy('course-list')

    def form_valid(self, form):
        form.instance.last_person = self.request.user
        return super().form_valid(form)


class CourseUpdateView(LoginRequiredMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'
    success_url = reverse_lazy('course-list')

    def form_valid(self, form):
        form.instance.last_person = self.request.user
        return super().form_valid(form)


class CourseDeleteView(LoginRequiredMixin, DeleteView):
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
    form = MasterForm(request.POST)
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
