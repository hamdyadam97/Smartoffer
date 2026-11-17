from datetime import date, timedelta
from unittest import mock

from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import EmployeeRole, Permission, Person, Role
from core.models import Branch, Company
from courses.models import Course
from offers.models import OfferRecipient, StudentOffer
from students.models import Contact, Student
from .models import Permit, PermitTemplate
from .services import build_context, build_pdf, issue_error, render_html


def make_student(branch, first='محمد', last='العتيبي', national_id='1012345678', mobile='0501234567'):
    contact = Contact.objects.create(first_name=first, forth_name=last, identity_number=national_id, mobile=mobile)
    return Student.objects.create(contact=contact, branch=branch)


class PermitTestBase(TestCase):
    def setUp(self):
        company = Company.objects.create(name='Co')
        self.riyadh = Branch.objects.create(company=company, code=1, name='الرياض', licence_code='LIC-1')
        self.hafr = Branch.objects.create(company=company, code=2, name='حفر الباطن')
        self.course = Course.objects.create(program_type='دبلوم', name='موارد بشرية', branch=None,
                                            period='سنة', end_date=date.today() + timedelta(days=200))
        self.student = make_student(self.riyadh)
        self.admin = Person.objects.create_user(email='admin@example.com', password='x', is_superuser=True)
        self.client = Client()
        self.client.force_login(self.admin)

    def employee(self, branch, actions=('view', 'add', 'change'), email='e@example.com'):
        person = Person.objects.create_user(email=email, password='x', branch=branch)
        role = Role.objects.create(name=f'role-{email}')
        for action in actions:
            perm, _ = Permission.objects.get_or_create(
                codename=f'{action}_permit',
                defaults={'name': 'x', 'app_label': 'permits', 'model_name': 'permit', 'action': action})
            role.permissions.add(perm)
        EmployeeRole.objects.create(person=person, role=role, branch=branch)
        return person

    def issue(self, student=None, branch=None, **extra):
        return Permit.objects.create(student=student or self.student, branch=branch or self.riyadh,
                                     course=self.course, issued_by=self.admin, **extra)


class PermitModelTests(PermitTestBase):
    def test_number_program_and_expiry_are_filled(self):
        permit = self.issue()
        self.assertRegex(permit.number, rf'^PERM-{timezone.localdate().year}-\d{{6}}$')
        self.assertEqual(permit.program_name, 'دبلوم موارد بشرية')
        self.assertEqual(permit.expiry_date, self.course.end_date)

    def test_expiry_defaults_to_a_year_without_course_end(self):
        self.course.end_date = None
        self.course.save()
        permit = self.issue()
        self.assertEqual(permit.expiry_date, permit.issue_date + timedelta(days=365))

    def test_past_expiry_shows_as_expired(self):
        permit = self.issue(expiry_date=date.today() - timedelta(days=1))
        self.assertEqual(permit.status, 'active')
        self.assertEqual(permit.effective_status, 'expired')
        self.assertIsNone(issue_error(self.student, self.riyadh))


class IssueRuleTests(PermitTestBase):
    def test_active_permit_in_same_branch_blocks_duplicate(self):
        existing = self.issue()
        self.assertIn(existing.number, issue_error(self.student, self.riyadh))

    def test_active_permit_in_other_branch_blocks_by_national_id(self):
        """نفس الشخص متسجل طالب في فرعين: المشهد النشط في فرع بيمنع التاني."""
        self.issue()
        other = make_student(self.hafr, mobile='0559999999')  # نفس رقم الهوية
        error = issue_error(other, self.hafr)
        self.assertIn('الرياض', error)
        self.assertIn('لازم تتواصل', error)

    def test_cancelled_permit_does_not_block(self):
        self.issue(status=Permit.STATUS_CANCELLED)
        self.assertIsNone(issue_error(self.student, self.riyadh))


