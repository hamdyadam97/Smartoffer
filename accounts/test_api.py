from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from core.models import Company, Branch
from .models import Team, Person, Role, EmployeeRole, EmployeePerformance


class AuthAPITest(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Test Co')
        self.branch = Branch.objects.create(name='Branch', code=1, company=self.company)
        self.user = Person.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            forth_name='User',
            branch=self.branch
        )

    def test_login_success(self):
        url = '/api/auth/login/'
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_failure(self):
        url = '/api/auth/login/'
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_current_user(self):
        self.client.force_authenticate(user=self.user)
        url = '/api/persons/me/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')


class TeamAPITest(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Test Co')
        self.branch = Branch.objects.create(name='Branch', code=1, company=self.company)
        self.user = Person.objects.create_user(
            email='admin@test.com',
            password='test123',
            first_name='Admin',
            forth_name='User',
            is_staff=True,
            branch=self.branch
        )
        self.client.force_authenticate(user=self.user)
        self.team = Team.objects.create(name='فريق المبيعات', code='SALES')

    def test_list_teams(self):
        url = '/api/teams/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_team(self):
        url = '/api/teams/'
        data = {
            'name': 'فريق التسويق',
            'code': 'MKT',
            'description': 'فريق التسويق'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'فريق التسويق')

    def test_retrieve_team(self):
        url = f'/api/teams/{self.team.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'فريق المبيعات')

    def test_update_team(self):
        url = f'/api/teams/{self.team.id}/'
        data = {'name': 'فريق المبيعات المحدث', 'code': 'SALES'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'فريق المبيعات المحدث')

    def test_delete_team(self):
        url = f'/api/teams/{self.team.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class PersonAPITest(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Test Co')
        self.branch = Branch.objects.create(name='Branch', code=1, company=self.company)
        self.user = Person.objects.create_user(
            email='admin@test.com',
            password='test123',
            first_name='Admin',
            forth_name='User',
            is_staff=True,
            branch=self.branch
        )
        self.client.force_authenticate(user=self.user)

    def test_list_persons(self):
        url = '/api/persons/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_person(self):
        url = '/api/persons/'
        data = {
            'email': 'newuser@test.com',
            'password': 'newpass123',
            'first_name': 'جديد',
            'forth_name': 'مستخدم',
            'branch': self.branch.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class RoleAPITest(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Test Co')
        self.branch = Branch.objects.create(name='Branch', code=1, company=self.company)
        self.user = Person.objects.create_user(
            email='admin@test.com',
            password='test123',
            first_name='Admin',
            forth_name='User',
            is_staff=True,
            branch=self.branch
        )
        self.client.force_authenticate(user=self.user)
        self.role = Role.objects.create(name='مدير_فرع', description='مدير')

    def test_list_roles(self):
        url = '/api/roles/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_role(self):
        url = '/api/roles/'
        data = {
            'name': 'موظف_عروض',
            'description': 'موظف عروض'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class EmployeeRoleAPITest(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Test Co')
        self.branch = Branch.objects.create(name='Branch', code=1, company=self.company)
        self.user = Person.objects.create_user(
            email='admin@test.com',
            password='test123',
            first_name='Admin',
            forth_name='User',
            is_staff=True,
            branch=self.branch
        )
        self.role = Role.objects.create(name='مدير_فرع', description='مدير')
        self.emp_role = EmployeeRole.objects.create(
            person=self.user,
            role=self.role,
            branch=self.branch
        )
        self.client.force_authenticate(user=self.user)

    def test_list_employee_roles(self):
        url = '/api/employee-roles/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 1)


class EmployeePerformanceAPITest(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Test Co')
        self.branch = Branch.objects.create(name='Branch', code=1, company=self.company)
        self.user = Person.objects.create_user(
            email='admin@test.com',
            password='test123',
            first_name='Admin',
            forth_name='User',
            is_staff=True,
            branch=self.branch
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
        self.client.force_authenticate(user=self.user)

    def test_list_performances(self):
        url = '/api/employee-performances/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 1)

    def test_create_performance(self):
        url = '/api/employee-performances/'
        data = {
            'person': self.user.id,
            'branch': self.branch.id,
            'period_month': 5,
            'period_year': 2026,
            'offers_sent': 15,
            'offers_opened': 8,
            'subscriptions': 3
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
