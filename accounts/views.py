from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.urls import reverse_lazy
from django.db import models
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Person, Team, BranchAccess, Role, EmployeeRole, EmployeePerformance, Permission
from .forms import (
    PersonCreationForm, PersonChangeForm, TeamForm,
    BranchAccessForm, RoleForm, EmployeeRoleForm, EmployeePerformanceForm, PermissionForm
)


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'بيانات الدخول غير صحيحة')
    return render(request, 'registration/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


# ============================================================
# Person Views
# ============================================================

class PersonListView(LoginRequiredMixin, ListView):
    model = Person
    template_name = 'accounts/person_list.html'
    context_object_name = 'persons'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(first_name__icontains=search) |
                models.Q(email__icontains=search) |
                models.Q(forth_name__icontains=search) |
                models.Q(slug__icontains=search)
            )
        team = self.request.GET.get('team')
        if team:
            queryset = queryset.filter(team_id=team)
        branch = self.request.GET.get('branch')
        if branch:
            queryset = queryset.filter(branch_id=branch)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from core.models import Branch
        context['teams'] = Team.objects.all()
        context['branches'] = Branch.objects.all()
        context['roles'] = Role.objects.all()
        return context


class PersonDetailView(LoginRequiredMixin, DetailView):
    model = Person
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    template_name = 'accounts/person_detail.html'
    context_object_name = 'person'


class PersonCreateView(LoginRequiredMixin, CreateView):
    model = Person
    form_class = PersonCreationForm
    template_name = 'accounts/person_form.html'
    success_url = reverse_lazy('person-list')

    def form_valid(self, form):
        messages.success(self.request, 'تم إنشاء المستخدم بنجاح')
        return super().form_valid(form)


class PersonUpdateView(LoginRequiredMixin, UpdateView):
    model = Person
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    form_class = PersonChangeForm
    template_name = 'accounts/person_form.html'
    success_url = reverse_lazy('person-list')

    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث المستخدم بنجاح')
        return super().form_valid(form)