class PermitViewTests(PermitTestBase):
    @mock.patch('permits.views.services.send_whatsapp', return_value={'success': True})
    def test_create_and_send_whatsapp(self, send):
        response = self.client.post(reverse('permit-create'), {
            'student': self.student.pk, 'course': self.course.pk, 'study_mode': 'online', 'send_whatsapp': 'on',
        }, follow=True)
        permit = Permit.objects.get()
        self.assertRedirects(response, reverse('permit-detail', args=[permit.pk]))
        self.assertEqual((permit.branch, permit.issued_by, permit.study_mode), (self.riyadh, self.admin, 'online'))
        send.assert_called_once_with(permit, '0501234567')
        self.assertContains(response, 'اتبعت المشهد واتساب')

    def test_create_blocked_shows_message(self):
        self.issue()
        response = self.client.post(reverse('permit-create'), {'student': self.student.pk, 'course': self.course.pk})
        self.assertContains(response, 'مينفعش يتطلع مشهد مكرر')
        self.assertEqual(Permit.objects.count(), 1)

    def test_course_from_another_branch_rejected(self):
        hafr_course = Course.objects.create(program_type='دورة', name='تصوير', branch=self.hafr)
        response = self.client.post(reverse('permit-create'), {'student': self.student.pk, 'course': hafr_course.pk})
        self.assertContains(response, 'تبع فرع تاني')
        self.assertFalse(Permit.objects.exists())

    def test_create_from_offer_prefills_and_links(self):
        offer = StudentOffer.objects.create(title='عرض', content='x', branch=self.riyadh, course=self.course,
                                            created_by=self.admin)
        OfferRecipient.objects.create(offer=offer, student=self.student, channel='whatsapp')
        response = self.client.get(reverse('permit-create') + f'?offer={offer.slug}')
        self.assertEqual(response.context['form'].initial['student'], self.student.pk)
        self.assertEqual(response.context['form'].initial['course'], self.course.pk)
        self.client.post(reverse('permit-create'), {'offer': offer.slug, 'student': self.student.pk, 'course': self.course.pk})
        self.assertEqual(Permit.objects.get().offer, offer)
        self.assertContains(self.client.get(reverse('studentoffer-detail', args=[offer.slug])), 'إصدار مشهد')

    def test_cancel_allows_new_permit_elsewhere(self):
        permit = self.issue()
        self.client.post(reverse('permit-cancel', args=[permit.pk]), {'reason': 'نقل'})
        permit.refresh_from_db()
        self.assertEqual(permit.status, 'cancelled')
        self.assertIn('سبب الإلغاء: نقل', permit.notes)
        self.assertIsNone(issue_error(make_student(self.hafr, mobile='0551'), self.hafr))

    def test_list_search_and_student_page(self):
        permit = self.issue()
        response = self.client.get(reverse('permit-list'), {'q': '1012345678'})
        self.assertContains(response, permit.number)
        self.assertNotContains(self.client.get(reverse('permit-list'), {'status': 'cancelled'}), permit.number)
        self.assertContains(self.client.get(reverse('student-detail', args=[self.student.slug])), permit.number)

    def test_employee_scoped_to_own_branch(self):
        mine = self.issue()
        other = self.issue(student=make_student(self.hafr, national_id='1099999999', mobile='0552'), branch=self.hafr)
        employee = self.employee(self.riyadh)
        self.client.force_login(employee)
        response = self.client.get(reverse('permit-list'))
        self.assertContains(response, mine.number)
        self.assertNotContains(response, other.number)
        self.assertIn(self.client.get(reverse('permit-detail', args=[other.pk])).status_code, (403, 404))
        self.assertEqual(self.client.get(reverse('permit-pdf', args=[other.pk])).status_code, 403)
        self.assertEqual(self.client.post(reverse('permit-cancel', args=[other.pk])).status_code, 403)
        # مايقدرش يختار طالب من فرع تاني
        response = self.client.post(reverse('permit-create'), {'student': other.student.pk, 'course': self.course.pk})
        self.assertIn('student', response.context['form'].errors)

    def test_employee_without_permission_denied(self):
        self.client.force_login(self.employee(self.riyadh, actions=()))
        self.assertEqual(self.client.get(reverse('permit-list')).status_code, 403)
        self.assertEqual(self.client.get(reverse('permit-create')).status_code, 403)

    def test_templates_are_executive_only(self):
        self.client.force_login(self.employee(self.riyadh))
        self.assertEqual(self.client.get(reverse('permittemplate-list')).status_code, 403)


