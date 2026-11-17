import os
import sqlite3
import tempfile
from io import StringIO

from django.core.management import CommandError, call_command
from django.test import TestCase

from core.models import Branch, Company
from courses.models import Course
from permits.models import Permit, PermitTemplate
from permits.services import render_html
from students.models import Contact, Student

SCHEMA = """
create table institutes_institute (id integer primary key, name text, city text, license_number text, phone text,
  email text, address text, logo text, signature_image text, stamp_image text, background_img text,
  registration_officer_id integer, is_deleted bool default 0);
create table accounts_user (id integer primary key, email text, username text, first_name text, last_name text);
create table programs_diploma (id integer primary key, name text, is_deleted bool default 0, duration text,
  duration_months integer, hours integer, start_date text, end_date text);
create table programs_course (id integer primary key, name text, is_deleted bool default 0, duration text,
  duration_months integer, hours integer, start_date text, end_date text);
create table programs_diploma_institutes (id integer primary key, diploma_id integer, institute_id integer);
create table programs_course_institutes (id integer primary key, course_id integer, institute_id integer);
create table clients_client (id integer primary key, institute_id integer, national_id text, phone text,
  full_name text, first_name text, last_name text, birth_date text, address text);
create table permissions_permissionslip (id integer primary key, permission_number text, client_id integer,
  institute_id integer, diploma_id integer, course_id integer, issue_date text, expiry_date text, status text,
  notes text, study_mode text, issued_by_id integer, referral_employee_id integer, issued_from_public bool,
  referral_code text, created_at text, is_deleted bool default 0);
create table permissions_permissiontemplate (id integer primary key, institute_id integer, header_content text,
  body_content text, footer_content text, custom_css text, font_family text, page_size text, orientation text,
  is_deleted bool default 0);
"""


