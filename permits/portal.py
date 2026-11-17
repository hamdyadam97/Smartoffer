"""البوابة العامة: الطالب بيطلّع مشهده بنفسه من غير تسجيل دخول (/certificate/ أو /certificate/<كود الموظف>/)."""
import logging
import re

from django import forms
from django.core import signing
from django.core.cache import cache
from django.db import transaction
from django.db.models import Q
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from core.models import Branch
from courses.models import Course
from students.models import Contact, Student
from . import services
from .models import Permit, PermitTemplate, ReferralCode

logger = logging.getLogger(__name__)

TOKEN_SALT = 'permits.portal'
TOKEN_MAX_AGE = 60 * 60 * 24 * 30  # لينك التحميل شغال 30 يوم
ISSUE_LIMIT_PER_HOUR = 20


def portal_branches():
    """الفروع اللي بتطلّع مشاهد (ليها قالب مشهد). لو مفيش قوالب خالص: كل الفروع."""
    with_template = Branch.objects.filter(permit_template__isnull=False)
    return (with_template if with_template.exists() else Branch.objects.all()).order_by('code')


def branch_courses(branch):
    return Course.objects.filter(Q(branch=branch) | Q(branch__isnull=True)).order_by('program_type', 'name')


def referral_for(code):
    if not code:
        return None
    return ReferralCode.objects.select_related('person__branch').filter(
        code__iexact=code, person__is_active=True).first()


def digits(value):
    return re.sub(r'\D', '', str(value or ''))


def permit_token(permit):
    return signing.dumps(permit.pk, salt=TOKEN_SALT)


def permit_from_token(token):
    try:
        pk = signing.loads(token, salt=TOKEN_SALT, max_age=TOKEN_MAX_AGE)
    except signing.BadSignature:
        raise Http404
    permit = Permit.objects.select_related('student__contact', 'branch', 'course').filter(pk=pk).first()
    if permit is None:
        raise Http404
    return permit


class PortalForm(forms.Form):
    branch = forms.ModelChoiceField(queryset=Branch.objects.none(), label='المعهد / الفرع', empty_label='اختار الفرع')
    course = forms.ModelChoiceField(queryset=Course.objects.none(), label='الدبلوم / الدورة', empty_label='اختار البرنامج')
    study_mode = forms.ChoiceField(choices=[('', 'بدون تحديد')] + Permit.STUDY_MODE_CHOICES, required=False,
                                   label='طريقة الدراسة', widget=forms.Select(attrs={'class': 'form-select'}))
    national_id = forms.CharField(max_length=10, label='رقم الهوية / الإقامة')
    full_name = forms.CharField(max_length=255, label='الاسم الرباعي')
    phone = forms.CharField(max_length=20, label='رقم الجوال')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['branch'].queryset = portal_branches()
        branch_id = self.data.get('branch') or self.initial.get('branch')
        branch = Branch.objects.filter(pk=branch_id).first() if str(branch_id or '').isdigit() else None
        self.fields['course'].queryset = branch_courses(branch) if branch else Course.objects.none()
        self.fields['course'].label_from_instance = lambda c: c.get_display_name()

    def clean_national_id(self):
        value = digits(self.cleaned_data['national_id'])
        if not re.fullmatch(r'[12]\d{9}', value):
            raise forms.ValidationError('رقم الهوية لازم يبقى 10 أرقام ويبدأ بـ 1 أو 2.')
        return value

    def clean_phone(self):
        value = digits(self.cleaned_data['phone'])
        if len(value) < 9:
            raise forms.ValidationError('رقم الجوال مش صحيح.')
        return value

    def clean_full_name(self):
        value = re.sub(r'\s+', ' ', self.cleaned_data['full_name']).strip()
        if len(value.split()) < 2:
            raise forms.ValidationError('اكتب الاسم كامل (الاسم الأول واسم العائلة على الأقل).')
        return value


class PortalError(Exception):
    pass


def _student_for(data, branch):
    """الطالب برقم الهوية. لو مسجل لازم الجوال يطابق (عشان محدش يطلّع مشهد باسم حد تاني)."""
    students = list(Student.objects.select_related('contact').filter(contact__identity_number=data['national_id']))
    if students:
        phone = data['phone'][-9:]
        mobiles = [digits(s.contact.mobile)[-9:] for s in students if s.contact.mobile]
        if mobiles and phone not in mobiles:
            raise PortalError('رقم الهوية ده مسجل عندنا برقم جوال مختلف. تواصل مع المعهد لتحديث بياناتك.')
        student = next((s for s in students if s.branch_id == branch.pk), students[0])
        if not mobiles:  # مسجل من غير جوال: نسجّل الجوال اللي كتبه
            student.contact.mobile = data['phone']
            student.contact.save(update_fields=['mobile'])
        return student
    parts = data['full_name'].split()
    contact = Contact.objects.create(
        first_name=parts[0], second_name=parts[1] if len(parts) > 2 else '',
        third_name=' '.join(parts[2:-1]) if len(parts) > 3 else '', forth_name=parts[-1],
        identity_number=data['national_id'], mobile=data['phone'],
    )
    return Student.objects.create(contact=contact, branch=branch)


