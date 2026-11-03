from django.test import TestCase, Client
from django.urls import reverse

from accounts.models import Person
from core.models import Bank, Branch, Company
from courses.models import Course, Master
from finance.models import Call, Deposit, Offer, Payment
from offers.models import OfferRecipient, StudentOffer
from registrations.models import Account
from students.models import Contact, Student


class BranchDeleteTests(TestCase):
    def setUp(self):
        self.user = Person.objects.create_user(
            email='admin@example.com', password='testpass123', first_name='A', forth_name='B',
        )
        self.user.is_superuser = True
        self.user.save()
        self.client = Client()
        self.client.force_login(self.user)

        company = Company.objects.create(name='Co')
        self.branch = Branch.objects.create(company=company, code=1, name='Target')
        self.other = Branch.objects.create(company=company, code=2, name='Other')

    def _fill(self, branch, n):
        master = Master.objects.create(branch=branch, name=f'm{n}')
        course = Course.objects.create(master=master, target_level='الكل')
        student = Student.objects.create(
            contact=Contact.objects.create(first_name=f's{n}', forth_name='x'), branch=branch,
        )
        account = Account.objects.create(course=course, student=student, code=n)
        Payment.objects.create(account=account, code=n, amount_number=50)
        offer = Offer.objects.create(master=master, code=n, customer_name='c')
        Call.objects.create(offer=offer, person=self.user)
        student_offer = StudentOffer.objects.create(title='t', content='c', branch=branch, created_by=self.user)
        OfferRecipient.objects.create(offer=student_offer, student=student, channel='whatsapp')
        bank = Bank.objects.create(branch=branch, name='b', account_number='1')
        Deposit.objects.create(code=n, amount=10, bank=bank)
        Person.objects.create_user(
            email=f'emp{n}@example.com', password='x', first_name='E', forth_name='E', branch=branch,
        )

    def test_delete_branch_deletes_all_related_data_only_for_that_branch(self):
        self._fill(self.branch, 1)
        self._fill(self.other, 2)

        confirm = self.client.get(reverse('branch-delete', args=[self.branch.slug]))
        self.assertIn(('تسجيل', 1), confirm.context['related_counts'])

        response = self.client.post(reverse('branch-delete', args=[self.branch.slug]))

        self.assertRedirects(response, reverse('branch-list'))
        self.assertFalse(Branch.objects.filter(pk=self.branch.pk).exists())
        for model in [Master, Course, Student, Contact, Account, Payment, Offer, Call,
                      StudentOffer, OfferRecipient, Bank, Deposit]:
            self.assertEqual(model.objects.count(), 1, model.__name__)
        self.assertFalse(Person.objects.filter(email='emp1@example.com').exists())
        self.assertTrue(Person.objects.filter(email='emp2@example.com').exists())
        self.assertTrue(Person.objects.filter(pk=self.user.pk).exists())

    def test_delete_branch_keeps_current_user_even_if_main_branch(self):
        self.user.branch = self.branch
        self.user.save()
        self.client.post(reverse('branch-delete', args=[self.branch.slug]))
        self.assertFalse(Branch.objects.filter(pk=self.branch.pk).exists())
        self.assertTrue(Person.objects.filter(pk=self.user.pk).exists())
