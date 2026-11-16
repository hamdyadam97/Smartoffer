from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse
from openpyxl import Workbook, load_workbook

from accounts.models import Person
from core.models import Branch, Company
from courses.models import Course
from offers.importer import COLUMNS
from offers.models import OfferRecipient, StudentOffer
from students.models import Contact, Student

HEADERS = [title for title, _ in COLUMNS]


def excel(*rows, headers=HEADERS):
    wb = Workbook()
    ws = wb.active
    ws.append(headers)
    for row in rows:
        ws.append(list(row))
    buffer = BytesIO()
    wb.save(buffer)
    return SimpleUploadedFile('offers.xlsx', buffer.getvalue())


def row(name='محمد أحمد علي', phone='0501234567', email='', branch='', course='دبلوم موارد بشرية',
        price=3500, price_description='', date='2025-03-15', status='', channel='', content=''):
    return [name, phone, email, branch, course, price, price_description, date, status, channel, content]


class OfferImportTests(TestCase):
    def setUp(self):
        company = Company.objects.create(name='Co')
        self.branch = Branch.objects.create(company=company, code=1, name='الرياض')
        self.other = Branch.objects.create(company=company, code=2, name='حفر الباطن')
        self.course = Course.objects.create(program_type='دبلوم', name='موارد بشرية', branch=None)
        self.admin = Person.objects.create_user(email='admin@example.com', password='x', is_superuser=True)
        self.client = Client()
        self.client.force_login(self.admin)

    def post(self, file, branch=None, register=False):
        data = {'file': file, 'branch': (branch or self.branch).pk}
        if register:
            data['register_students'] = 'on'
        return self.client.post(reverse('studentoffer-import'), data, follow=True)

    def test_template_download(self):
        response = self.client.get(reverse('studentoffer-import-template'))
        self.assertEqual(response.status_code, 200)
        ws = load_workbook(BytesIO(response.content)).active
        self.assertEqual([c.value for c in ws[1]], HEADERS)

    def test_unregistered_person_kept_as_name_and_phone(self):
        response = self.post(excel(row()))
        self.assertContains(response, 'تم استيراد 1 عرض')
        offer = StudentOffer.objects.get()
        recipient = offer.recipients.get()
        self.assertIsNone(recipient.student)
        self.assertEqual((recipient.contact_name, recipient.contact_phone), ('محمد أحمد علي', '0501234567'))
        self.assertEqual((offer.course, offer.title, offer.branch), (self.course, 'دبلوم موارد بشرية', self.branch))
        self.assertEqual((offer.status, str(offer.created_at.date())), ('مرسلة', '2025-03-15'))
        self.assertEqual(Student.objects.count(), 0)

    def test_existing_student_is_linked_by_phone(self):
        student = Student.objects.create(
            contact=Contact.objects.create(first_name='محمد', forth_name='علي', mobile='966501234567'),
            branch=self.branch,
        )
        response = self.post(excel(row(phone='0501234567')))
        self.assertContains(response, 'اتربطوا بطلاب مسجلين')
        self.assertEqual(OfferRecipient.objects.get().student, student)

    def test_register_option_creates_students(self):
        response = self.post(excel(row(), row(name='سارة', phone='0559998887')), register=True)
        self.assertContains(response, 'اتسجل 2 طالب جديد')
        student = Student.objects.get(contact__mobile='0501234567')
        self.assertEqual((student.contact.first_name, student.contact.forth_name, student.branch),
                         ('محمد', 'علي', self.branch))
        self.assertEqual(OfferRecipient.objects.filter(student__isnull=False).count(), 2)

    def test_unknown_specialization_kept_as_title(self):
        response = self.post(excel(row(course='دورة تصوير')))
        self.assertContains(response, 'دورة تصوير')
        offer = StudentOffer.objects.get()
        self.assertIsNone(offer.course)
        self.assertEqual(offer.title, 'دورة تصوير')

    def test_branch_column_and_branch_specialization_preferred(self):
        branch_course = Course.objects.create(program_type='دبلوم', name='موارد بشرية', branch=self.other)
        self.post(excel(row(branch='حفر الباطن'), row(branch='2', phone='0551112223')))
        self.assertEqual(set(StudentOffer.objects.values_list('branch', 'course')), {(self.other.pk, branch_course.pk)})

    def test_any_bad_row_imports_nothing(self):
        response = self.post(excel(row(), row(name='', phone='055'), row(branch='فرع مش موجود'), row(date='بكرة')))
        self.assertContains(response, 'ما اتسجلش أي عرض')
        self.assertContains(response, 'صف 3: الاسم فاضي')
        self.assertContains(response, 'صف 4')
        self.assertContains(response, 'صف 5')
        self.assertEqual(StudentOffer.objects.count(), 0)

    def test_wrong_file(self):
        response = self.post(SimpleUploadedFile('x.xlsx', b'not excel'))
        self.assertContains(response, 'مش ملف إكسل')
        response = self.post(excel(row(), headers=['a', 'b']))
        self.assertContains(response, 'عناوين الأعمدة')

    def test_employee_cannot_import_into_other_branch(self):
        from accounts.models import EmployeeRole, Permission, Role
        employee = Person.objects.create_user(email='e@example.com', password='x', branch=self.branch)
        role = Role.objects.create(name='r')
        for action in ('add', 'view'):
            perm, _ = Permission.objects.get_or_create(
                codename=f'{action}_studentoffer',
                defaults={'name': 'x', 'app_label': 'offers', 'model_name': 'studentoffer', 'action': action},
            )
            role.permissions.add(perm)
        EmployeeRole.objects.create(person=employee, role=role, branch=self.branch)
        self.client.force_login(employee)
        response = self.post(excel(row(branch='حفر الباطن')))
        self.assertContains(response, 'مش موجود أو مش مسموح لك')
        self.assertEqual(StudentOffer.objects.count(), 0)

    def test_pdf_works_for_offer_linked_to_student(self):
        """جهة الاتصال مالهاش إيميل: الـ PDF كان بيقع لما العرض مربوط بطالب."""
        Student.objects.create(
            contact=Contact.objects.create(first_name='محمد', forth_name='علي', mobile='0501234567'), branch=self.branch,
        )
        self.post(excel(row(email='m@example.com')))
        offer = StudentOffer.objects.get()
        response = self.client.get(reverse('studentoffer-export-pdf', args=[offer.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content.startswith(b'%PDF'))
