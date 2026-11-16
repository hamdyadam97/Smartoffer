from django.test import TestCase, Client
from django.urls import reverse

from accounts.models import Person, Role, EmployeeRole, Permission
from core.models import Company, Branch
from .models import Course


def give_perms(role, *codenames):
    for codename in codenames:
        action, model_name = codename.split('_', 1)
        perm, _ = Permission.objects.get_or_create(
            codename=codename,
            defaults={'name': codename, 'app_label': 'courses', 'model_name': model_name, 'action': action},
        )
        role.permissions.add(perm)


class CourseTests(TestCase):
    """«التخصصات»: دبلوم أو دورة بكل بياناتها، والفرع الفاضي = لكل الفروع."""

    def setUp(self):
        self.company = Company.objects.create(name='Smart Academy')
        self.branch = Branch.objects.create(company=self.company, code=1, name='Main Branch')
        self.other_branch = Branch.objects.create(company=self.company, code=2, name='Hafr')
        self.course = Course.objects.create(program_type='دبلوم', name='موارد بشرية', branch=self.branch)

        self.user = Person.objects.create_user(email='tester@example.com', password='x', first_name='Test')
        self.role = Role.objects.create(name='course_manager')
        give_perms(self.role, 'view_course', 'add_course', 'change_course', 'delete_course')
        EmployeeRole.objects.create(person=self.user, role=self.role, branch=self.branch)
        self.client = Client()
        self.client.force_login(self.user)

    def _create(self, **data):
        payload = {'program_type': 'دبلوم', 'name': 'x', 'max_student_count': 1, 'target_level': 'الكل'}
        payload.update(data)
        return self.client.post(reverse('course-create-ajax'), payload)

    def test_list_page(self):
        response = self.client.get(reverse('course-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'التخصصات')
        self.assertContains(response, 'courseModal')
        self.assertIn(self.course, response.context['courses'])

    def test_create_with_type_and_all_course_data(self):
        response = self._create(
            program_type='دورة', name='لغة إنجليزية', branch=self.branch.pk, instructor='أحمد',
            period='شهر', hours=40, start_date='2026-12-01',
        )
        self.assertEqual(response.status_code, 200, response.content)
        course = Course.objects.get(pk=response.json()['course']['id'])
        self.assertEqual(course.get_display_name(), 'دورة لغة إنجليزية')
        self.assertEqual((course.branch, course.instructor, course.period, course.hours),
                         (self.branch, 'أحمد', 'شهر', 40))
        self.assertGreater(course.code, self.course.code)

    def test_type_word_in_name_becomes_the_type(self):
        response = self._create(program_type='دبلوم', name='دورة موارد بشرية', branch=self.branch.pk)
        course = Course.objects.get(pk=response.json()['course']['id'])
        self.assertEqual((course.program_type, course.name), ('دورة', 'موارد بشرية'))

    def test_filter_by_type(self):
        Course.objects.create(program_type='دورة', name='لغة', branch=self.branch)
        response = self.client.get(reverse('course-list'), {'program_type': 'دورة'})
        self.assertEqual([c.name for c in response.context['courses']], ['لغة'])

    def test_employee_sees_own_branch_and_all_branches_items_only(self):
        shared = Course.objects.create(program_type='دورة', name='لكل الفروع', branch=None)
        other = Course.objects.create(program_type='دبلوم', name='فرع تاني', branch=self.other_branch)
        courses = list(self.client.get(reverse('course-list')).context['courses'])
        self.assertIn(shared, courses)
        self.assertIn(self.course, courses)
        self.assertNotIn(other, courses)
        self.assertEqual(self.client.get(reverse('course-detail', args=[shared.pk])).status_code, 200)
        self.assertIn(self.client.get(reverse('course-detail', args=[other.pk])).status_code, (403, 404))

    def test_employee_cannot_create_in_other_branch(self):
        response = self._create(name='y', branch=self.other_branch.pk)
        self.assertEqual(response.status_code, 400)

    def test_delete_deletes_registrations(self):
        from registrations.models import Account
        from students.models import Contact, Student
        student = Student.objects.create(
            contact=Contact.objects.create(first_name='Ali', forth_name='Omar'), branch=self.branch,
        )
        account = Account.objects.create(course=self.course, student=student, code=1)
        confirm = self.client.get(reverse('course-delete', args=[self.course.pk]))
        self.assertEqual(confirm.context['accounts_count'], 1)
        response = self.client.post(reverse('course-delete', args=[self.course.pk]))
        self.assertRedirects(response, reverse('course-list'))
        self.assertFalse(Course.objects.filter(pk=self.course.pk).exists())
        self.assertFalse(Account.objects.filter(pk=account.pk).exists())

    def test_detail_shows_only_own_branch_students_for_shared_item(self):
        from registrations.models import Account
        from students.models import Contact, Student
        shared = Course.objects.create(program_type='دورة', name='مشترك', branch=None)
        give_perms(self.role, 'view_registration')
        mine = Student.objects.create(contact=Contact.objects.create(first_name='mine', forth_name='x'), branch=self.branch)
        theirs = Student.objects.create(contact=Contact.objects.create(first_name='theirs', forth_name='x'), branch=self.other_branch)
        Account.objects.create(course=shared, student=mine, code=1)
        Account.objects.create(course=shared, student=theirs, code=2)
        response = self.client.get(reverse('course-detail', args=[shared.pk]))
        self.assertEqual([a.student for a in response.context['accounts']], [mine])

    def test_create_requires_permission(self):
        other = Person.objects.create_user(email='other@example.com', password='x')
        self.client.force_login(other)
        self.assertEqual(self._create(name='z').status_code, 403)
