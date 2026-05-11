from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404

from courses.models import Course
from students.models import Student
from .models import Account, AttachType, Attach, AccountAttach, AccountCondition, AccountNote
from .forms import (
    AccountForm, AttachTypeForm, AttachForm,
    AccountAttachForm, AccountConditionForm, AccountNoteForm,
)


# ============================================================
# Account Views
# ============================================================

class AccountListView(LoginRequiredMixin, ListView):
    model = Account
    template_name = 'registrations/account_list.html'
    context_object_name = 'accounts'
    paginate_by = 20

    def get_queryset(self):
        queryset = Account.objects.select_related('student', 'course', 'course__master', 'last_person').all()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(student__contact__first_name__icontains=search) |
                Q(student__contact__forth_name__icontains=search)
            )
        course = self.request.GET.get('course')
        if course:
            queryset = queryset.filter(course_id=course)
        student = self.request.GET.get('student')
        if student:
            queryset = queryset.filter(student_id=student)
        payment_type = self.request.GET.get('payment_type')
        if payment_type:
            queryset = queryset.filter(course_payment_type=payment_type)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['courses'] = Course.objects.select_related('master').all()
        context['students'] = Student.objects.select_related('contact').all()
        return context


class AccountDetailView(LoginRequiredMixin, DetailView):
    model = Account
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    template_name = 'registrations/account_detail.html'
    context_object_name = 'account'

    def get_queryset(self):
        return Account.objects.select_related('student', 'course', 'course__master', 'last_person')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['courses'] = Course.objects.select_related('master').all()
        context['students'] = Student.objects.select_related('contact').all()
        return context


class AccountCreateView(LoginRequiredMixin, CreateView):
    model = Account
    form_class = AccountForm
    template_name = 'registrations/account_form.html'
    success_url = reverse_lazy('registration-list')

    def form_valid(self, form):
        form.instance.last_person = self.request.user
        return super().form_valid(form)


class AccountUpdateView(LoginRequiredMixin, UpdateView):
    model = Account
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    form_class = AccountForm
    template_name = 'registrations/account_form.html'
    success_url = reverse_lazy('registration-list')

    def form_valid(self, form):
        form.instance.last_person = self.request.user
        return super().form_valid(form)


class AccountDeleteView(LoginRequiredMixin, DeleteView):
    model = Account
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    template_name = 'registrations/account_confirm_delete.html'
    success_url = reverse_lazy('registration-list')


@require_POST
def account_create_ajax(request):
    form = AccountForm(request.POST)
    if form.is_valid():
        account = form.save(commit=False)
        account.last_person = request.user
        account.save()
        return JsonResponse({'success': True, 'message': 'تم إنشاء التسجيل بنجاح', 'id': account.id, 'slug': account.slug})
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


@require_POST
def account_update_ajax(request, pk):
    account = get_object_or_404(Account, pk=pk)
    form = AccountForm(request.POST, instance=account)
    if form.is_valid():
        account = form.save(commit=False)
        account.last_person = request.user
        account.save()
        return JsonResponse({'success': True, 'message': 'تم تحديث التسجيل بنجاح'})
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


# ============================================================
# AttachType Views
# ============================================================

class AttachTypeListView(LoginRequiredMixin, ListView):
    model = AttachType
    template_name = 'registrations/attachtype_list.html'
    context_object_name = 'attach_types'
    paginate_by = 20


class AttachTypeDetailView(LoginRequiredMixin, DetailView):
    model = AttachType
    template_name = 'registrations/attachtype_detail.html'
    context_object_name = 'attach_type'


class AttachTypeCreateView(LoginRequiredMixin, CreateView):
    model = AttachType
    form_class = AttachTypeForm
    template_name = 'registrations/attachtype_form.html'
    success_url = reverse_lazy('attachtype-list')


class AttachTypeUpdateView(LoginRequiredMixin, UpdateView):
    model = AttachType
    form_class = AttachTypeForm
    template_name = 'registrations/attachtype_form.html'
    success_url = reverse_lazy('attachtype-list')


class AttachTypeDeleteView(LoginRequiredMixin, DeleteView):
    model = AttachType
    template_name = 'registrations/attachtype_confirm_delete.html'
    success_url = reverse_lazy('attachtype-list')


# ============================================================
# Attach Views
# ============================================================

class AttachListView(LoginRequiredMixin, ListView):
    model = Attach
    template_name = 'registrations/attach_list.html'
    context_object_name = 'attaches'
    paginate_by = 20

    def get_queryset(self):
        queryset = Attach.objects.select_related('attach_type', 'person').all()
        attach_type = self.request.GET.get('type')
        if attach_type:
            queryset = queryset.filter(attach_type_id=attach_type)
        return queryset


class AttachDetailView(LoginRequiredMixin, DetailView):
    model = Attach
    template_name = 'registrations/attach_detail.html'
    context_object_name = 'attach'

    def get_queryset(self):
        return Attach.objects.select_related('attach_type', 'person')


class AttachCreateView(LoginRequiredMixin, CreateView):
    model = Attach
    form_class = AttachForm
    template_name = 'registrations/attach_form.html'
    success_url = reverse_lazy('attach-list')

    def form_valid(self, form):
        form.instance.person = self.request.user
        return super().form_valid(form)


