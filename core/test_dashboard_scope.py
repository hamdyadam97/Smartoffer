from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import EmployeeRole, Permission, Person, Role
from core.models import Branch, Company
from courses.models import Course
from offers.models import OfferRecipient, StudentOffer
from permits.models import Permit
from students.models import Contact, Student


class DashboardScopeTests(TestCase):
    """لوحة التحكم: الموظف يشوف شغله بس، المدير فروعه، مدير النظام كل حاجة."""

    def setUp(self):
        company = Company.objects.create(name='Co')
        self.riyadh = Branch.objects.create(company=company, code=1, name='الرياض')
        self.hafr = Branch.objects.create(company=company, code=2, name='حفر الباطن')
        course = Course.objects.create(program_type='دبلوم', name='موارد', branch=None)
        self.ali = Person.objects.create_user(email='ali@example.com', password='x', branch=self.riyadh)
        self.sara = Person.objects.create_user(email='sara@example.com', password='x', branch=self.riyadh)
        self.boss = Person.objects.create_user(email='boss@example.com', password='x', branch=self.riyadh)
        self.admin = Person.objects.create_user(email='admin@example.com', password='x', is_superuser=True)

        employee_role = Role.objects.create(name='موظف')
        for code in ('view_studentoffer', 'view_student', 'view_permit', 'view_account'):
            perm, _ = Permission.objects.get_or_create(codename=code, defaults={
                'name': code, 'app_label': 'x', 'model_name': code.split('_', 1)[1], 'action': 'view'})
            employee_role.permissions.add(perm)
        manager_role = Role.objects.create(name='مدير')
        manager_role.permissions.add(*employee_role.permissions.all(), Permission.objects.get(codename='view_branch_dashboard'))
        for person in (self.ali, self.sara):
            EmployeeRole.objects.create(person=person, role=employee_role, branch=self.riyadh)
        EmployeeRole.objects.create(person=self.boss, role=manager_role, branch=self.riyadh)

        def student(name, branch):
            return Student.objects.create(contact=Contact.objects.create(first_name=name, forth_name='x'), branch=branch)

        def offer(person, branch, st):
            o = StudentOffer.objects.create(title=f'عرض {person.email}', content='x', branch=branch, created_by=person)
            OfferRecipient.objects.create(offer=o, student=st, channel='whatsapp')

        s1, s2, s3 = student('طالب علي', self.riyadh), student('طالب سارة', self.riyadh), student('طالب حفر', self.hafr)
        offer(self.ali, self.riyadh, s1)
        offer(self.ali, self.riyadh, s1)
        offer(self.sara, self.riyadh, s2)
        offer(self.admin, self.hafr, s3)
        Permit.objects.create(student=s1, branch=self.riyadh, course=course, issued_by=self.ali)
        Permit.objects.create(student=s2, branch=self.riyadh, course=course, issued_by=self.sara)
        Permit.objects.create(student=s3, branch=self.hafr, course=course, issued_by=self.admin)

    def dashboard(self, person, **params):
        web = Client()
        web.force_login(person)
        return web.get(reverse('dashboard'), params)

    def test_employee_sees_only_own_work(self):
        ctx = self.dashboard(self.ali).context
        self.assertEqual((ctx['student_offers_count'], ctx['permits_count'], ctx['students_count']), (2, 1, 1))
        self.assertFalse(ctx['is_manager_view'])
        self.assertEqual(ctx['branch_stats'], [])
        self.assertNotContains(self.dashboard(self.ali), 'طالب سارة')
        # التجميع في الرسوم مايتكررش (عرضين لنفس الطالب)
        self.assertEqual(sum(ctx['offer_status_data']), 2)

    def test_employee_cannot_pick_branch(self):
        self.assertEqual(self.dashboard(self.ali, branch=self.riyadh.pk).status_code, 403)

    def test_manager_sees_his_branch_only(self):
        ctx = self.dashboard(self.boss).context
        self.assertEqual((ctx['student_offers_count'], ctx['permits_count'], ctx['students_count']), (3, 2, 2))
        self.assertTrue(ctx['is_manager_view'])
        self.assertEqual([bs['branch'] for bs in ctx['branch_stats']], [self.riyadh])
        self.assertEqual(self.dashboard(self.boss, branch=self.hafr.pk).status_code, 403)

    def test_admin_sees_everything(self):
        ctx = self.dashboard(self.admin).context
        self.assertEqual((ctx['student_offers_count'], ctx['permits_count']), (4, 3))
        ctx = self.dashboard(self.admin, branch=self.hafr.pk).context
        self.assertEqual((ctx['student_offers_count'], ctx['permits_count']), (1, 1))

    def test_branch_dashboard_is_for_managers(self):
        web = Client()
        web.force_login(self.ali)
        self.assertEqual(web.get(reverse('branch-dashboard', args=[self.riyadh.slug])).status_code, 403)
        web.force_login(self.boss)
        self.assertEqual(web.get(reverse('branch-dashboard', args=[self.riyadh.slug])).status_code, 200)
        self.assertEqual(web.get(reverse('branch-dashboard', args=[self.hafr.slug])).status_code, 403)