class PersonDeleteView(LoginRequiredMixin, DeleteView):
    model = Person
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    template_name = 'accounts/person_confirm_delete.html'
    success_url = reverse_lazy('person-list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'تم حذف المستخدم بنجاح')
        return super().delete(request, *args, **kwargs)


@require_POST
def person_create_ajax(request):
    form = PersonCreationForm(request.POST, request.FILES)
    if form.is_valid():
        person = form.save()
        return JsonResponse({'success': True, 'message': 'تم إنشاء الموظف بنجاح', 'id': person.id, 'slug': person.slug})
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


@require_POST
def person_update_ajax(request, pk):
    person = get_object_or_404(Person, pk=pk)
    form = PersonChangeForm(request.POST, request.FILES, instance=person)
    if form.is_valid():
        form.save()
        return JsonResponse({'success': True, 'message': 'تم تحديث الموظف بنجاح'})
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


# ============================================================
# Team Views
# ============================================================

class TeamListView(LoginRequiredMixin, ListView):
    model = Team
    template_name = 'accounts/team_list.html'
    context_object_name = 'teams'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from core.models import Branch
        context['branches'] = Branch.objects.all()
        context['roles'] = Role.objects.all()
        return context


class TeamDetailView(LoginRequiredMixin, DetailView):
    model = Team
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    template_name = 'accounts/team_detail.html'
    context_object_name = 'team'


class TeamCreateView(LoginRequiredMixin, CreateView):
    model = Team
    form_class = TeamForm
    template_name = 'accounts/team_form.html'
    success_url = reverse_lazy('team-list')

    def form_valid(self, form):
        messages.success(self.request, 'تم إنشاء الفريق بنجاح')
        return super().form_valid(form)


class TeamUpdateView(LoginRequiredMixin, UpdateView):
    model = Team
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    form_class = TeamForm
    template_name = 'accounts/team_form.html'
    success_url = reverse_lazy('team-list')

    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث الفريق بنجاح')
        return super().form_valid(form)


class TeamDeleteView(LoginRequiredMixin, DeleteView):
    model = Team
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    template_name = 'accounts/team_confirm_delete.html'
    success_url = reverse_lazy('team-list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'تم حذف الفريق بنجاح')
        return super().delete(request, *args, **kwargs)


@require_POST
def team_create_ajax(request):
    form = TeamForm(request.POST)
    if form.is_valid():
        team = form.save()
        return JsonResponse({'success': True, 'message': 'تم إنشاء الفريق بنجاح', 'id': team.id, 'slug': team.slug})
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


@require_POST
def team_update_ajax(request, pk):
    team = get_object_or_404(Team, pk=pk)
    form = TeamForm(request.POST, instance=team)
    if form.is_valid():
        form.save()
        return JsonResponse({'success': True, 'message': 'تم تحديث الفريق بنجاح'})
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


# ============================================================
# BranchAccess Views
# ============================================================

class BranchAccessListView(LoginRequiredMixin, ListView):
    model = BranchAccess
    template_name = 'accounts/branchaccess_list.html'
    context_object_name = 'accesses'
    paginate_by = 20


class BranchAccessCreateView(LoginRequiredMixin, CreateView):
    model = BranchAccess
    form_class = BranchAccessForm
    template_name = 'accounts/branchaccess_form.html'
    success_url = reverse_lazy('branchaccess-list')

    def form_valid(self, form):
        messages.success(self.request, 'تم إنشاء صلاحية الفرع بنجاح')
        return super().form_valid(form)


class BranchAccessUpdateView(LoginRequiredMixin, UpdateView):
    model = BranchAccess
    form_class = BranchAccessForm
    template_name = 'accounts/branchaccess_form.html'
    success_url = reverse_lazy('branchaccess-list')

    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث صلاحية الفرع بنجاح')
        return super().form_valid(form)


class BranchAccessDeleteView(LoginRequiredMixin, DeleteView):
    model = BranchAccess
    template_name = 'accounts/branchaccess_confirm_delete.html'
    success_url = reverse_lazy('branchaccess-list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'تم حذف صلاحية الفرع بنجاح')
        return super().delete(request, *args, **kwargs)


# ============================================================
# Role Views
# ============================================================

class RoleListView(LoginRequiredMixin, ListView):
    model = Role
    template_name = 'accounts/role_list.html'
    context_object_name = 'roles'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(name__icontains=search) |
                models.Q(description__icontains=search) |
                models.Q(slug__icontains=search)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .models import Permission
        from collections import defaultdict
        perms = Permission.objects.all().order_by('app_label', 'model_name', 'action')
        grouped = defaultdict(lambda: defaultdict(list))
        for p in perms:
            grouped[p.app_label][p.model_name].append(p)
        context['grouped_permissions'] = {app: dict(models) for app, models in grouped.items()}
        return context


class RoleDetailView(LoginRequiredMixin, DetailView):
    model = Role
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    template_name = 'accounts/role_detail.html'
    context_object_name = 'role'


class RoleCreateView(LoginRequiredMixin, CreateView):
    model = Role
    form_class = RoleForm
    template_name = 'accounts/role_form.html'
    success_url = reverse_lazy('role-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .models import Permission
        from collections import defaultdict
        perms = Permission.objects.all().order_by('app_label', 'model_name', 'action')
        grouped = defaultdict(lambda: defaultdict(list))
        for p in perms:
            grouped[p.app_label][p.model_name].append(p)
        context['grouped_permissions'] = {app: dict(models) for app, models in grouped.items()}
        context['selected_permissions'] = []
        return context

    def form_valid(self, form):
        messages.success(self.request, 'تم إنشاء الدور بنجاح')
        return super().form_valid(form)


class RoleUpdateView(LoginRequiredMixin, UpdateView):
    model = Role
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    form_class = RoleForm
    template_name = 'accounts/role_form.html'
    success_url = reverse_lazy('role-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .models import Permission
        from collections import defaultdict
        perms = Permission.objects.all().order_by('app_label', 'model_name', 'action')
        grouped = defaultdict(lambda: defaultdict(list))
        for p in perms:
            grouped[p.app_label][p.model_name].append(p)
        context['grouped_permissions'] = {app: dict(models) for app, models in grouped.items()}
        context['selected_permissions'] = list(self.object.permissions.values_list('id', flat=True))
        return context

    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث الدور بنجاح')
        return super().form_valid(form)


class RoleDeleteView(LoginRequiredMixin, DeleteView):
    model = Role
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    template_name = 'accounts/role_confirm_delete.html'
    success_url = reverse_lazy('role-list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'تم حذف الدور بنجاح')
        return super().delete(request, *args, **kwargs)


@require_POST
def role_create_ajax(request):
    form = RoleForm(request.POST)
    if form.is_valid():
        role = form.save()
        return JsonResponse({'success': True, 'message': 'تم إنشاء الدور بنجاح', 'id': role.id, 'slug': role.slug})
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


@require_POST
def role_update_ajax(request, pk):
    role = get_object_or_404(Role, pk=pk)
    form = RoleForm(request.POST, instance=role)
    if form.is_valid():
        form.save()
        return JsonResponse({'success': True, 'message': 'تم تحديث الدور بنجاح'})
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


# ============================================================
# Permission Views
# ============================================================

class PermissionListView(LoginRequiredMixin, ListView):
    model = Permission
    template_name = 'accounts/permission_list.html'
    context_object_name = 'permissions'
    paginate_by = 30

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(name__icontains=search) |
                models.Q(codename__icontains=search) |
                models.Q(app_label__icontains=search) |
                models.Q(model_name__icontains=search)
            )
        app = self.request.GET.get('app')
        if app:
            queryset = queryset.filter(app_label=app)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['apps'] = Permission.objects.values_list('app_label', flat=True).distinct().order_by('app_label')
        return context


class PermissionCreateView(LoginRequiredMixin, CreateView):
    model = Permission
    form_class = PermissionForm
    template_name = 'accounts/permission_form.html'
    success_url = reverse_lazy('permission-list')

    def form_valid(self, form):
        messages.success(self.request, 'تم إنشاء الصلاحية بنجاح')
        return super().form_valid(form)


class PermissionUpdateView(LoginRequiredMixin, UpdateView):
    model = Permission
    form_class = PermissionForm
    template_name = 'accounts/permission_form.html'
    success_url = reverse_lazy('permission-list')

    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث الصلاحية بنجاح')
        return super().form_valid(form)


class PermissionDeleteView(LoginRequiredMixin, DeleteView):
    model = Permission
    template_name = 'accounts/permission_confirm_delete.html'
    success_url = reverse_lazy('permission-list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'تم حذف الصلاحية بنجاح')
        return super().delete(request, *args, **kwargs)


@require_POST
def permission_create_ajax(request):
    form = PermissionForm(request.POST)
    if form.is_valid():
        perm = form.save()
        return JsonResponse({'success': True, 'message': 'تم إنشاء الصلاحية بنجاح', 'id': perm.id})
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


@require_POST
def permission_update_ajax(request, pk):
    perm = get_object_or_404(Permission, pk=pk)
    form = PermissionForm(request.POST, instance=perm)
    if form.is_valid():
        form.save()
        return JsonResponse({'success': True, 'message': 'تم تحديث الصلاحية بنجاح'})
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


# ============================================================
# EmployeeRole Views
# ============================================================

class EmployeeRoleListView(LoginRequiredMixin, ListView):
    model = EmployeeRole
    template_name = 'accounts/employeerole_list.html'
    context_object_name = 'employee_roles'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['teams'] = Team.objects.all()
        context['roles'] = Role.objects.all()
        context['persons'] = Person.objects.filter(is_staff=True).order_by('first_name', 'forth_name')
        from core.models import Branch
        context['branches'] = Branch.objects.all()
        return context


class EmployeeRoleCreateView(LoginRequiredMixin, CreateView):
    model = EmployeeRole
    form_class = EmployeeRoleForm
    template_name = 'accounts/employeerole_form.html'
    success_url = reverse_lazy('employeerole-list')

    def form_valid(self, form):
        messages.success(self.request, 'تم إنشاء دور الموظف بنجاح')
        return super().form_valid(form)


class EmployeeRoleUpdateView(LoginRequiredMixin, UpdateView):
    model = EmployeeRole
    form_class = EmployeeRoleForm
    template_name = 'accounts/employeerole_form.html'
    success_url = reverse_lazy('employeerole-list')

    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث دور الموظف بنجاح')
        return super().form_valid(form)


class EmployeeRoleDeleteView(LoginRequiredMixin, DeleteView):
    model = EmployeeRole
    template_name = 'accounts/employeerole_confirm_delete.html'
    success_url = reverse_lazy('employeerole-list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'تم حذف دور الموظف بنجاح')
        return super().delete(request, *args, **kwargs)


@require_POST
def employeerole_bulk_create(request):
    """Assign a role to person(s) across multiple branches."""
    role_id = request.POST.get('role')
    if not role_id:
        return JsonResponse({'success': False, 'message': 'الدور مطلوب'}, status=400)

    role = get_object_or_404(Role, pk=role_id)

    # Determine branches
    all_branches = request.POST.get('all_branches') == 'on'
    if all_branches:
        from core.models import Branch
        branches = list(Branch.objects.all())
    else:
        branch_ids = request.POST.getlist('branches')
        if not branch_ids:
            return JsonResponse({'success': False, 'message': 'اختر فرعاً واحداً على الأقل'}, status=400)
        from core.models import Branch
        branches = list(Branch.objects.filter(pk__in=branch_ids))

    # Determine persons
    person_id = request.POST.get('person')
    team_id = request.POST.get('team')

    if person_id:
        persons = [get_object_or_404(Person, pk=person_id)]
    elif team_id:
        team = get_object_or_404(Team, pk=team_id)
        persons = list(team.members.all())
    else:
        return JsonResponse({'success': False, 'message': 'اختر موظف أو فريق'}, status=400)

    created = 0
    skipped = 0
    for person in persons:
        for branch in branches:
            obj, was_created = EmployeeRole.objects.get_or_create(
                person=person, role=role, branch=branch
            )
            if was_created:
                created += 1
            else:
                skipped += 1

    msg = f'تم إنشاء {created} دور بنجاح'
    if skipped:
        msg += f' (تم تخطي {skipped} مسجل مسبقاً)'
    return JsonResponse({'success': True, 'message': msg})


# ============================================================
# EmployeePerformance Views
# ============================================================

class EmployeePerformanceListView(LoginRequiredMixin, ListView):
    model = EmployeePerformance
    template_name = 'accounts/employeeperformance_list.html'
    context_object_name = 'performances'
    paginate_by = 20


class EmployeePerformanceCreateView(LoginRequiredMixin, CreateView):
    model = EmployeePerformance
    form_class = EmployeePerformanceForm
    template_name = 'accounts/employeeperformance_form.html'
    success_url = reverse_lazy('employeeperformance-list')

    def form_valid(self, form):
        messages.success(self.request, 'تم إنشاء أداء الموظف بنجاح')
        return super().form_valid(form)


class EmployeePerformanceUpdateView(LoginRequiredMixin, UpdateView):
    model = EmployeePerformance
    form_class = EmployeePerformanceForm
    template_name = 'accounts/employeeperformance_form.html'
    success_url = reverse_lazy('employeeperformance-list')

    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث أداء الموظف بنجاح')
        return super().form_valid(form)


class EmployeePerformanceDeleteView(LoginRequiredMixin, DeleteView):
    model = EmployeePerformance
    template_name = 'accounts/employeeperformance_confirm_delete.html'
    success_url = reverse_lazy('employeeperformance-list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'تم حذف أداء الموظف بنجاح')
        return super().delete(request, *args, **kwargs)