def issue_public_permit(data, referral=None):
    """بيرجّع (المشهد، اتعمل جديد؟). نفس قواعد الموظف: مشهد نشط في فرع تاني بيمنع، ونفس الفرع بيرجّع القديم."""
    branch, course = data['branch'], data['course']
    with transaction.atomic():
        student = _student_for(data, branch)
        existing = services.find_existing_permit(student, branch)
        if existing:
            return existing, False
        error = services.issue_error(student, branch)
        if error:
            raise PortalError(error.replace('لازم تتواصل', 'برجاء التواصل'))
        permit = Permit.objects.create(
            student=student, branch=branch, course=course, study_mode=data.get('study_mode') or '',
            issued_from_public=True, referral_employee=referral.person if referral else None,
            referral_code=referral.code if referral else '',
        )
    if referral and (referral.person.mobile or referral.person.phone):
        try:
            services.send_whatsapp(permit, referral.person.mobile or referral.person.phone,
                                   title='🎓 مشهد جديد عن طريق رابطك')
        except Exception:
            logger.exception('Referral WhatsApp failed for permit %s', permit.number)
    return permit, True


def _client_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
    return forwarded.split(',')[0].strip() or request.META.get('REMOTE_ADDR', '')


def _too_many(request):
    key = f'permit-portal:{_client_ip(request)}'
    count = cache.get(key, 0)
    if count >= ISSUE_LIMIT_PER_HOUR:
        return True
    cache.set(key, count + 1, 60 * 60)
    return False


# ---------------------------------------------------------------- views

def landing(request, ref_code=None):
    ref_code = ref_code or request.GET.get('ref', '')
    referral = referral_for(ref_code)
    initial = {}
    if referral and referral.person.branch and portal_branches().filter(pk=referral.person.branch_id).exists():
        initial['branch'] = referral.person.branch_id

    if request.method == 'POST':
        form = PortalForm(request.POST, initial=initial)
        if form.is_valid():
            if _too_many(request):
                form.add_error(None, 'طلبات كتير من نفس الجهاز. حاول تاني بعد شوية.')
            else:
                try:
                    permit, created = issue_public_permit(form.cleaned_data, referral)
                    return redirect('portal-result', token=permit_token(permit))
                except PortalError as exc:
                    form.add_error(None, str(exc))
    else:
        form = PortalForm(initial=initial)
    return render(request, 'permits/portal/landing.html', {
        'form': form, 'ref_code': referral.code if referral else '', 'branch_locked': bool(initial.get('branch')),
    })


def programs_json(request):
    branch_id = request.GET.get('branch', '')
    branch = portal_branches().filter(pk=branch_id).first() if branch_id.isdigit() else None
    courses = branch_courses(branch) if branch else []
    return JsonResponse({'programs': [{'id': c.pk, 'name': c.get_display_name()} for c in courses]})


def result(request, token):
    permit = permit_from_token(token)
    return render(request, 'permits/portal/result.html', {'permit': permit, 'token': token})


def download(request, token):
    permit = permit_from_token(token)
    response = HttpResponse(services.build_pdf(permit), content_type='application/pdf')
    disposition = 'attachment' if request.GET.get('download') else 'inline'
    response['Content-Disposition'] = f'{disposition}; filename="{services.pdf_filename(permit)}"'
    return response


@require_POST
def send_email(request, token):
    permit = permit_from_token(token)
    email = request.POST.get('email', '').strip()
    try:
        forms.EmailField().clean(email)
    except forms.ValidationError:
        return render(request, 'permits/portal/result.html',
                      {'permit': permit, 'token': token, 'email_error': 'الإيميل مش صحيح.'})
    key = f'permit-portal-email:{permit.pk}'
    if cache.get(key, 0) >= 3:
        return render(request, 'permits/portal/result.html',
                      {'permit': permit, 'token': token, 'email_error': 'اتبعت أكتر من مرة. حاول بكرة.'})
    cache.set(key, cache.get(key, 0) + 1, 60 * 60 * 24)
    try:
        services.send_email(permit, email, site_url=request.build_absolute_uri('/').rstrip('/'))
        sent = True
    except Exception:
        logger.exception('Portal email failed for permit %s', permit.number)
        sent = False
    return render(request, 'permits/portal/result.html', {
        'permit': permit, 'token': token, 'email_sent': email if sent else '',
        'email_error': '' if sent else 'حصلت مشكلة في الإرسال. حمّل المشهد من الزرار بدل كده.',
    })
