from django.test import TestCase, Client
from django.urls import reverse

from accounts.models import EmployeeRole, Permission, Person, Role
from core.models import Branch, Company
from courses.models import Course, Master
from registrations.models import Account
from students.models import Contact, Student


def role_with(*codenames):
    role = Role.objects.create(name='-'.join(codenames))
    for codename in codenames:
        action, model_name = codename.split('_', 1)
        perm, _ = Permission.objects.get_or_create(
            codename=codename,
            defaults={'name': codename, 'app_label': 'x', 'model_name': model_name, 'action': action},
        )
        role.permissions.add(perm)
    return role


class SecurityTests(TestCase):
    def setUp(self):
        company = Company.objects.create(name='Co')
        self.mine = Branch.objects.create(company=company, code=1, name='Mine')
        self.other = Branch.objects.create(company=company, code=2, name='Other')
        self.manager = Person.objects.create_user(email='mgr@example.com', password='x', branch=self.mine)
        EmployeeRole.objects.create(
            person=self.manager, branch=self.mine,
            role=role_with('add_person', 'change_person', 'delete_person', 'view_person',
                           'view_registration', 'add_registration'),
        )
        self.admin = Person.objects.create_user(email='admin@example.com', password='x', is_superuser=True, branch=self.mine)
        self.client = Client()

    def test_anonymous_ajax_redirects_to_login_instead_of_crashing(self):
        for name, args in [('person-create-ajax', []), ('student-create-ajax', []),
                           ('registration-create-ajax', []), ('course-create-ajax', [])]:
            with self.subTest(name=name):
                response = self.client.post(reverse(name, args=args))
                self.assertEqual(response.status_code, 302)
                self.assertIn('/login/', response['Location'])

    def test_branch_manager_cannot_create_superuser(self):
        self.client.force_login(self.manager)
        response = self.client.post(reverse('person-create-ajax'), {
            'email': 'evil@example.com', 'first_name': 'e', 'branch': self.mine.pk,
            'password1': 'Strong-pass-123', 'password2': 'Strong-pass-123',
            'is_superuser': 'on', 'is_active': 'on',
        })
        self.assertEqual(response.status_code, 200, response.content)
        self.assertFalse(Person.objects.get(email='evil@example.com').is_superuser)

    def test_branch_manager_cannot_promote_self(self):
        self.client.force_login(self.manager)
        self.client.post(reverse('person-update-ajax', args=[self.manager.pk]), {
            'email': self.manager.email, 'branch': self.mine.pk, 'is_superuser': 'on', 'is_active': 'on',
        })
        self.manager.refresh_from_db()
        self.assertFalse(self.manager.is_superuser)

    def test_branch_manager_cannot_edit_or_delete_admin(self):
        self.client.force_login(self.manager)
        response = self.client.post(reverse('person-update-ajax', args=[self.admin.pk]), {
            'email': 'hijacked@example.com', 'branch': self.mine.pk, 'password1': 'x1', 'password2': 'x1',
        })
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.client.get(reverse('person-update', args=[self.admin.slug])).status_code, 403)
        self.assertEqual(self.client.post(reverse('person-delete', args=[self.admin.slug])).status_code, 403)
        self.admin.refresh_from_db()
        self.assertEqual(self.admin.email, 'admin@example.com')

    def test_admin_can_still_create_admin(self):
        self.client.force_login(self.admin)
        self.client.post(reverse('person-create-ajax'), {
            'email': 'admin2@example.com', 'first_name': 'a', 'branch': self.mine.pk,
            'password1': 'Strong-pass-123', 'password2': 'Strong-pass-123', 'is_superuser': 'on', 'is_active': 'on',
        })
        self.assertTrue(Person.objects.get(email='admin2@example.com').is_superuser)

    def test_only_admin_can_edit_roles_and_permissions(self):
        mgr_role = self.manager.employee_roles.first().role
        for codename in ['view_role', 'add_role', 'change_role', 'delete_role', 'add_permission', 'change_permission']:
            action, model_name = codename.split('_', 1)
            perm, _ = Permission.objects.get_or_create(
                codename=codename,
                defaults={'name': codename, 'app_label': 'x', 'model_name': model_name, 'action': action},
            )
            mgr_role.permissions.add(perm)
        self.client.force_login(self.manager)

        # يقدر يشوف الأدوار، بس ما يقدرش يزود صلاحيات لدوره
        self.assertEqual(self.client.get(reverse('role-list')).status_code, 200)
        self.assertEqual(self.client.get(reverse('role-update', args=[mgr_role.slug])).status_code, 403)
        all_perm = Permission.objects.get(codename='delete_role')
        response = self.client.post(reverse('role-update-ajax', args=[mgr_role.pk]), {
            'name': mgr_role.name, 'permissions': [p.pk for p in Permission.objects.all()],
        })
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.client.post(reverse('role-create-ajax'), {'name': 'x'}).status_code, 403)
        self.assertEqual(self.client.post(reverse('permission-create-ajax'), {}).status_code, 403)
        self.assertIn(all_perm, mgr_role.permissions.all())  # unchanged set still there

        self.client.force_login(self.admin)
        self.assertEqual(self.client.get(reverse('role-update', args=[mgr_role.slug])).status_code, 200)

    def test_messages_are_private(self):
        from messaging.models import InternalMessage
        third = Person.objects.create_user(email='third@example.com', password='x')
        msg = InternalMessage.objects.create(sender=self.admin, recipient=self.manager, subject='secret', body='b')

        # المستلم يقدر يفتح الرسالة من غير أي صلاحية إضافية، بس ما يعدلهاش
        self.client.force_login(self.manager)
        self.assertEqual(self.client.get(reverse('internalmessage-detail', args=[msg.pk])).status_code, 200)
        msg.refresh_from_db()
        self.assertTrue(msg.is_read)
        self.assertEqual(self.client.get(reverse('internalmessage-update', args=[msg.pk])).status_code, 404)

        # أي حد تالت ما يشوفهاش ولا يمسحها
        self.client.force_login(third)
        self.assertEqual(self.client.get(reverse('internalmessage-detail', args=[msg.pk])).status_code, 404)
        self.assertEqual(self.client.post(reverse('internalmessage-delete', args=[msg.pk])).status_code, 404)
        self.assertNotContains(self.client.get(reverse('internalmessage-list')), 'secret')
        self.assertTrue(InternalMessage.objects.filter(pk=msg.pk).exists())

    def test_notifications_are_private(self):
        from notifications.models import AppNotification
        note = AppNotification.objects.create(user=self.admin, title='private', body='b')
        self.client.force_login(self.manager)
        self.assertEqual(self.client.get(reverse('appnotification-detail', args=[note.pk])).status_code, 404)
        self.assertEqual(self.client.post(reverse('appnotification-delete', args=[note.pk])).status_code, 404)
        self.assertTrue(AppNotification.objects.filter(pk=note.pk).exists())

    def test_dropdowns_only_show_own_branch_data(self):
        master = Master.objects.create(name='m')
        data = {}
        for branch in (self.mine, self.other):
            course = Course.objects.create(master=master, branch=branch, target_level='الكل')
            student = Student.objects.create(contact=Contact.objects.create(first_name=branch.name, forth_name='x'), branch=branch)
            Account.objects.create(course=course, student=student, code=branch.code)
            data[branch.pk] = (course, student)
        course, student = data[self.mine.pk]
        self.client.force_login(self.manager)

        ctx = self.client.get(reverse('registration-list')).context
        self.assertEqual(list(ctx['courses']), [course])
        self.assertEqual(list(ctx['students']), [student])
