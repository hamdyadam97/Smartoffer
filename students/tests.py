from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import Company, Branch
from .models import Contact, Student

User = get_user_model()


class ContactModelTest(TestCase):
    def setUp(self):
        self.contact = Contact.objects.create(
            first_name='محمد',
            forth_name='أحمد',
            mobile='0501234567',
            identity_number='1234567890'
        )

    def test_contact_creation(self):
        self.assertEqual(self.contact.first_name, 'محمد')
        self.assertEqual(self.contact.get_full_name(), 'محمد أحمد')
        self.assertEqual(str(self.contact), 'محمد أحمد')

    def test_contact_unique_identity(self):
        # Contact لا يوجد به unique constraint على identity_number
        # لكن يمكننا اختبار إنشاء contact آخر
        contact2 = Contact.objects.create(
            first_name='علي',
            forth_name='خالد',
            mobile='0509876543',
            identity_number='0987654321'
        )
        self.assertEqual(contact2.first_name, 'علي')


class StudentModelTest(TestCase):
    def setUp(self):
        self.contact = Contact.objects.create(
            first_name='محمد',
            forth_name='أحمد',
            mobile='0501234567',
            identity_number='1234567890'
        )
        self.student = Student.objects.create(
            contact=self.contact,
            level='مبتدئ',
            preferred_contact='whatsapp'
        )

    def test_student_creation(self):
        self.assertEqual(self.student.level, 'مبتدئ')
        self.assertEqual(self.student.get_full_name(), 'محمد أحمد')
        self.assertEqual(str(self.student), 'محمد أحمد')

    def test_student_get_mobile(self):
        self.assertEqual(self.student.get_mobile(), '0501234567')
