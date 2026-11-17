"""Smoke test: every page that scopes by branch still works, and a branch employee only sees
their own branch's data (specializations are shared between branches)."""
from django.test import TestCase, Client
from django.urls import reverse

from accounts.models import EmployeeRole, Permission, Person, Role
from core.models import Branch, Company
from courses.models import Course
from offers.models import StudentOffer
from registrations.models import Account
from reports.utils import generate_report_data, get_dashboard_data
from students.models import Contact, Student

VIEW_PERMS = [
    'view_course', 'view_registration', 'view_account', 'view_student', 'view_studentoffer',
]


class BranchScopeSmokeTests(TestCase):
    def setUp(self):
        company = Company.objects.create(name='Faw')
        self.riyadh = Branch.objects.create(company=company, code=1, name='Riyadh')
        self.hafr = Branch.objects.create(company=company, code=2, name='Hafr')
        # تخصص لكل الفروع + تخصص لكل فرع
        self.shared = Course.objects.create(program_type='دبلوم', name='الموارد البشرية', branch=None)
        self.admin = Person.objects.create_user(email='admin@example.com', password='x', is_superuser=True)
        self.data = {b.pk: self._fill(b) for b in (self.riyadh, self.hafr)}

        self.employee = Person.objects.create_user(email='hafr@example.com', password='x', branch=self.hafr)
        role = Role.objects.create(name='موظف')
        for codename in VIEW_PERMS:
            action, model_name = codename.split('_', 1)
            perm, _ = Permission.objects.get_or_create(
                codename=codename,
                defaults={'name': codename, 'app_label': 'x', 'model_name': model_name, 'action': action},
            )
            role.permissions.add(perm)
        EmployeeRole.objects.create(person=self.employee, role=role, branch=self.hafr)
        self.client = Client()

    def _fill(self, branch):
        course = Course.objects.create(program_type='دورة', name=f'لغة {branch.name}', branch=branch, target_level='الكل')
        student = Student.objects.create(
            contact=Contact.objects.create(first_name=f's{branch.code}', forth_name='x'), branch=branch,
        )
        account = Account.objects.create(course=course, student=student, code=branch.code)
        offer = StudentOffer.objects.create(
            title=self.shared.get_display_name(), content='c', branch=branch, course=self.shared,
            created_by=self.admin,
        )
        return {'course': course, 'account': account, 'offer': offer}

    def _pages(self, branch):
        d = self.data[branch.pk]
        return [
            reverse('dashboard'),
            reverse('course-detail', args=[self.shared.pk]),
            reverse('course-list'), reverse('course-detail', args=[d['course'].pk]),
            reverse('registration-list'), reverse('registration-detail', args=[d['account'].slug]),
            reverse('studentoffer-list'), reverse('studentoffer-detail', args=[d['offer'].slug]),
        ]

    def test_admin_can_open_every_page(self):
        self.client.force_login(self.admin)
        for url in self._pages(self.riyadh) + [
            reverse('branch-dashboard', args=[self.hafr.slug]),
            reverse('branch-detail', args=[self.hafr.slug]),
            reverse('report-dashboard'),
        ]:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_dashboard_counts(self):
        self.client.force_login(self.admin)
        ctx = self.client.get(reverse('dashboard')).context
        self.assertEqual(ctx['students_count'], 2)
        self.assertEqual(ctx['registrations_count'], 2)
        self.assertEqual(ctx['student_offers_count'], 2)
        self.assertEqual(ctx['offer_status_data'], [2])
        ctx = self.client.get(reverse('branch-dashboard', args=[self.hafr.slug])).context
        self.assertEqual(ctx['student_offers_count'], 1)

    def test_employee_sees_shared_course_and_only_own_branch_data(self):
        self.client.force_login(self.employee)
        for url in self._pages(self.hafr):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

        mine, other = self.data[self.hafr.pk], self.data[self.riyadh.pk]
        self.assertEqual(set(self.client.get(reverse('course-list')).context['courses']), {mine['course'], self.shared})
        self.assertEqual(list(self.client.get(reverse('registration-list')).context['object_list']), [mine['account']])
        self.assertEqual(list(self.client.get(reverse('studentoffer-list')).context['offers']), [mine['offer']])
        # لوحة التحكم بتعرض شغل الموظف هو بس (مش كل بيانات الفرع)، والموظف ده ماعملش حاجة
        self.assertEqual(self.client.get(reverse('dashboard')).context['students_count'], 0)

        for url in [
            reverse('course-detail', args=[other['course'].pk]),
            reverse('registration-detail', args=[other['account'].slug]),
            reverse('studentoffer-detail', args=[other['offer'].slug]),
        ]:
            with self.subTest(url=url):
                self.assertIn(self.client.get(url).status_code, (403, 404))

    def test_reports(self):
        for report_type in ['summary', 'students', 'offers', 'branches', 'employees']:
            with self.subTest(report_type=report_type):
                generate_report_data(report_type, user=self.admin)
        offers = generate_report_data('offers', user=self.admin, branch=self.hafr)
        self.assertEqual(offers['إجمالي العروض'], 1)
        self.assertEqual(offers['العروض'][0]['التخصص'], 'دبلوم الموارد البشرية')
        self.assertEqual(get_dashboard_data(user=self.admin)['offers_total'], 2)

    def test_quick_offer_uses_specialization_directly(self):
        self.client.force_login(self.admin)
        other_branch_course = self.data[self.riyadh.pk]['course']
        data = {
            'branch': self.hafr.pk, 'course': self.shared.pk, 'content': 'c', 'price': '1500',
            'contact_name': 'Ali', 'contact_phone': '966500000000', 'channel': 'whatsapp',
        }
        response = self.client.post(reverse('quick-offer-ajax'), data)
        self.assertEqual(response.status_code, 200, response.content)
        offer = StudentOffer.objects.get(slug=response.json()['slug'])
        self.assertEqual((offer.title, offer.course), ('دبلوم الموارد البشرية', self.shared))
        # تخصص فرع تاني مينفعش
        response = self.client.post(reverse('quick-offer-ajax'), {**data, 'course': other_branch_course.pk})
        self.assertEqual(response.status_code, 400)

    def test_registration_on_shared_specialization_follows_student_branch(self):
        from registrations.forms import AccountForm
        student = Student.objects.get(branch=self.hafr)
        account = Account.objects.create(course=self.shared, student=student, code=9)
        self.assertEqual(account.get_branch(), self.hafr)
        self.client.force_login(self.employee)
        self.assertIn(account, self.client.get(reverse('registration-list')).context['object_list'])
        form = AccountForm(data={
            'course': self.data[self.riyadh.pk]['course'].pk, 'student': student.pk, 'code': 10,
            'register_date': '2026-11-16T10:00', 'course_payment_type': 'نقدي',
            'course_price': 0, 'course_discount_amount': 0, 'course_profit_amount': 0, 'course_credit_amount': 0,
        }, user=self.admin)
        self.assertFalse(form.is_valid())
        self.assertIn('course', form.errors)
