import logging
from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from accounts.mixins import BranchPermissionMixin, ExecutiveOnlyMixin
from core.models import Branch
from courses.models import Course
from offers.models import StudentOffer
from students.models import Contact, Student
from . import services
from .forms import PermitForm, PermitTemplateForm
from .models import Permit, PermitTemplate

logger = logging.getLogger(__name__)


def _get_permit(request, pk, perm):
    permit = get_object_or_404(Permit.objects.select_related('student__contact', 'branch', 'course'), pk=pk)
    if not request.user.has_perm(perm, branch=permit.branch):
        raise PermissionDenied('غير مسموح لك دخول هنا')
    return permit


def _status_filter(qs, status):
    today = timezone.localdate()
    if status == 'active':
        return qs.filter(status=Permit.STATUS_ACTIVE, expiry_date__gte=today)
    if status == 'expired':
        return qs.filter(Q(status=Permit.STATUS_EXPIRED) | Q(status=Permit.STATUS_ACTIVE, expiry_date__lt=today))
    if status == 'cancelled':
        return qs.filter(status=Permit.STATUS_CANCELLED)
    return qs


class PermitListView(BranchPermissionMixin, ListView):
    model = Permit
    required_perm = 'view_permit'
    branch_field = 'branch'
    template_name = 'permits/permit_list.html'
    context_object_name = 'permits'
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset().select_related('student__contact', 'branch', 'course', 'issued_by')
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(number__icontains=q) | Q(program_name__icontains=q)
                | Q(student__contact__first_name__icontains=q) | Q(student__contact__forth_name__icontains=q)
                | Q(student__contact__identity_number__icontains=q) | Q(student__contact__mobile__icontains=q)
            )
        qs = _status_filter(qs, self.request.GET.get('status', ''))
        if self.request.GET.get('branch', '').isdigit():
            qs = qs.filter(branch_id=self.request.GET['branch'])
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        base = BranchPermissionMixin.get_queryset(self)
        ctx['counts'] = {key: _status_filter(base, key).count() for key in ('active', 'expired', 'cancelled')}
        ctx['branches'] = self.request.user.get_branches_for_perm('view_permit')
        ctx['can_add'] = self.request.user.has_perm_on_any_branch('add_permit')
        if ctx['can_add']:
            from .models import ReferralCode
            code = ReferralCode.for_person(self.request.user).code
            ctx['referral_link'] = self.request.build_absolute_uri(reverse('portal-ref', args=[code]))
        ctx['portal_link'] = self.request.build_absolute_uri(reverse('portal'))
        return ctx


class PermitCreateView(BranchPermissionMixin, CreateView):
    model = Permit
    form_class = PermitForm
    required_perm = 'add_permit'
    template_name = 'permits/permit_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_initial(self):
        """جاي من عرض أو من صفحة طالب: نملا الطالب والتخصص."""
        initial = super().get_initial()
        offer = self.get_offer()
        if offer:
            if offer.course_id:
                initial['course'] = offer.course_id
            recipient = offer.recipients.filter(student__isnull=False).first()
            if recipient:
                initial['student'] = recipient.student_id
        student = Student.objects.filter(slug=self.request.GET.get('student') or None).first()
        if student:
            initial['student'] = student.pk
        return initial

    def get_offer(self):
        slug = self.request.POST.get('offer') or self.request.GET.get('offer')
        offer = StudentOffer.objects.filter(slug=slug).first() if slug else None
        if offer and self.request.user.has_perm('view_studentoffer', branch=offer.branch):
            return offer
        return None

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['offer'] = self.get_offer()
        return ctx

    def form_valid(self, form):
        form.instance.offer = self.get_offer()
        response = super().form_valid(form)
        permit = self.object
        messages.success(self.request, f'تم إصدار المشهد رقم {permit.number}.')
        if self.request.POST.get('send_whatsapp'):
            _send_to_student_whatsapp(self.request, permit)
        return response

    def get_success_url(self):
        return reverse('permit-detail', args=[self.object.pk])


class PermitDetailView(BranchPermissionMixin, DetailView):
    model = Permit
    required_perm = 'view_permit'
    branch_field = 'branch'
    template_name = 'permits/permit_detail.html'
    context_object_name = 'permit'

    def get_queryset(self):
        return super().get_queryset().select_related('student__contact', 'branch', 'course', 'issued_by', 'offer')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user, branch = self.request.user, self.object.branch
        ctx['can_send'] = user.has_perm('add_permit', branch=branch)
        ctx['can_cancel'] = user.has_perm('change_permit', branch=branch) and self.object.status != Permit.STATUS_CANCELLED
        ctx['other_permits'] = (Permit.objects.filter(student=self.object.student).exclude(pk=self.object.pk)
                                .select_related('branch'))
        return ctx


@login_required
def permit_pdf(request, pk):
    permit = _get_permit(request, pk, 'view_permit')
    try:
        pdf = services.build_pdf(permit)
    except Exception as exc:
        logger.exception('Permit PDF failed')
        messages.error(request, f'تعذّر إنشاء ملف الـ PDF: {exc}')
        return redirect('permit-detail', pk=pk)
    response = HttpResponse(pdf, content_type='application/pdf')
    disposition = 'attachment' if request.GET.get('download') else 'inline'
    response['Content-Disposition'] = f'{disposition}; filename="{services.pdf_filename(permit)}"'
    return response


