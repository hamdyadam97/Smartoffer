from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import EmployeeRole, Permission, Person, Role
from core.models import Branch, Company


class RoleOnPersonFormTests(TestCase):
    """الدور بيتحدد من شاشة الموظف نفسها، من غير صفحة أدوار الموظفين."""

    def setUp(self):
        company = Company.objects.create(name='Co')
        self.b1 = Branch.objects.create(company=company, code=1, name='الرياض')
        self.b2 = Branch.objects.create(company=company, code=2, name='حفر الباطن')
        self.employee_role = Role.objects.create(name='موظف')
        self.manager_role = Role.objects.create(name='مدير')
        self.admin = Person.objects.create_user(email='admin@example.com', password='x', is_superuser=True)
        self.web = Client()
        self.web.force_login(self.admin)

    def create(self, **extra):
        data = {'email': 'new@example.com', 'first_name': 'أحمد', 'branch': self.b1.pk,
                'role': self.employee_role.pk, 'password1': 'Pass12345!', 'password2': 'Pass12345!',
                'is_active': 'on', **extra}
        return self.web.post(reverse('person-create-ajax'), data)

    def roles(self, person):
        return set(person.employee_roles.values_list('role__name', 'branch__code'))

    def test_role_applies_on_create(self):
        self.assertTrue(self.create().json()['success'])
        person = Person.objects.get(email='new@example.com')
        self.assertEqual(self.roles(person), {('موظف', 1)})

    def test_all_branches_checkbox(self):
        self.create(role=self.manager_role.pk, all_branches='on')
        person = Person.objects.get(email='new@example.com')
        self.assertEqual(self.roles(person), {('مدير', 1), ('مدير', 2)})
        self.assertTrue(person.has_role_on_all_branches())

    def test_edit_changes_role_and_scope(self):
        self.create(role=self.manager_role.pk, all_branches='on')
        person = Person.objects.get(email='new@example.com')
        self.web.post(reverse('person-update-ajax', args=[person.pk]), {
            'email': person.email, 'first_name': 'أحمد', 'branch': self.b2.pk,
            'role': self.employee_role.pk, 'is_active': 'on'})
        self.assertEqual(self.roles(person), {('موظف', 2)})

    def test_branch_manager_cannot_grant_all_branches(self):
        perm = Permission.objects.create(codename='add_person', name='x', app_label='accounts',
                                         model_name='person', action='add')
        self.manager_role.permissions.add(perm)
        manager = Person.objects.create_user(email='m@example.com', password='x', branch=self.b1)
        EmployeeRole.objects.create(person=manager, role=self.manager_role, branch=self.b1)
        other = EmployeeRole.objects.create(person=self.admin, role=self.employee_role, branch=self.b2)
        self.web.force_login(manager)
        self.create(all_branches='on')
        person = Person.objects.get(email='new@example.com')
        self.assertEqual(self.roles(person), {('موظف', 1)})
        self.assertTrue(EmployeeRole.objects.filter(pk=other.pk).exists())

    def test_editing_from_modal_keeps_admin_and_staff_flags(self):
        """الشاشة مفيهاش خانة «مدير نظام» ولا «موظف»: الحفظ منها مايغيرهمش."""
        other_admin = Person.objects.create_user(email='boss@example.com', password='x', is_superuser=True,
                                                 is_staff=True, branch=self.b1)
        response = self.web.post(reverse('person-update-ajax', args=[other_admin.pk]), {
            'email': other_admin.email, 'first_name': 'مدير', 'branch': self.b1.pk, 'is_active': 'on'})
        self.assertTrue(response.json()['success'])
        other_admin.refresh_from_db()
        self.assertTrue(other_admin.is_superuser)
        self.assertTrue(other_admin.is_staff)

    def test_employee_page_has_no_separate_role_screen(self):
        page = self.web.get(reverse('person-list'))
        self.assertContains(page, 'id_all_branches')
        self.assertNotContains(page, 'personRoleModal')
        self.assertNotContains(page, 'أدوار الموظفين')