class ImportMashahedTests(TestCase):
    def setUp(self):
        company = Company.objects.create(name='Co')
        self.riyadh = Branch.objects.create(company=company, code=1, name='الرياض')
        self.hafr = Branch.objects.create(company=company, code=2, name='حفر الباطن')
        # طالب موجود في Smart Offer بنفس رقم الهوية
        self.existing = Student.objects.create(
            contact=Contact.objects.create(first_name='سارة', forth_name='علي', identity_number='1000000002'),
            branch=self.riyadh)
        fd, self.path = tempfile.mkstemp(suffix='.sqlite3')
        os.close(fd)
        db = sqlite3.connect(self.path)
        db.executescript(SCHEMA)
        db.executemany('insert into institutes_institute (id, name, city, license_number, registration_officer_id) values (?,?,?,?,?)', [
            (1, 'معهد الفاو العالي للتدريب بالرياض', 'الرياض', 'LIC-R', 1),
            (2, 'معهد الفاو بحفر الباطن', 'حفر الباطن', '', None),
        ])
        db.execute("insert into accounts_user values (1, 'old@example.com', 'old', 'خالد', 'سعد')")
        db.execute("insert into programs_diploma (id, name, duration_months, end_date) values (1, 'دبلومة إدارة الموارد البشرية', 24, '2027-06-30')")
        db.execute("insert into programs_diploma_institutes (diploma_id, institute_id) values (1, 1), (1, 2)")
        db.execute("insert into programs_course (id, name, duration) values (1, 'تصميم واجهات', '3 شهور')")
        db.execute("insert into programs_course_institutes (course_id, institute_id) values (1, 2)")
        db.executemany('insert into clients_client (id, institute_id, national_id, phone, full_name) values (?,?,?,?,?)', [
            (1, 1, '1000000001', '0501111111', 'محمد أحمد عبدالله العتيبي'),
            (2, 1, '1000000002', '0502222222', 'سارة علي'),
        ])
        db.executemany('insert into permissions_permissionslip (id, permission_number, client_id, institute_id, diploma_id, course_id, issue_date, expiry_date, status, notes, study_mode, issued_by_id, issued_from_public, referral_code, created_at, is_deleted) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', [
            (1, 'PERM-2026-111111', 1, 1, 1, None, '2026-07-25', '2027-06-30', 'active', '', 'online', 1, 0, '', '2026-07-25 20:06:20.783181', 0),
            (2, 'PERM-2026-222222', 2, 2, None, 1, '2026-08-01', '2026-11-01', 'cancelled', 'x', '', None, 1, 'EMP001', '2026-08-01 10:00:00', 0),
            (3, 'PERM-2026-333333', 2, 2, None, 1, '2026-08-01', '2026-11-01', 'active', '', '', None, 0, '', None, 1),
        ])
        db.execute("insert into permissions_permissiontemplate (institute_id, body_content, font_family, page_size, orientation) values "
                   "(1, '<p>{{ institute.name }} | {{ client.full_name }} | {{ program.duration_months }} شهر</p>', 'cairo', 'A4', 'portrait')")
        db.commit()
        db.close()

    def tearDown(self):
        os.remove(self.path)

    def run_import(self, *args):
        out = StringIO()
        call_command('import_mashahed', '--source', self.path, *args, stdout=out)
        return out.getvalue()

    def test_dry_run_changes_nothing(self):
        output = self.run_import()
        self.assertIn('دي كانت تجربة', output)
        self.assertIn('مشاهد: 2 اتنقلت', output)
        self.assertFalse(Permit.objects.exists())
        self.assertEqual(Student.objects.count(), 1)

    def test_commit_imports_everything(self):
        output = self.run_import('--commit')
        self.assertIn('تم النقل', output)
        self.assertEqual(Permit.objects.count(), 2)  # الممسوح ما اتنقلش

        first = Permit.objects.get(number='PERM-2026-111111')
        self.assertEqual((first.branch, first.status, first.study_mode), (self.riyadh, 'active', 'online'))
        self.assertEqual(first.student.contact.identity_number, '1000000001')
        self.assertEqual(first.student.contact.get_full_name(), 'محمد أحمد عبدالله العتيبي')
        self.assertEqual(first.program_name, 'دبلوم إدارة الموارد البشرية')
        self.assertEqual(str(first.created_at.date()), '2026-07-25')
        self.assertIn('أصدره في النظام القديم: خالد سعد', first.notes)
        # دبلومة في معهدين -> تخصص لكل الفروع
        self.assertIsNone(first.course.branch)
        self.assertEqual(first.course.period, '24 شهر')

        second = Permit.objects.get(number='PERM-2026-222222')
        self.assertEqual(second.student, self.existing)  # اتربط بالطالب الموجود برقم الهوية
        self.assertEqual((second.branch, second.status, second.referral_code), (self.hafr, 'cancelled', 'EMP001'))
        self.assertEqual(second.course.branch, self.hafr)  # دورة في معهد واحد -> تخصص الفرع ده
        self.assertEqual(second.course.get_display_name(), 'دورة تصميم واجهات')

        template = PermitTemplate.objects.get(branch=self.riyadh)
        self.assertEqual(template.registration_officer, 'خالد سعد')
        self.assertIn('معهد الفاو العالي للتدريب بالرياض | محمد أحمد عبدالله العتيبي | 24 شهر', render_html(first))
        self.assertEqual(self.riyadh.__class__.objects.get(pk=self.riyadh.pk).licence_code, 'LIC-R')

    def test_running_twice_does_not_duplicate(self):
        self.run_import('--commit')
        output = self.run_import('--commit')
        self.assertIn('مشاهد: 0 اتنقلت، 3 اتخطت', output)
        self.assertEqual(Permit.objects.count(), 2)
        self.assertEqual(Course.objects.count(), 2)
        self.assertEqual(Student.objects.count(), 2)

    def test_unmatched_institute_stops_without_changes(self):
        Branch.objects.filter(pk=self.hafr.pk).update(name='الدمام')
        with self.assertRaisesMessage(CommandError, 'صلّح ربط المعاهد'):
            self.run_import('--commit')
        self.assertFalse(Permit.objects.exists())

    def test_manual_map_and_create_branches(self):
        self.run_import('--map', '2=1', '--commit')
        self.assertEqual(Permit.objects.get(number='PERM-2026-222222').branch, self.riyadh)
        Permit.objects.all().delete()
        Branch.objects.filter(pk=self.hafr.pk).update(name='الدمام')
        self.run_import('--create-branches', '--commit')
        self.assertEqual(Permit.objects.get(number='PERM-2026-222222').branch.name, 'معهد الفاو بحفر الباطن')
