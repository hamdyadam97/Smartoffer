import re

from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from accounts.models import PasswordResetCode, Person


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class LoginAndResetTests(TestCase):
    def setUp(self):
        self.person = Person.objects.create_user(email='ali@example.com', password='Old-pass-123', first_name='علي')

    # ---------------------------------------------------------- الدخول
    def test_wrong_password_shows_clear_error_and_keeps_email(self):
        response = self.client.post(reverse('login'), {'username': 'ali@example.com', 'password': 'wrong'})
        self.assertContains(response, 'الإيميل أو كلمة المرور غلط')
        self.assertContains(response, 'alert alert-danger')
        self.assertContains(response, 'value="ali@example.com"')

    def test_unknown_email_same_message(self):
        response = self.client.post(reverse('login'), {'username': 'nobody@example.com', 'password': 'x'})
        self.assertContains(response, 'الإيميل أو كلمة المرور غلط')

    def test_inactive_account_message(self):
        self.person.is_active = False
        self.person.save()
        response = self.client.post(reverse('login'), {'username': 'ali@example.com', 'password': 'Old-pass-123'})
        self.assertContains(response, 'الحساب ده موقوف')

    def test_login_ok_and_next(self):
        response = self.client.post(reverse('login') + '?next=/permits/', {'username': 'ALI@example.com',
                                                                          'password': 'Old-pass-123'})
        self.assertRedirects(response, '/permits/', fetch_redirect_response=False)
        response = self.client.post(reverse('login') + '?next=//evil.com', {'username': 'ali@example.com',
                                                                            'password': 'Old-pass-123'})
        self.assertRedirects(response, reverse('dashboard'), fetch_redirect_response=False)

    def test_error_messages_use_bootstrap_danger(self):
        from django.contrib.messages import constants
        from django.conf import settings
        self.assertEqual(settings.MESSAGE_TAGS[constants.ERROR], 'danger')

    # ---------------------------------------------------------- نسيت كلمة المرور
    def request_code(self, email='ali@example.com'):
        return self.client.post(reverse('password-reset'), {'email': email}, follow=True)

    def sent_code(self):
        return re.search(r'\b(\d{6})\b', mail.outbox[-1].body).group(1)

    def test_full_reset_flow(self):
        response = self.request_code()
        self.assertContains(response, 'هيوصلك كود')
        self.assertEqual(mail.outbox[-1].to, ['ali@example.com'])
        response = self.client.post(reverse('password-reset-verify'), {
            'code': self.sent_code(), 'password1': 'New-pass-456!', 'password2': 'New-pass-456!'}, follow=True)
        self.assertContains(response, 'اتغيرت كلمة المرور')
        self.person.refresh_from_db()
        self.assertTrue(self.person.check_password('New-pass-456!'))
        self.assertFalse(PasswordResetCode.objects.filter(used=False).exists())

    def test_unknown_email_gets_same_answer_without_email(self):
        response = self.request_code('nobody@example.com')
        self.assertContains(response, 'هيوصلك كود')
        self.assertEqual(len(mail.outbox), 0)

    def test_wrong_code_counts_attempts(self):
        self.request_code()
        code = self.sent_code()
        wrong = '000000' if code != '000000' else '111111'
        for left in (4, 3, 2, 1):
            response = self.client.post(reverse('password-reset-verify'), {
                'code': wrong, 'password1': 'New-pass-456!', 'password2': 'New-pass-456!'})
            self.assertContains(response, f'فاضلك {left} محاولات')
        self.client.post(reverse('password-reset-verify'), {'code': wrong, 'password1': 'New-pass-456!',
                                                             'password2': 'New-pass-456!'})
        # حتى الكود الصح مابقاش ينفع
        response = self.client.post(reverse('password-reset-verify'), {
            'code': code, 'password1': 'New-pass-456!', 'password2': 'New-pass-456!'})
        self.assertContains(response, 'اطلب كود جديد')
        self.person.refresh_from_db()
        self.assertTrue(self.person.check_password('Old-pass-123'))

    def test_new_code_cancels_old_and_limit(self):
        self.request_code()
        old = self.sent_code()
        self.request_code()
        response = self.client.post(reverse('password-reset-verify'), {
            'code': old, 'password1': 'New-pass-456!', 'password2': 'New-pass-456!'})
        if old != self.sent_code():
            self.assertContains(response, 'اطلب كود جديد')
        self.request_code()
        response = self.request_code()
        self.assertContains(response, 'اتبعت أكتر من كود')
        self.assertEqual(len(mail.outbox), 3)

    def test_verify_without_request_redirects(self):
        self.assertRedirects(self.client.get(reverse('password-reset-verify')), reverse('password-reset'))

    @override_settings(EMAIL_BACKEND='accounts.test_login_reset.BrokenBackend')
    def test_email_failure_is_reported(self):
        response = self.request_code()
        self.assertContains(response, 'مشكلة في إرسال الإيميل')
        self.assertFalse(PasswordResetCode.objects.exists())

    def test_login_page_links_to_reset(self):
        self.assertContains(self.client.get(reverse('login')), reverse('password-reset'))


class BrokenBackend:
    def __init__(self, *args, **kwargs):
        pass

    def send_messages(self, messages):
        raise OSError('smtp down')
