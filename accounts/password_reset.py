"""نسيت كلمة المرور: الموظف بيكتب إيميله، بيوصله كود من 6 أرقام، بيكتبه مع كلمة المرور الجديدة."""
import logging
import secrets
from datetime import timedelta

from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.password_validation import validate_password
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.utils import timezone

from .models import PasswordResetCode, Person

logger = logging.getLogger(__name__)

SESSION_KEY = 'password_reset_email'
MAX_CODES_PER_WINDOW = 3


class RequestForm(forms.Form):
    email = forms.EmailField(label='الإيميل', widget=forms.EmailInput(attrs={'class': 'form-control', 'dir': 'ltr', 'autofocus': True}))


class VerifyForm(forms.Form):
    code = forms.CharField(label='الكود اللي وصلك', max_length=6, widget=forms.TextInput(attrs={
        'class': 'form-control text-center fs-4', 'dir': 'ltr', 'inputmode': 'numeric', 'autocomplete': 'one-time-code',
        'autofocus': True}))
    password1 = forms.CharField(label='كلمة المرور الجديدة', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='اكتبها تاني', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password1') and cleaned.get('password1') != cleaned.get('password2'):
            self.add_error('password2', 'كلمتين المرور مش زي بعض.')
        return cleaned


def email_is_configured():
    """لو الإرسال على console/dummy يبقى الإيميل بيتطبع في اللوج بس ومش بيوصل لحد."""
    backend = settings.EMAIL_BACKEND.lower()
    return not ('console' in backend or 'dummy' in backend)


def _send_code(person):
    """بيعمل كود جديد ويبعته. بيرجّع رسالة غلط أو None."""
    if not email_is_configured():
        return ('إرسال الإيميلات مش متظبط على السيرفر، فالكود مش هيوصل. '
                'كلّم الإدارة عشان تغيّرلك كلمة المرور.')
    window = timezone.now() - timedelta(minutes=PasswordResetCode.VALID_MINUTES)
    if person.reset_codes.filter(created_at__gte=window).count() >= MAX_CODES_PER_WINDOW:
        return 'اتبعت أكتر من كود في آخر ربع ساعة. استخدم آخر كود وصلك أو استنى شوية.'
    code = f'{secrets.randbelow(10 ** 6):06d}'
    person.reset_codes.filter(used=False).update(used=True)  # الكود الجديد بيلغي القديم
    reset = PasswordResetCode.objects.create(person=person, code_hash=make_password(code))
    try:
        send_mail(
            subject='كود تغيير كلمة المرور - Smart Offer',
            message=(f'مرحباً {person.get_short_name()}،\n\n'
                     f'كود تغيير كلمة المرور: {code}\n'
                     f'الكود صالح لمدة {PasswordResetCode.VALID_MINUTES} دقيقة.\n\n'
                     'لو انت ماطلبتش تغيير كلمة المرور تجاهل الرسالة دي.'),
            from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[person.email],
        )
    except Exception:
        logger.exception('Password reset email failed for %s', person.pk)
        reset.delete()
        return 'حصلت مشكلة في إرسال الإيميل. كلّم الإدارة عشان تغيّرلك كلمة المرور.'
    return None


def request_code(request):
    form = RequestForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email'].strip()
        person = Person.objects.filter(email__iexact=email).first()
        if person is None:
            form.add_error('email', 'الإيميل ده مش مسجل عندنا. اتأكد منه أو كلّم الإدارة.')
        elif not person.is_active:
            form.add_error('email', 'الحساب ده موقوف. كلّم الإدارة عشان تفعّله.')
        else:
            error = _send_code(person)
            if error:
                form.add_error(None, error)
            else:
                request.session[SESSION_KEY] = person.email
                messages.success(request, f'بعتنا كود من 6 أرقام على {person.email}. '
                                          'لو ماظهرش في الـ Inbox بص في الـ Spam.')
                return redirect('password-reset-verify')
    return render(request, 'registration/password_reset.html', {'form': form})


def verify_code(request):
    email = request.session.get(SESSION_KEY)
    if not email:
        return redirect('password-reset')
    form = VerifyForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        person = Person.objects.filter(email__iexact=email, is_active=True).first()
        reset = person.reset_codes.filter(used=False).first() if person else None
        if reset is None or not reset.is_valid:
            form.add_error('code', 'الكود خلص أو اتلغى. اطلب كود جديد.')
        elif not check_password(form.cleaned_data['code'].strip(), reset.code_hash):
            reset.attempts += 1
            reset.save(update_fields=['attempts'])
            left = PasswordResetCode.MAX_ATTEMPTS - reset.attempts
            form.add_error('code', f'الكود غلط. فاضلك {left} محاولات.' if left > 0 else 'الكود غلط كتير. اطلب كود جديد.')
        else:
            try:
                validate_password(form.cleaned_data['password1'], person)
            except forms.ValidationError as exc:
                form.add_error('password1', exc)
            else:
                person.set_password(form.cleaned_data['password1'])
                person.save(update_fields=['password'])
                person.reset_codes.update(used=True)
                request.session.pop(SESSION_KEY, None)
                messages.success(request, 'اتغيرت كلمة المرور. ادخل بالكلمة الجديدة.')
                return redirect('login')
    return render(request, 'registration/password_reset_verify.html', {'form': form, 'email': email})
