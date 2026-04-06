from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import Company, Branch
from .models import Team, Role, EmployeeRole, EmployeePerformance

User = get_user_model()


class TeamModelTest(TestCase):
    def setUp(self):
        self.team = Team.objects.create(
            name='فريق المبيعات',
            code='SALES',
            description='فريق مبيعات المعهد'
        )

    def test_team_creation(self):
        self.assertEqual(self.team.name, 'فريق المبيعات')
        self.assertEqual(self.team.code, 'SALES')
        self.assertEqual(str(self.team), 'فريق المبيعات')

    def test_team_unique_code(self):
        with self.assertRaises(Exception):
            Team.objects.create(name='فريق آخر', code='SALES')


class PersonModelTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Test Company')
        self.branch = Branch.objects.create(
            name='الفرع الرئيسي',
            code=1,
            company=self.company
        )
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='أحمد',
            second_name='محمد',
            third_name='علي',
            forth_name='خالد',
            branch=self.branch
        )

    def test_user_creation(self):
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.get_full_name(), 'أحمد محمد علي خالد')
        self.assertEqual(self.user.get_short_name(), 'أحمد خالد')
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff)

    def test_user_str(self):
        self.assertIn('test@example.com', str(self.user))

    def test_get_branches(self):
        branches = self.user.get_branches()
        self.assertIn(self.branch, branches)


class RoleModelTest(TestCase):
    def setUp(self):
        self.role = Role.objects.create(
            name='مدير_فرع',
            description='مدير الفرع الرئيسي'
        )

    def test_role_creation(self):
        self.assertEqual(self.role.name, 'مدير_فرع')
        self.assertEqual(self.role.get_name_display(), 'مدير فرع')


class EmployeeRoleModelTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Test Co')
        self.branch = Branch.objects.create(name='Branch', code=1, company=self.company)
        self.user = User.objects.create_user(
            email='emp@test.com',
            password='test123',
            first_name='Test',
            forth_name='User'
        )
        self.role = Role.objects.create(name='موظف_عروض')
        self.emp_role = EmployeeRole.objects.create(
            person=self.user,
            role=self.role,
            branch=self.branch
        )

    def test_employee_role_creation(self):
        self.assertEqual(self.emp_role.person, self.user)
        self.assertEqual(self.emp_role.role, self.role)
        self.assertEqual(self.emp_role.branch, self.branch)

    def test_unique_together(self):
        with self.assertRaises(Exception):
            EmployeeRole.objects.create(
                person=self.user,
                role=self.role,
                branch=self.branch
            )


class EmployeePerformanceModelTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Test Co')
        self.branch = Branch.objects.create(name='Branch', code=1, company=self.company)
        self.user = User.objects.create_user(
            email='perf@test.com',
            password='test123',
            first_name='Test',
            forth_name='User'
        )
        self.performance = EmployeePerformance.objects.create(
            person=self.user,
            branch=self.branch,
            period_month=4,
            period_year=2026,
            offers_sent=10,
            offers_opened=5,
            subscriptions=2
        )

    def test_performance_creation(self):
        self.assertEqual(self.performance.offers_sent, 10)
        self.assertEqual(self.performance.subscriptions, 2)
        self.assertEqual(str(self.performance), 'Test User - 4/2026')
