from django.test import TestCase, Client
from django.urls import reverse

from accounts.models import Person, Role, EmployeeRole, Permission
from core.models import Company, Branch, MasterCategory
from .models import Master, Course


class CourseFormAjaxTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Root Academy')
        self.branch = Branch.objects.create(company=self.company, code=1, name='Digital Roots')
        self.master = Master.objects.create(branch=self.branch, code=10, name='Programming')

        self.user = Person.objects.create_user(
            email='tester@example.com',
            password='testpass123',
            first_name='Test',
            forth_name='User',
        )

        # إنشاء دور وصلاحيات
        self.role = Role.objects.create(name='course_manager')
        for codename in ['add_course', 'change_course', 'add_master']:
            perm = Permission.objects.get(codename=codename, content_type__app_label='courses')
            self.role.permissions.add(perm)
        EmployeeRole.objects.create(person=self.user, role=self.role, branch=self.branch)

        self.client = Client()
        self.client.force_login(self.user)

    def test_course_create_view_has_modal_context(self):
        response = self.client.get(reverse('course-create'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('branches', response.context)
        self.assertIn('categories', response.context)
        self.assertContains(response, 'masterModal')
        self.assertContains(response, 'master-info-ajax')

    def test_master_info_ajax_returns_company_and_next_code(self):
        url = reverse('master-info-ajax', args=[self.master.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['company_name'], 'Root Academy')
        self.assertEqual(data['next_code'], 1)

    def test_master_info_ajax_next_code_after_existing_course(self):
        Course.objects.create(master=self.master, code=1, target_level='الكل')
        Course.objects.create(master=self.master, code=3, target_level='الكل')
        url = reverse('master-info-ajax', args=[self.master.pk])
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(data['next_code'], 4)

    def test_master_create_ajax_adds_master(self):
        url = reverse('master-create-ajax')
        response = self.client.post(url, {
            'branch': self.branch.pk,
            'code': 20,
            'name': 'New Master',
            'period': '3 months',
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertTrue(Master.objects.filter(pk=data['master']['id']).exists())