class AttachUpdateView(LoginRequiredMixin, UpdateView):
    model = Attach
    form_class = AttachForm
    template_name = 'registrations/attach_form.html'
    success_url = reverse_lazy('attach-list')


class AttachDeleteView(LoginRequiredMixin, DeleteView):
    model = Attach
    template_name = 'registrations/attach_confirm_delete.html'
    success_url = reverse_lazy('attach-list')


# ============================================================
# AccountAttach Views
# ============================================================

class AccountAttachListView(LoginRequiredMixin, ListView):
    model = AccountAttach
    template_name = 'registrations/accountattach_list.html'
    context_object_name = 'account_attaches'
    paginate_by = 20

    def get_queryset(self):
        queryset = AccountAttach.objects.select_related('account', 'attach').all()
        account = self.request.GET.get('account')
        if account:
            queryset = queryset.filter(account_id=account)
        return queryset


class AccountAttachDetailView(LoginRequiredMixin, DetailView):
    model = AccountAttach
    template_name = 'registrations/accountattach_detail.html'
    context_object_name = 'account_attach'

    def get_queryset(self):
        return AccountAttach.objects.select_related('account', 'attach')


class AccountAttachCreateView(LoginRequiredMixin, CreateView):
    model = AccountAttach
    form_class = AccountAttachForm
    template_name = 'registrations/accountattach_form.html'
    success_url = reverse_lazy('accountattach-list')


class AccountAttachUpdateView(LoginRequiredMixin, UpdateView):
    model = AccountAttach
    form_class = AccountAttachForm
    template_name = 'registrations/accountattach_form.html'
    success_url = reverse_lazy('accountattach-list')


class AccountAttachDeleteView(LoginRequiredMixin, DeleteView):
    model = AccountAttach
    template_name = 'registrations/accountattach_confirm_delete.html'
    success_url = reverse_lazy('accountattach-list')


# ============================================================
# AccountCondition Views
# ============================================================

class AccountConditionListView(LoginRequiredMixin, ListView):
    model = AccountCondition
    template_name = 'registrations/accountcondition_list.html'
    context_object_name = 'account_conditions'
    paginate_by = 20

    def get_queryset(self):
        queryset = AccountCondition.objects.select_related('account', 'person').all()
        account = self.request.GET.get('account')
        if account:
            queryset = queryset.filter(account_id=account)
        fulfilled = self.request.GET.get('fulfilled')
        if fulfilled is not None:
            queryset = queryset.filter(fulfilled=fulfilled.lower() == 'true')
        return queryset


class AccountConditionDetailView(LoginRequiredMixin, DetailView):
    model = AccountCondition
    template_name = 'registrations/accountcondition_detail.html'
    context_object_name = 'account_condition'

    def get_queryset(self):
        return AccountCondition.objects.select_related('account', 'person')


class AccountConditionCreateView(LoginRequiredMixin, CreateView):
    model = AccountCondition
    form_class = AccountConditionForm
    template_name = 'registrations/accountcondition_form.html'
    success_url = reverse_lazy('accountcondition-list')

    def form_valid(self, form):
        form.instance.person = self.request.user
        return super().form_valid(form)


class AccountConditionUpdateView(LoginRequiredMixin, UpdateView):
    model = AccountCondition
    form_class = AccountConditionForm
    template_name = 'registrations/accountcondition_form.html'
    success_url = reverse_lazy('accountcondition-list')

    def form_valid(self, form):
        form.instance.person = self.request.user
        return super().form_valid(form)


class AccountConditionDeleteView(LoginRequiredMixin, DeleteView):
    model = AccountCondition
    template_name = 'registrations/accountcondition_confirm_delete.html'
    success_url = reverse_lazy('accountcondition-list')


# ============================================================
# AccountNote Views
# ============================================================

class AccountNoteListView(LoginRequiredMixin, ListView):
    model = AccountNote
    template_name = 'registrations/accountnote_list.html'
    context_object_name = 'account_notes'
    paginate_by = 20

    def get_queryset(self):
        queryset = AccountNote.objects.select_related('account', 'person').all()
        account = self.request.GET.get('account')
        if account:
            queryset = queryset.filter(account_id=account)
        return queryset


class AccountNoteDetailView(LoginRequiredMixin, DetailView):
    model = AccountNote
    template_name = 'registrations/accountnote_detail.html'
    context_object_name = 'account_note'

    def get_queryset(self):
        return AccountNote.objects.select_related('account', 'person')


class AccountNoteCreateView(LoginRequiredMixin, CreateView):
    model = AccountNote
    form_class = AccountNoteForm
    template_name = 'registrations/accountnote_form.html'
    success_url = reverse_lazy('accountnote-list')

    def form_valid(self, form):
        form.instance.person = self.request.user
        return super().form_valid(form)


class AccountNoteUpdateView(LoginRequiredMixin, UpdateView):
    model = AccountNote
    form_class = AccountNoteForm
    template_name = 'registrations/accountnote_form.html'
    success_url = reverse_lazy('accountnote-list')

    def form_valid(self, form):
        form.instance.person = self.request.user
        return super().form_valid(form)


class AccountNoteDeleteView(LoginRequiredMixin, DeleteView):
    model = AccountNote
    template_name = 'registrations/accountnote_confirm_delete.html'
    success_url = reverse_lazy('accountnote-list')
