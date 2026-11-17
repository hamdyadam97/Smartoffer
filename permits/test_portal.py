from unittest import mock

from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import Person
from core.models import Branch, Company
from courses.models import Course
from students.models import Contact, Student
from .models import Permit, PermitTemplate, ReferralCode
from .portal import permit_token


class PortalTests(TestCase):
    def setUp(self):
        cache.clear()
        company = Company.objects.create(name='Co')
        self.riyadh = Branch.objects.create(company=company, code=9, name='الفاو الرياض')
        self.hafr = Branch.objects.create(company=company, code=15, name='الفاو حفر الباطن')
        self.no_permits = Branch.objects.create(company=company, code=1, name='الأهلي عرعر')
        PermitTemplate.objects.create(branch=self.riyadh)
        PermitTemplate.objects.create(branch=self.hafr)
        self.course = Course.objects.create(program_type='دبلوم', name='موارد بشرية', branch=None)
        self.hafr_course = Course.objects.create(program_type='دورة', name='تصوير', branch=self.hafr)
        self.web = Client()  # من غير تسجيل دخول

    def data(self, **extra):
        return {'branch': self.riyadh.pk, 'course': self.course.pk, 'national_id': '1012345678',
                'full_name': 'محمد أحمد العتيبي', 'phone': '0501234567', **extra}

    def test_landing_is_public_and_lists_permit_branches_only(self):
        response = self.web.get(reverse('portal'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'الفاو الرياض')
        self.assertNotContains(response, 'الأهلي عرعر')

    def test_programs_json(self):
        names = [p['name'] for p in self.web.get(reverse('portal-programs'), {'branch': self.hafr.pk}).json()['programs']]
        self.assertEqual(set(names), {'دبلوم موارد بشرية', 'دورة تصوير'})
        names = [p['name'] for p in self.web.get(reverse('portal-programs'), {'branch': self.riyadh.pk}).json()['programs']]
        self.assertEqual(names, ['دبلوم موارد بشرية'])

    def test_new_student_gets_permit_and_pdf(self):
        response = self.web.post(reverse('portal'), self.data(), follow=True)
        permit = Permit.objects.get()
        self.assertTrue(permit.issued_from_public)
        self.assertEqual((permit.branch, permit.course), (self.riyadh, self.course))
        self.assertEqual(permit.student.contact.identity_number, '1012345678')
        self.assertContains(response, permit.number)
        pdf = self.web.get(reverse('portal-download', args=[permit_token(permit)]))
        self.assertTrue(pdf.content.startswith(b'%PDF'))

    def test_same_branch_returns_existing_permit(self):
        self.web.post(reverse('portal'), self.data())
        self.web.post(reverse('portal'), self.data())
        self.assertEqual(Permit.objects.count(), 1)

    def test_other_branch_active_permit_blocks(self):
        self.web.post(reverse('portal'), self.data())
        response = self.web.post(reverse('portal'), self.data(branch=self.hafr.pk, course=self.hafr_course.pk))
        self.assertContains(response, 'برجاء التواصل')
        self.assertEqual(Permit.objects.count(), 1)

    def test_existing_student_needs_matching_phone(self):
        Student.objects.create(contact=Contact.objects.create(
            first_name='سارة', forth_name='علي', identity_number='1012345678', mobile='966509999999'), branch=self.riyadh)
        response = self.web.post(reverse('portal'), self.data())
        self.assertContains(response, 'برقم جوال مختلف')
        self.assertFalse(Permit.objects.exists())
        self.web.post(reverse('portal'), self.data(phone='0509999999'))
        self.assertEqual(Permit.objects.get().student.contact.first_name, 'سارة')
        self.assertEqual(Student.objects.count(), 1)

    def test_course_of_other_branch_rejected(self):
        response = self.web.post(reverse('portal'), self.data(course=self.hafr_course.pk))
        self.assertIn('course', response.context['form'].errors)

    def test_invalid_national_id(self):
        response = self.web.post(reverse('portal'), self.data(national_id='12345'))
        self.assertContains(response, '10 أرقام')

    @mock.patch('permits.portal.services.send_whatsapp', return_value={'success': True})
    def test_referral_link_credits_employee_and_locks_branch(self, send):
        employee = Person.objects.create_user(email='e@example.com', password='x', branch=self.hafr, mobile='0551112222')
        code = ReferralCode.for_person(employee).code
        page = self.web.get(reverse('portal-ref', args=[code.lower()]))
        self.assertContains(page, 'type="hidden" name="branch" id="id_branch" value="%d"' % self.hafr.pk)
        self.web.post(reverse('portal-ref', args=[code]), self.data(branch=self.hafr.pk, course=self.hafr_course.pk))
        permit = Permit.objects.get()
        self.assertEqual((permit.referral_employee, permit.referral_code), (employee, code))
        send.assert_called_once()
        self.assertEqual(send.call_args.args[1], '0551112222')

    def test_unknown_referral_code_still_works(self):
        self.web.post(reverse('portal-ref', args=['NOPE']), self.data())
        self.assertIsNone(Permit.objects.get().referral_employee)

    def test_bad_token_404(self):
        self.assertEqual(self.web.get(reverse('portal-result', args=['bad'])).status_code, 404)

    def test_email_send_and_limit(self):
        self.web.post(reverse('portal'), self.data())
        token = permit_token(Permit.objects.get())
        with mock.patch('permits.portal.services.send_email') as send:
            response = self.web.post(reverse('portal-email', args=[token]), {'email': 'a@example.com'})
            self.assertContains(response, 'اتبعت المشهد على a@example.com')
            for _ in range(3):
                response = self.web.post(reverse('portal-email', args=[token]), {'email': 'a@example.com'})
            self.assertContains(response, 'اتبعت أكتر من مرة')
            self.assertEqual(send.call_count, 3)

    def test_staff_sees_referral_link(self):
        admin = Person.objects.create_user(email='admin@example.com', password='x', is_superuser=True)
        staff = Client()
        staff.force_login(admin)
        code = ReferralCode.for_person(admin).code
        self.assertContains(staff.get(reverse('permit-list')), f'/certificate/{code}/')
