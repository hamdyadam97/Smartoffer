from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied

from accounts.mixins import BranchPermissionMixin, filter_by_branch

from .models import Course
from .forms import CourseForm

# «التخصصات»: كل تخصص (دبلوم أو دورة) بكل بياناته. التخصص اللي فرعه فاضي متاح لكل الفروع.


def _form_branches(user, perm):
    from core.models import Branch
    branches = Branch.objects.select_related('company').order_by('code', 'name')
    if user.is_executive():
        return branches
    return branches.filter(pk__in=[b.pk for b in user.get_branches_for_perm(perm)])


class CourseListView(BranchPermissionMixin, ListView):
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'
    paginate_by = 20
    required_perm = 'view_course'
    branch_field = 'branch'
    include_shared = True

    def get_queryset(self):
        queryset = super().get_queryset().select_related('branch', 'branch__company')
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search) |
                Q(instructor__icontains=search) | Q(company_name__icontains=search)
            )
        program_type = self.request.GET.get('program_type')
        if program_type:
            queryset = queryset.filter(program_type=program_type)
        level = self.request.GET.get('target_level')
        if level:
            queryset = queryset.filter(target_level=level)
        start_after = self.request.GET.get('start_after')
        if start_after:
            queryset = queryset.filter(start_date__gte=start_after)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['program_types'] = Course.PROGRAM_TYPE_CHOICES
        context['branches'] = _form_branches(self.request.user, 'add_course')
        return context


class CourseDetailView(BranchPermissionMixin, DetailView):
    required_perm = 'view_course'
    branch_field = 'branch'
    include_shared = True
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # التخصص ممكن يبقى لكل الفروع، فالطلاب بيظهروا من فروع المستخدم بس
        context['accounts'] = filter_by_branch(
            self.object.accounts.select_related('student__contact', 'student__branch'),
            self.request.user, 'student__branch', perm='view_registration',
        )
        return context


class CourseUpdateView(BranchPermissionMixin, UpdateView):
    required_perm = 'change_course'
    branch_field = 'branch'
    include_shared = True
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
        context['branches'] = _form_branches(self.request.user, 'change_course')
        return context

    def form_valid(self, form):
        form.instance.last_person = self.request.user
        return super().form_valid(form)


class CourseDeleteView(BranchPermissionMixin, DeleteView):
    required_perm = 'delete_course'
    branch_field = 'branch'
    include_shared = True
    model = Course
    template_name = 'courses/course_confirm_delete.html'
    success_url = reverse_lazy('course-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['accounts_count'] = self.object.accounts.count()
        return context

    def form_valid(self, form):
        """حذف التخصص بكل اللي مرتبط بيه: التسجيلات (ومرفقاتها وشروطها وملاحظاتها)."""
        from registrations.models import Account
        with transaction.atomic():
            Account.objects.filter(course=self.object).delete()
            response = super().form_valid(form)
        messages.success(self.request, 'تم حذف التخصص وكل البيانات المرتبطة به.')
        return response


# ============================================================
# AJAX Views
# ============================================================

@login_required
@require_POST
def course_create_ajax(request):
    """إنشاء تخصص جديد عبر AJAX (للـ Modal)"""
    if not request.user.has_perm_on_any_branch('add_course'):
        raise PermissionDenied('غير مسموح لك دخول هنا')

    form = CourseForm(request.POST, user=request.user)
    if form.is_valid():
        course = form.save(commit=False)
        course.last_person = request.user
        course.save()
        return JsonResponse({
            'success': True,
            'message': 'تم إنشاء التخصص بنجاح',
            'course': {
                'id': course.id,
                'code': course.code,
                'display_name': course.get_display_name(),
                'detail_url': reverse('course-detail', args=[course.pk]),
            }
        })
    return JsonResponse({
        'success': False,
        'errors': form.errors
    }, status=400)
