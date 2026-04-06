from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from core.models import Company, Branch
from courses.models import Master, Course
from students.models import Contact, Student
from registrations.models import Account
from .models import Payment, PaymentOut, Deposit, Withdraw, Offer, Call

User = get_user_model()


class PaymentModelTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Test Co')
        self.branch = Branch.objects.create(name='Branch', code=1, company=self.company)
        self.user = User.objects.create_user(
            email='test@test.com',
            password='test123',
            first_name='Test',
            forth_name='User'
        )
        
        # Create course and registration
        self.master = Master.objects.create(
            name='برمجة',
            code=1,
            branch=self.branch,
            last_person=self.user
        )
        self.course = Course.objects.create(
            master=self.master,
            code=1,
            last_person=self.user
        )
        self.contact = Contact.objects.create(
            first_name='محمد',
            forth_name='أحمد',
            mobile='0501234567',
            identity_number='1234567890'
        )
        self.student = Student.objects.create(
            contact=self.contact,
            level='مبتدئ'
        )
        self.account = Account.objects.create(
            course=self.course,
            student=self.student,
            code=1,
            course_price=1000,
            last_person=self.user
        )
        
        self.payment = Payment.objects.create(
            account=self.account,
            code=1001,
            amount_number=Decimal('500.00'),
            amount_string='خمسمائة ريال',
            type='ايرادات اساسية',
            last_person=self.user
        )

    def test_payment_creation(self):
        self.assertEqual(self.payment.amount_number, Decimal('500.00'))
        self.assertEqual(self.payment.type, 'ايرادات اساسية')

    def test_payment_tax(self):
        tax = self.payment.get_tax()
        self.assertEqual(tax, 25.0)  # 5% of 500

    def test_payment_with_tax(self):
        total = self.payment.get_amount_with_tax()
        self.assertEqual(total, 525.0)


class OfferModelTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Test Co')
        self.branch = Branch.objects.create(name='Branch', code=1, company=self.company)
        self.user = User.objects.create_user(
            email='test@test.com',
            password='test123',
            first_name='Test',
            forth_name='User'
        )
        self.master = Master.objects.create(
            name='برمجة',
            code=1,
            branch=self.branch,
            last_person=self.user
        )
        self.offer = Offer.objects.create(
            master=self.master,
            code=1,
            customer_name='عميل تجريبي',
            customer_mobile='0501234567',
            master_payment_type='نقدي',
            master_price=Decimal('2000.00'),
            master_discount_amount=Decimal('10.00'),
            last_person=self.user
        )

    def test_offer_creation(self):
        self.assertEqual(self.offer.customer_name, 'عميل تجريبي')
        self.assertEqual(self.offer.master_price, Decimal('2000.00'))

    def test_offer_get_net(self):
        net = self.offer.get_net()
        # 2000 - (2000 * 10 / 100) = 1800
        self.assertAlmostEqual(net, 1800.0, places=1)

    def test_offer_get_discount(self):
        discount = self.offer.get_discount()
        self.assertEqual(discount, 200.0)


class CallModelTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Test Co')
        self.branch = Branch.objects.create(name='Branch', code=1, company=self.company)
        self.user = User.objects.create_user(
            email='test@test.com',
            password='test123',
            first_name='Test',
            forth_name='User'
        )
        self.master = Master.objects.create(
            name='برمجة',
            code=1,
            branch=self.branch,
            last_person=self.user
        )
        self.offer = Offer.objects.create(
            master=self.master,
            code=1,
            customer_name='عميل تجريبي',
            customer_mobile='0501234567',
            last_person=self.user
        )
        self.call = Call.objects.create(
            offer=self.offer,
            person=self.user,
            call_type='OUTGOING',
            duration=120,
            notes='مكالمة متابعة'
        )

    def test_call_creation(self):
        self.assertEqual(self.call.duration, 120)
        self.assertEqual(self.call.call_type, 'OUTGOING')


class PaymentOutModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@test.com',
            password='test123',
            first_name='Test',
            forth_name='User'
        )
        self.payment_out = PaymentOut.objects.create(
            code=1001,
            amount_number=Decimal('1000.00'),
            receiver_name='محمد أحمد',
            reason='مصاريف تشغيل',
            last_person=self.user
        )

    def test_payment_out_creation(self):
        self.assertEqual(self.payment_out.receiver_name, 'محمد أحمد')
        self.assertEqual(self.payment_out.amount_number, Decimal('1000.00'))


class DepositModelTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Test Co')
        self.branch = Branch.objects.create(name='Branch', code=1, company=self.company)
        self.user = User.objects.create_user(
            email='test@test.com',
            password='test123',
            first_name='Test',
            forth_name='User'
        )
        from core.models import Bank
        self.bank = Bank.objects.create(
            branch=self.branch,
            name='بنك الراجحي',
            account_number='123456789'
        )
        self.deposit = Deposit.objects.create(
            code=1001,
            amount=Decimal('5000.00'),
            bank=self.bank,
            last_person=self.user
        )

    def test_deposit_creation(self):
        self.assertEqual(self.deposit.amount, Decimal('5000.00'))
        self.assertEqual(str(self.deposit.bank), 'بنك الراجحي')
