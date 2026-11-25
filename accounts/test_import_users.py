import csv
import tempfile
from io import StringIO
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from openpyxl import Workbook

from accounts.models import EmployeeRole, Person, Role
from core.models import Branch, Company


class ImportUsersTests(TestCase):
    def setUp(self):
        company = Company.objects.create(name='Co')
        self.riyadh = Branch.objects.create(company=company, code=9, name='الفاو الرياض')
        self.qassim = Branch.objects.create(company=company, code=11, name='الفاو التخصصي القصيم')
        self.thiqa = Branch.objects.create(company=company, code=30, name='الثقة الدائمة')
        self.role = Role.objects.create(name='موظف')
        Person.objects.create_user(email='nujood.alotaibi@ararhni.com', password='old')
        Person.objects.create_user(email='old.user@ahli-fao-grp.com', password='keep-me')
        self.tmp = Path(tempfile.mkdtemp())

    def xlsx(self, rows):
        wb = Workbook()
        ws = wb.active
        ws.append(['الاسم', 'اسم المستخدم', 'الفرع'])
        for row in rows:
            ws.append(row)
        path = self.tmp / 'users.xlsx'
        wb.save(path)
        return str(path)

    def run_cmd(self, path, *args):
        out = StringIO()
        call_command('import_users', path, '--domain', 'ahli-fao-grp.com', *args, stdout=out)
        return out.getvalue()

    ROWS = [
        ['أحمد العريني', 'ahmed.aloraini', 'فرع الفاو المتقدم بالرياض'],
        ['بدر الحربى', 'Badr26_ElHarby', 'فرع الفاو التخصصى بالقصيم'],
        ['إيمان فتحي محمود', 'eman.fathy', 'الثقة الدائمة'],
        ['ابتسام', 'nujood.alotaibi', ''],            # موجودة بإيميل تاني
        ['قديم', 'old.user', 'الثقة الدائمة'],          # موجود
        ['ناصر', 'ناصر محمد الشعلان', 'الثقة الدائمة'],  # اسم مستخدم مش صالح
        ['بدون فرع', 'no.branch', ''],
        ['مكرر', 'eman.fathy', 'الثقة الدائمة'],
    ]

    def test_dry_run_creates_nothing(self):
        output = self.run_cmd(self.xlsx(self.ROWS))
        self.assertIn('دي كانت تجربة', output)
        self.assertIn('هيتضاف: 4', output)
        self.assertEqual(Person.objects.count(), 2)

    def test_commit(self):
        output = self.run_cmd(self.xlsx(self.ROWS), '--commit')
        self.assertIn('تم.', output)
        ahmed = Person.objects.get(email='ahmed.aloraini@ahli-fao-grp.com')
        self.assertTrue(ahmed.check_password('Smart@123'))
        self.assertEqual((ahmed.first_name, ahmed.forth_name, ahmed.branch), ('أحمد', 'العريني', self.riyadh))
        self.assertTrue(EmployeeRole.objects.filter(person=ahmed, role=self.role, branch=self.riyadh).exists())
        self.assertEqual(Person.objects.get(email='badr26_elharby@ahli-fao-grp.com').branch, self.qassim)
        self.assertEqual(Person.objects.get(email='eman.fathy@ahli-fao-grp.com').branch, self.thiqa)
        no_branch = Person.objects.get(email='no.branch@ahli-fao-grp.com')
        self.assertIsNone(no_branch.branch)
        self.assertFalse(no_branch.employee_roles.exists())
        # الموجود ماتغيرش، والموجود بإيميل تاني ماتعملوش حساب
        self.assertTrue(Person.objects.get(email='old.user@ahli-fao-grp.com').check_password('keep-me'))
        self.assertFalse(Person.objects.filter(email='nujood.alotaibi@ahli-fao-grp.com').exists())
        self.assertIn('موجود بإيميل تاني', output)
        self.assertIn('اسم مستخدم مش صالح', output)
        self.assertIn('مكرر في الشيت', output)
        self.assertEqual(Person.objects.count(), 6)

    def test_unknown_branch_stops_and_map_fixes(self):
        path = self.xlsx([['هيا', 'haya', 'فرع المورد الوافي']])
        with self.assertRaises(CommandError):
            self.run_cmd(path, '--commit')
        self.assertFalse(Person.objects.filter(email='haya@ahli-fao-grp.com').exists())
        self.run_cmd(path, '--map', 'فرع المورد الوافي=30', '--commit')
        self.assertEqual(Person.objects.get(email='haya@ahli-fao-grp.com').branch, self.thiqa)

    def test_csv_and_domain_without_extension(self):
        path = self.tmp / 'users.csv'
        with open(path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['الاسم', 'اسم المستخدم', 'الفرع'])
            writer.writerow(['يوسف', 'yousef.x', 'فرع الفاو المتقدم بالرياض'])
        self.run_cmd(str(path), '--commit')
        self.assertTrue(Person.objects.filter(email='yousef.x@ahli-fao-grp.com').exists())
        with self.assertRaises(CommandError):
            call_command('import_users', str(path), '--domain', 'ahli-fao-grp', stdout=StringIO())
