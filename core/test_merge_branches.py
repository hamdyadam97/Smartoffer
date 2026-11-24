from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from accounts.models import EmployeeRole, Person, Role
from core.models import Bank, Branch, Company
from courses.models import Course
from offers.models import StudentOffer
from permits.models import Permit, PermitTemplate
from registrations.models import Account
from students.models import Contact, Student


class MergeBranchesTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Co')
        self.men = Branch.objects.create(company=self.company, code=9, name='الفاو الرياض (رجال)')
        self.women = Branch.objects.create(company=self.company, code=10, name='الفاو الرياض (نساء)',
                                           licence_code='LIC-W', phone1='0111')
        self.other = Branch.objects.create(company=self.company, code=20, name='آفاق التطور')
        self.single = Branch.objects.create(company=self.company, code=45, name='طريف (رجال)')
        self.role = Role.objects.create(name='موظف')
        self.admin = Person.objects.create_user(email='admin@example.com', password='x', is_superuser=True)

        # بيانات على فرع النساء
        self.employee = Person.objects.create_user(email='w@example.com', password='x', branch=self.women)
        EmployeeRole.objects.create(person=self.employee, role=self.role, branch=self.women)
        EmployeeRole.objects.create(person=self.employee, role=self.role, branch=self.men)  # مكرر بعد الدمج
        self.student = Student.objects.create(contact=Contact.objects.create(first_name='سارة', forth_name='علي'),
                                              branch=self.women)
        self.course_m = Course.objects.create(program_type='دبلوم', name='موارد بشرية', branch=self.men)
        self.course_w = Course.objects.create(program_type='دبلوم', name='موارد بشرية', branch=self.women)
        self.offer = StudentOffer.objects.create(title='عرض', content='x', branch=self.women, course=self.course_w,
                                                 created_by=self.admin)
        self.permit = Permit.objects.create(student=self.student, branch=self.women, course=self.course_w)
        PermitTemplate.objects.create(branch=self.men, body_content='رجال')
        PermitTemplate.objects.create(branch=self.women, body_content='نساء')
        Bank.objects.create(branch=self.women, name='الراجحي', account_number='1')

    def run_cmd(self, *args):
        out = StringIO()
        call_command('merge_branches', *args, stdout=out)
        return out.getvalue()

    def test_dry_run_changes_nothing(self):
        output = self.run_cmd()
        self.assertIn('دي كانت تجربة', output)
        self.assertTrue(Branch.objects.filter(pk=self.women.pk).exists())
        self.assertEqual(Branch.objects.get(pk=self.men.pk).name, 'الفاو الرياض (رجال)')

    def test_merge_moves_everything(self):
        output = self.run_cmd('--commit')
        self.assertIn('تم الدمج', output)
        self.assertFalse(Branch.objects.filter(pk=self.women.pk).exists())
        men = Branch.objects.get(pk=self.men.pk)
        self.assertEqual(men.name, 'الفاو الرياض')
        self.assertEqual((men.licence_code, men.phone1), ('LIC-W', '0111'))  # اتكملت من فرع النساء

        self.student.refresh_from_db()
        self.offer.refresh_from_db()
        self.permit.refresh_from_db()
        self.employee.refresh_from_db()
        self.assertEqual((self.student.branch, self.offer.branch, self.permit.branch, self.employee.branch),
                         (men, men, men, men))
        # الدور المكرر اتشال، والتخصص المكرر اتدمج والعرض والمشهد اتنقلوا عليه
        self.assertEqual(list(self.employee.employee_roles.values_list('branch', flat=True)), [men.pk])
        self.assertEqual(Course.objects.filter(branch=men).count(), 1)
        self.assertEqual((self.offer.course, self.permit.course), (self.course_m, self.course_m))
        # قالب المشهد: بيفضل قالب الفرع الأساسي
        self.assertEqual(PermitTemplate.objects.get(branch=men).body_content, 'رجال')
        self.assertEqual(Bank.objects.get().branch, men)
        # فرع لوحده عليه «(رجال)» بيتشال من اسمه بس، والفرع العادي مابيتلمسش
        self.assertEqual(Branch.objects.get(pk=self.single.pk).name, 'طريف')
        self.assertEqual(Branch.objects.get(pk=self.other.pk).name, 'آفاق التطور')

    def test_registrations_follow_student(self):
        account = Account.objects.create(student=self.student, course=self.course_w, code=1)
        self.run_cmd('--commit')
        account.refresh_from_db()
        self.assertEqual(account.course, self.course_m)
        self.assertEqual(account.student.branch_id, self.men.pk)

    def test_manual_pair_and_keep_names(self):
        self.run_cmd('--pair', '9,10', '--keep-names', '--commit')
        self.assertEqual(Branch.objects.get(pk=self.men.pk).name, 'الفاو الرياض (رجال)')
        self.assertFalse(Branch.objects.filter(pk=self.women.pk).exists())
        self.assertEqual(Branch.objects.get(pk=self.single.pk).name, 'طريف (رجال)')  # --pair بيعمل الزوج ده بس
