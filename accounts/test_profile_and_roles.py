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
