"""Smoke test: every page that scopes by branch through courses/quotations still works,
and a branch employee only sees their own branch's data (specializations are shared)."""
from django.test import TestCase, Client
from django.urls import reverse

from accounts.models import EmployeeRole, Permission, Person, Role
from core.models import Branch, Company
from courses.models import Course, Master
from finance.models import Call, Offer, Payment
from registrations.models import Account
from reports.utils import generate_report_data
from students.models import Contact, Student

VIEW_PERMS = [
    'view_master', 'view_course', 'view_registration', 'view_account', 'view_payment',
    'view_offer', 'view_offer_price', 'view_call', 'view_student', 'view_studentoffer',
]


class BranchScopeSmokeTests(TestCase):
    def setUp(self):
        company = Company.objects.create(name='Faw')
        self.riyadh = Branch.objects.create(company=company, code=1, name='Riyadh')
        self.hafr = Branch.objects.create(company=company, code=2, name='Hafr')
        self.master = Master.objects.create(name='دبلوم الموارد البشرية')
        self.data = {b.pk: self._fill(b) for b in (self.riyadh, self.hafr)}

        self.admin = Person.objects.create_user(email='admin@example.com', password='x', is_superuser=True)
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
        course = Course.objects.create(master=self.master, branch=branch, target_level='الكل')
        student = Student.objects.create(
            contact=Contact.objects.create(first_name=f's{branch.code}', forth_name='x'), branch=branch,
        )
        account = Account.objects.create(course=course, student=student, code=branch.code)
        payment = Payment.objects.create(account=account, code=branch.code, amount_number=100)
        offer = Offer.objects.create(master=self.master, branch=branch, code=branch.code, customer_name='c')
        call = Call.objects.create(offer=offer, person=Person.objects.create_user(email=f'p{branch.code}@x.com', password='x'))
        return {'course': course, 'account': account, 'payment': payment, 'offer': offer, 'call': call}

    def _pages(self, branch):
        d = self.data[branch.pk]
        return [
            reverse('dashboard'),
            reverse('master-list'), reverse('master-detail', args=[self.master.slug]),
            reverse('course-list'), reverse('course-detail', args=[d['course'].pk]),
            reverse('registration-list'), reverse('registration-detail', args=[d['account'].slug]),
            reverse('payment-list'), reverse('payment-detail', args=[d['payment'].slug]),
            reverse('offer-list'), reverse('offer-detail', args=[d['offer'].pk]),
            reverse('call-list'), reverse('call-detail', args=[d['call'].slug]),
            reverse('studentoffer-list'),
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

    def test_employee_sees_shared_master_and_only_own_branch_data(self):
        self.client.force_login(self.employee)
        for url in self._pages(self.hafr):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

        self.assertIn(self.master, self.client.get(reverse('master-list')).context['masters'])
        mine, other = self.data[self.hafr.pk], self.data[self.riyadh.pk]
        self.assertEqual(list(self.client.get(reverse('course-list')).context['courses']), [mine['course']])
        self.assertEqual(list(self.client.get(reverse('registration-list')).context['object_list']), [mine['account']])
        self.assertEqual(list(self.client.get(reverse('payment-list')).context['object_list']), [mine['payment']])
        self.assertEqual(list(self.client.get(reverse('offer-list')).context['object_list']), [mine['offer']])
        self.assertEqual(list(self.client.get(reverse('call-list')).context['object_list']), [mine['call']])

        for url in [
            reverse('course-detail', args=[other['course'].pk]),
            reverse('registration-detail', args=[other['account'].slug]),
            reverse('payment-detail', args=[other['payment'].slug]),
            reverse('offer-detail', args=[other['offer'].pk]),
        ]:
            with self.subTest(url=url):
                self.assertIn(self.client.get(url).status_code, (403, 404))

    def test_reports_count_per_branch(self):
        for report_type in ['summary', 'students', 'offers', 'branches']:
            with self.subTest(report_type=report_type):
                generate_report_data(report_type, user=self.admin)
        summary = generate_report_data('summary', user=self.admin, branch=self.hafr)
        self.assertIsInstance(summary, dict)
