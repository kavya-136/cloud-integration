from django.test import TestCase
from django.urls import reverse

from accounts.models import CustomUser


class DashboardTests(TestCase):
    def test_index_page_renders(self):
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_requires_authentication(self):
        response = self.client.get(reverse('dashboard:dashboard'))
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={reverse('dashboard:dashboard')}")

    def test_dashboard_page_renders_for_authenticated_user(self):
        user = CustomUser.objects.create_user(username='dashuser', password='StrongPass1!')
        self.client.force_login(user)
        response = self.client.get(reverse('dashboard:dashboard'))
        self.assertEqual(response.status_code, 200)
