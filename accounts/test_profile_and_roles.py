from django.test import TestCase, Client
from django.urls import reverse

from accounts.models import EmployeeRole, Permission, Person, Role
from core.models import Branch, Company


def give_perms(role, *codenames):
    for codename in codenames:
        action, model_name = codename.split('_', 1)
        perm, _ = Permission.objects.get_or_create(
            codename=codename,
            defaults={'name': codename, 'app_label': 'accounts', 'model_name': model_name, 'action': action},
        )
        role.permissions.add(perm)


class ProfileAndEmployeeRoleTests(TestCase):
    def setUp(self):
        company = Company.objects.create(name='Co')
        self.branch = Branch.objects.create(company=company, code=1, name='Hafr')
        self.employee = Person.objects.create_user(
            email='obaid@example.com', password='x', first_name='عبيد', branch=self.branch,
        )
        EmployeeRole.objects.create(person=self.employee, role=Role.objects.create(name='موظف'), branch=self.branch)
        self.client = Client()

    def test_employee_can_view_own_profile_without_view_person(self):
        self.client.force_login(self.employee)
        response = self.client.get(reverse('person-detail', args=[self.employee.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['can_change'])
        self.assertNotContains(response, reverse('person-update', args=[self.employee.slug]))

    def test_employee_cannot_view_someone_else(self):
        other = Person.objects.create_user(email='other@example.com', password='x', first_name='o', branch=self.branch)
        self.client.force_login(self.employee)
        response = self.client.get(reverse('person-detail', args=[other.slug]))
        self.assertEqual(response.status_code, 403)

    def test_profile_link_in_menu_works(self):
        self.client.force_login(self.employee)
        response = self.client.get(reverse('dashboard'))
        self.assertContains(response, reverse('person-detail', args=[self.employee.slug]))

    def test_role_dropdown_lists_non_staff_employee_without_forth_name(self):
        manager = Person.objects.create_user(email='m@example.com', password='x', is_superuser=True)
        no_name = Person.objects.create_user(email='noname@example.com', password='x', branch=self.branch)
        self.assertFalse(no_name.is_staff)
        self.assertEqual(no_name.get_short_name(), 'noname@example.com')
        self.client.force_login(manager)
        response = self.client.get(reverse('employeerole-list'))
        self.assertIn(no_name, response.context['persons'])

    def test_employee_role_search(self):
        manager = Person.objects.create_user(email='m@example.com', password='x', is_superuser=True)
        self.client.force_login(manager)
        found = self.client.get(reverse('employeerole-list'), {'search': 'obaid'})
        self.assertEqual([er.person for er in found.context['employee_roles']], [self.employee])
        missing = self.client.get(reverse('employeerole-list'), {'search': 'nobody'})
        self.assertEqual(len(missing.context['employee_roles']), 0)
        self.assertContains(missing, 'الموظف ليس له دور')

    def test_non_executive_role_page_respects_branch(self):
        give_perms(self.employee.employee_roles.first().role, 'view_employeerole')
        self.client.force_login(self.employee)
        response = self.client.get(reverse('employeerole-list'), {'search': 'عبيد'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['employee_roles']), 1)


class PersonRoleOnCreateTests(TestCase):
    def setUp(self):
        company = Company.objects.create(name='Co')
        self.branch = Branch.objects.create(company=company, code=1, name='Main')
        self.admin = Person.objects.create_user(email='admin@example.com', password='x', is_superuser=True)
        self.employee_role = Role.objects.create(name='موظف')
        self.manager_role = Role.objects.create(name='مدير تنفيذي')
        self.client = Client()
        self.client.force_login(self.admin)

    def test_role_is_given_on_main_branch_when_creating_employee(self):
        response = self.client.post(reverse('person-create-ajax'), {
            'email': 'new@example.com', 'first_name': 'n', 'branch': self.branch.pk,
            'role': self.employee_role.pk, 'is_active': 'on',
            'password1': 'Strong-pass-123', 'password2': 'Strong-pass-123',
        })
        self.assertEqual(response.status_code, 200, response.content)
        person = Person.objects.get(email='new@example.com')
        self.assertEqual(list(person.employee_roles.values_list('role__name', 'branch_id')), [('موظف', self.branch.pk)])
        self.assertEqual(person.get_main_role(), self.employee_role)

    def test_changing_role_replaces_old_one_on_main_branch(self):
        person = Person.objects.create_user(email='p@example.com', password='x', branch=self.branch)
        EmployeeRole.objects.create(person=person, role=self.employee_role, branch=self.branch)
        response = self.client.post(reverse('person-update-ajax', args=[person.pk]), {
            'email': person.email, 'branch': self.branch.pk, 'role': self.manager_role.pk, 'is_active': 'on',
        })
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(list(person.employee_roles.values_list('role__name', flat=True)), ['مدير تنفيذي'])

    def test_role_needs_main_branch(self):
        response = self.client.post(reverse('person-create-ajax'), {
            'email': 'nobranch@example.com', 'first_name': 'n', 'role': self.employee_role.pk,
            'password1': 'Strong-pass-123', 'password2': 'Strong-pass-123',
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('branch', response.json()['errors'])

    def test_employees_page_shows_role_column(self):
        person = Person.objects.create_user(email='p@example.com', password='x', branch=self.branch)
        EmployeeRole.objects.create(person=person, role=self.manager_role, branch=self.branch)
        response = self.client.get(reverse('person-list'))
        self.assertContains(response, 'مدير تنفيذي')
        self.assertNotContains(response, 'الفريق')
