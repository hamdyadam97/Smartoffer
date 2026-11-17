from datetime import date, timedelta
from io import BytesIO

from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from openpyxl import load_workbook

from accounts.models import EmployeeRole, Permission, Person, Role
from core.models import Branch, Company
from courses.models import Course
from offers.models import OfferRecipient, StudentOffer
from permits.models import Permit
from students.models import Contact, Student


class LiveReportTests(TestCase):
    def setUp(self):
        company = Company.objects.create(name='Co')
        self.riyadh = Branch.objects.create(company=company, code=1, name='الرياض')
        self.hafr = Branch.objects.create(company=company, code=2, name='حفر الباطن')
        self.course = Course.objects.create(program_type='دبلوم', name='موارد بشرية', branch=None)
        self.admin = Person.objects.create_user(email='admin@example.com', password='x', is_superuser=True)
        self.ali = Person.objects.create_user(email='ali@example.com', password='x', first_name='علي', branch=self.riyadh)
        self.web = Client()
        self.web.force_login(self.admin)

        student = Student.objects.create(contact=Contact.objects.create(
            first_name='محمد', forth_name='العتيبي', identity_number='1012345678', mobile='0501'), branch=self.riyadh)
        for status in ('اشترك', 'مرسل'):
            offer = StudentOffer.objects.create(title='عرض', content='x', branch=self.riyadh, course=self.course,
                                                created_by=self.ali, price=3500, status='مرسلة')
            OfferRecipient.objects.create(offer=offer, student=student, channel='whatsapp', status=status)
        old = StudentOffer.objects.create(title='قديم', content='x', branch=self.hafr, created_by=self.admin)
        StudentOffer.objects.filter(pk=old.pk).update(created_at=timezone.now() - timedelta(days=400))
        Permit.objects.create(student=student, branch=self.riyadh, course=self.course, issued_by=self.ali)
        Permit.objects.create(student=student, branch=self.riyadh, course=self.course, issued_from_public=True,
                              referral_employee=self.ali, status=Permit.STATUS_CANCELLED)

    def get(self, **params):
        return self.web.get(reverse('report-live'), params)

    def test_branches_report_this_month(self):
        table = self.get(type='branches').context['table']
        riyadh = next(r for r in table.rows if r[0] == 'الرياض')
        # العروض، المستلمين، اشتركوا، النسبة، المشاهد، ملغية، من البوابة، طلاب جدد
        self.assertEqual(riyadh[1:], [2, 2, 1, '50%', 2, 1, 1, 1])
        hafr = next(r for r in table.rows if r[0] == 'حفر الباطن')
        self.assertEqual(hafr[1], 0)  # العرض القديم برة الفترة
        self.assertEqual(table.totals[1], 2)

    def test_all_periods_includes_old(self):
        table = self.get(type='branches', period='all').context['table']
        self.assertEqual(table.totals[1], 3)

    def test_custom_period(self):
        start = (timezone.localdate() - timedelta(days=410)).isoformat()
        end = (timezone.localdate() - timedelta(days=390)).isoformat()
        table = self.get(type='branches', period='custom', start=start, end=end).context['table']
        self.assertEqual(table.totals[1], 1)

    def test_employees_report(self):
        table = self.get(type='employees').context['table']
        ali = next(r for r in table.rows if r[0].startswith('علي'))
        self.assertEqual(ali[2:], [2, 2, 1, '50%', 1, 1])
        self.assertEqual(table.rows[0][0], ali[0])  # الأكتر شغل الأول

    def test_detail_reports(self):
        offers = self.get(type='offers').context['table']
        self.assertEqual(len(offers.rows), 2)
        self.assertIn('محمد العتيبي', offers.rows[0][6])
        permits = self.get(type='permits', branch=self.riyadh.pk).context['table']
        self.assertEqual(len(permits.rows), 2)
        self.assertEqual({r[8] for r in permits.rows}, {'نشط', 'ملغي'})
        self.assertIn('البوابة العامة', {r[9] for r in permits.rows})

    def test_monthly_report(self):
        table = self.get(type='monthly', period='all').context['table']
        self.assertEqual(len(table.rows), 2)
        self.assertEqual(table.totals[1:], [3, 2, 1, '50%', 2])

    def test_excel_export(self):
        response = self.get(type='branches', export='xlsx')
        self.assertIn('spreadsheetml', response['Content-Type'])
        ws = load_workbook(BytesIO(response.content)).active
        values = [[c.value for c in row] for row in ws.iter_rows()]
        self.assertEqual(values[0][0], 'تقرير الفروع')
        self.assertIn('الفرع', [v for row in values for v in row])
        self.assertIn('الإجمالي', [row[0] for row in values])

    def test_page_renders_and_sidebar_link(self):
        response = self.get(type='permits')
        self.assertContains(response, 'تصدير Excel')
        self.assertContains(response, reverse('report-live'))

    def test_employee_sees_only_own_branches(self):
        role = Role.objects.create(name='r')
        perm, _ = Permission.objects.get_or_create(codename='view_reportsnapshot', defaults={
            'name': 'x', 'app_label': 'reports', 'model_name': 'reportsnapshot', 'action': 'view'})
        role.permissions.add(perm)
        EmployeeRole.objects.create(person=self.ali, role=role, branch=self.hafr)
        self.web.force_login(self.ali)
        table = self.get(type='branches', period='all').context['table']
        self.assertEqual([r[0] for r in table.rows], ['حفر الباطن'])
        # حتى لو طلب فرع مش بتاعه
        table = self.get(type='permits', branch=self.riyadh.pk, period='all').context['table']
        self.assertEqual(table.rows, [])

    def test_no_permission(self):
        self.web.force_login(Person.objects.create_user(email='x@example.com', password='x'))
        self.assertEqual(self.get().status_code, 403)