class PermitPdfTests(PermitTestBase):
    def test_default_pdf(self):
        permit = self.issue()
        html = render_html(permit)
        self.assertIn('محمد العتيبي', html)
        self.assertIn('1012345678', html)
        self.assertIn('LIC-1', html)
        response = self.client.get(reverse('permit-pdf', args=[permit.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content.startswith(b'%PDF'))
        response = self.client.get(reverse('permit-pdf', args=[permit.pk]) + '?download=1')
        self.assertIn('attachment', response['Content-Disposition'])

    def test_old_system_template_variables_work(self):
        """قوالب برنامج المشاهد القديم بتستخدم client / institute / program: لازم تشتغل زي ما هي."""
        PermitTemplate.objects.create(
            branch=self.riyadh, font_family='amiri',
            header_content='<h1>{{ institute.name }} - {{ institute.license_number }}</h1>',
            body_content='<p>{{ client.full_name }} / {{ client.national_id }} / {{ program.name }} / '
                         '{{ program.duration_months }} / {{ permission.permission_number }}{{ permit.number }}</p>'
                         '{% if institute.signature_image %}<img src="file://{{ institute.signature_image.path }}">{% endif %}',
            footer_content='{{ today }}',
        )
        permit = self.issue()
        html = render_html(permit)
        self.assertIn('الرياض - LIC-1', html)
        self.assertIn('محمد العتيبي / 1012345678 / دبلوم موارد بشرية / سنة /', html)
        self.assertIn(permit.number, html)
        self.assertIn("font-family: 'Amiri'", html)
        self.assertTrue(build_pdf(permit).startswith(b'%PDF'))

    def test_old_afaq_template_with_hijri_city_and_background(self):
        """قالب آفاق التطور القديم: {% load hijri_filters %} و institute.city و bg_b64."""
        PermitTemplate.objects.create(
            branch=self.riyadh, city='الدمام', region='الشرقية',
            body_content='{% load hijri_filters %}<p>{{ institute.city }} - {{ institute.region }} | '
                         '{{ program.start_date|hijri }} | {{ program.start_date|hijri_words }} | '
                         '{{ program.end_date|date:"Y/m/d" }}</p>'
                         '{% if bg_b64 %}<img src="data:image/jpeg;base64,{{ bg_b64 }}">{% endif %}',
        )
        self.course.start_date = date(2026, 11, 17)
        self.course.save()
        html = render_html(self.issue())
        self.assertIn('الدمام - الشرقية | 1448/06/07هـ | 7 جمادى الآخرة 1448هـ |', html)
        self.assertTrue(build_pdf(self.issue(student=make_student(self.hafr, national_id='1', mobile='1'),
                                             branch=self.riyadh), strict=True).startswith(b'%PDF'))

    def test_broken_template_falls_back_to_default(self):
        template = PermitTemplate.objects.create(branch=self.riyadh, body_content='{% load hijri_tags %}')
        self.assertTrue(build_pdf(self.issue()).startswith(b'%PDF'))
        # المعاينة بتوضح الغلط بدل ما ترجع للافتراضي
        response = self.client.get(reverse('permittemplate-preview', args=[template.pk]), follow=True)
        self.assertContains(response, 'القالب فيه غلط')
        self.assertContains(response, 'hijri_tags')

    def test_template_create_and_edit_pages(self):
        response = self.client.get(reverse('permittemplate-create') + f'?branch={self.hafr.pk}')
        self.assertContains(response, '{{ client.full_name }}')
        self.client.post(reverse('permittemplate-create'), {
            'branch': self.hafr.pk, 'font_family': 'cairo', 'page_size': 'A4', 'orientation': 'portrait',
            'body_content': '<p>{{ client.full_name }}</p>'})
        template = PermitTemplate.objects.get(branch=self.hafr)
        self.assertEqual(self.client.get(reverse('permittemplate-update', args=[template.pk])).status_code, 200)
        self.assertContains(self.client.get(reverse('permittemplate-list')), 'حفر الباطن')

    def test_template_preview_without_permits(self):
        template = PermitTemplate.objects.create(branch=self.hafr, body_content='<p>{{ client.full_name }}</p>')
        response = self.client.get(reverse('permittemplate-preview', args=[template.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content.startswith(b'%PDF'))

    def test_context_without_template(self):
        ctx = build_context(self.issue())
        self.assertEqual(ctx['institute'].registration_officer, '')
        self.assertIsNone(ctx['institute'].stamp_image)