def _send_to_student_whatsapp(request, permit):
    phone = permit.student.contact.mobile
    if not phone:
        messages.warning(request, 'الطالب مالوش رقم جوال مسجل، فالمشهد ما اتبعتش واتساب.')
        return
    try:
        result = services.send_whatsapp(permit, phone)
    except Exception as exc:
        logger.exception('Permit WhatsApp failed')
        result = {'success': False, 'error': str(exc)}
    if result.get('success'):
        messages.success(request, f'اتبعت المشهد واتساب للطالب على {phone}.')
    else:
        messages.error(request, f'فشل إرسال الواتساب: {result.get("error", "خطأ غير معروف")}')


@require_POST
@login_required
def permit_send(request, pk):
    permit = _get_permit(request, pk, 'add_permit')
    channel = request.POST.get('channel')
    if channel == 'whatsapp':
        _send_to_student_whatsapp(request, permit)
    elif channel == 'me':
        phone = request.user.mobile or request.user.phone
        if not phone:
            messages.error(request, 'مفيش رقم جوال في حسابك. ضيفه من الملف الشخصي الأول.')
        else:
            try:
                result = services.send_whatsapp(permit, phone, title='📄 نسخة من مشهد')
            except Exception as exc:
                result = {'success': False, 'error': str(exc)}
            if result.get('success'):
                messages.success(request, 'اتبعتلك نسخة من المشهد على واتسابك.')
            else:
                messages.error(request, f'فشل إرسال الواتساب: {result.get("error", "خطأ غير معروف")}')
    elif channel == 'email':
        email = request.POST.get('email', '').strip()
        if not email:
            messages.error(request, 'اكتب الإيميل اللي هيتبعت عليه المشهد.')
        else:
            try:
                services.send_email(permit, email, site_url=request.build_absolute_uri('/').rstrip('/'))
                messages.success(request, f'اتبعت المشهد على {email}.')
            except Exception as exc:
                logger.exception('Permit email failed')
                messages.error(request, f'فشل إرسال الإيميل: {exc}')
    else:
        messages.error(request, 'طريقة إرسال مش معروفة.')
    return redirect('permit-detail', pk=pk)


@require_POST
@login_required
def permit_cancel(request, pk):
    permit = _get_permit(request, pk, 'change_permit')
    permit.status = Permit.STATUS_CANCELLED
    note = request.POST.get('reason', '').strip()
    if note:
        permit.notes = (permit.notes + '\n' if permit.notes else '') + f'سبب الإلغاء: {note}'
    permit.save(update_fields=['status', 'notes', 'updated_at'])
    messages.success(request, f'تم إلغاء المشهد {permit.number}. الطالب يقدر ياخد مشهد من فرع تاني دلوقتي.')
    return redirect('permit-detail', pk=pk)


# ---------------------------------------------------------------- القوالب (مدير النظام بس)

class PermitTemplateListView(LoginRequiredMixin, ExecutiveOnlyMixin, ListView):
    model = PermitTemplate
    template_name = 'permits/template_list.html'
    context_object_name = 'templates'

    def get_queryset(self):
        return super().get_queryset().select_related('branch')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['branches_without'] = Branch.objects.filter(permit_template__isnull=True)
        return ctx


class PermitTemplateCreateView(LoginRequiredMixin, ExecutiveOnlyMixin, CreateView):
    model = PermitTemplate
    form_class = PermitTemplateForm
    template_name = 'permits/template_form.html'
    success_url = reverse_lazy('permittemplate-list')

    def get_initial(self):
        return {'branch': self.request.GET.get('branch')}

    def form_valid(self, form):
        messages.success(self.request, 'تم حفظ القالب.')
        return super().form_valid(form)


class PermitTemplateUpdateView(LoginRequiredMixin, ExecutiveOnlyMixin, UpdateView):
    model = PermitTemplate
    form_class = PermitTemplateForm
    template_name = 'permits/template_form.html'
    success_url = reverse_lazy('permittemplate-list')

    def form_valid(self, form):
        messages.success(self.request, 'تم تحديث القالب.')
        return super().form_valid(form)


def _sample_permit(branch):
    """مشهد تجريبي (مش متسجل) عشان معاينة القالب."""
    contact = Contact(first_name='محمد', second_name='أحمد', third_name='عبدالله', forth_name='العتيبي',
                      identity_number='1012345678', mobile='966500000000')
    student = Student(contact=contact, branch=branch)
    course = Course.objects.filter(Q(branch=branch) | Q(branch__isnull=True)).first()
    return Permit(number=f'PERM-{date.today().year}-000000', student=student, branch=branch, course=course,
                  program_name=course.get_display_name() if course else 'دبلوم إدارة الموارد البشرية',
                  issue_date=timezone.localdate(), expiry_date=timezone.localdate(), study_mode='offline')


@login_required
def permit_template_preview(request, pk):
    if not request.user.is_executive():
        raise PermissionDenied('غير مسموح لك دخول هنا')
    template = get_object_or_404(PermitTemplate, pk=pk)
    permit = Permit.objects.filter(branch=template.branch).first() or _sample_permit(template.branch)
    try:
        pdf = services.build_pdf(permit, strict=True)
    except Exception as exc:
        messages.error(request, f'القالب فيه غلط، والمشاهد بتطلع بالقالب الافتراضي لحد ما يتصلح: '
                                f'{type(exc).__name__}: {exc}')
        return redirect('permittemplate-update', pk=pk)
    return HttpResponse(pdf, content_type='application/pdf')
