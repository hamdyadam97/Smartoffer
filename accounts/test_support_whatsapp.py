from django.test import TestCase, override_settings
from django.urls import reverse

from accounts.models import Person


class SupportWhatsAppTests(TestCase):
    def setUp(self):
        self.client.force_login(Person.objects.create_user(email='a@example.com', password='x', is_superuser=True))

    def test_default_number(self):
        response = self.client.get(reverse('dashboard'))
        self.assertContains(response, 'https://wa.me/966538766419')
        self.assertNotContains(response, '966569736794')

    @override_settings(SUPPORT_WHATSAPP='966500000000')
    def test_number_from_settings(self):
        self.assertContains(self.client.get(reverse('dashboard')), 'https://wa.me/966500000000')
