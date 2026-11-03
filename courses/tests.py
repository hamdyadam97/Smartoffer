from django.test import TestCase, Client
from django.urls import reverse

from accounts.models import Person, Role, EmployeeRole, Permission
from core.models import Company, Branch
from .models import Master, Course


class CourseFormAjaxTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Smart Academy')
        self.branch = Branch.objects.create(company=self.company, code=1, name='Main Branch')
        self.master = Master.objects.create(branch=self.branch, code=10, name='Programming')

        self.user = Person.objects.create_user(
            email='tester@example.com',
            password='testpass123',
            first_name='Test',
            forth_name='User',
        )

        # إنشاء دور وصلاحيات
        self.role = Role.objects.create(name='course_manager')
        for codename in ['view_course', 'add_course', 'change_course', 'add_master']:
            action, model_name = codename.split('_', 1)
            perm, _ = Permission.objects.get_or_create(
                codename=codename,
                defaults={'name': codename, 'app_label': 'courses', 'model_name': model_name, 'action': action},
            )
            self.role.permissions.add(perm)
        EmployeeRole.objects.create(person=self.user, role=self.role, branch=self.branch)

        self.client = Client()
        self.client.force_login(self.user)

    def test_course_list_has_modal_context(self):
        response = self.client.get(reverse('course-list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('branches', response.context)
        self.assertIn('program_types', response.context)
        self.assertIn('form_master_queryset', response.context)
        self.assertContains(response, 'courseModal')
        self.assertContains(response, reverse('course-create-ajax'))
        self.assertContains(response, 'masterModal')
        self.assertContains(response, '/masters/ajax/info/')

    def test_master_info_ajax_returns_company_and_next_code(self):
        url = reverse('master-info-ajax', args=[self.master.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['company_name'], 'Smart Academy')
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
            'program_type': 'دورة',
            'code': 20,
            'name': 'New Master',
            'period': '3 months',
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(Master.objects.get(pk=data['master']['id']).program_type, 'دورة')

    def test_course_create_ajax_adds_course(self):
        url = reverse('course-create-ajax')
        response = self.client.post(url, {
            'master': self.master.pk,
            'code': 1,
            'instructor': 'Dr. Ahmed',
            'company_name': '',
            'max_student_count': 20,
            'target_level': 'الكل',
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertTrue(Course.objects.filter(pk=data['course']['id']).exists())

    def test_delete_course_deletes_registrations_and_payments(self):
        from finance.models import Payment
        from registrations.models import Account
        from students.models import Contact, Student
        course = Course.objects.create(master=self.master, code=1, target_level='الكل')
        student = Student.objects.create(
            contact=Contact.objects.create(first_name='Ali', forth_name='Omar'),
            branch=self.branch,
        )
        account = Account.objects.create(course=course, student=student, code=1)
        Payment.objects.create(account=account, code=1, amount_number=100)
        self.user.is_superuser = True
        self.user.save()

        confirm = self.client.get(reverse('course-delete', args=[course.pk]))
        self.assertEqual(confirm.context['accounts_count'], 1)
        self.assertEqual(confirm.context['payments_count'], 1)

        response = self.client.post(reverse('course-delete', args=[course.pk]))

        self.assertRedirects(response, reverse('course-list'))
        self.assertFalse(Course.objects.filter(pk=course.pk).exists())
        self.assertFalse(Account.objects.filter(pk=account.pk).exists())
        self.assertFalse(Payment.objects.filter(account_id=account.pk).exists())

    def test_delete_master_deletes_courses_registrations_and_offers(self):
        from finance.models import Call, Offer, Payment
        from registrations.models import Account
        from students.models import Contact, Student
        course = Course.objects.create(master=self.master, code=1, target_level='الكل')
        student = Student.objects.create(
            contact=Contact.objects.create(first_name='Ali', forth_name='Omar'),
            branch=self.branch,
        )
        account = Account.objects.create(course=course, student=student, code=1)
        Payment.objects.create(account=account, code=1, amount_number=100)
        offer = Offer.objects.create(master=self.master, code=1, customer_name='Client')
        Call.objects.create(offer=offer, person=self.user)
        self.user.is_superuser = True
        self.user.save()

        confirm = self.client.get(reverse('master-delete', args=[self.master.slug]))
        self.assertEqual(confirm.context['courses_count'], 1)
        self.assertEqual(confirm.context['calls_count'], 1)

        response = self.client.post(reverse('master-delete', args=[self.master.slug]))

        self.assertRedirects(response, reverse('master-list'))
        self.assertFalse(Master.objects.filter(pk=self.master.pk).exists())
        self.assertFalse(Course.objects.filter(pk=course.pk).exists())
        self.assertFalse(Account.objects.filter(pk=account.pk).exists())
        self.assertFalse(Offer.objects.filter(pk=offer.pk).exists())

    def test_course_create_ajax_requires_permission(self):
        # مستخدم بدون صلاحية
        other = Person.objects.create_user(
            email='other@example.com',
            password='testpass123',
            first_name='Other',
            forth_name='User',
        )
        self.client.force_login(other)
        url = reverse('course-create-ajax')
        response = self.client.post(url, {
            'master': self.master.pk,
            'code': 5,
            'target_level': 'الكل',
        })
        self.assertEqual(response.status_code, 403)
