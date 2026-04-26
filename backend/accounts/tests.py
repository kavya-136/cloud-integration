from django.test import TestCase
from django.urls import reverse

from .models import CustomUser


class AccountsTests(TestCase):
    def test_custom_user_model_can_be_created(self):
        user = CustomUser.objects.create_user(username='tester', password='securepass123')
        self.assertEqual(user.username, 'tester')
        self.assertNotEqual(user.password, 'securepass123')
        self.assertTrue(user.check_password('securepass123'))

    def test_login_page_renders(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)

    def test_signup_page_renders(self):
        response = self.client.get(reverse('accounts:signup'))
        self.assertEqual(response.status_code, 200)

    def test_signup_invalid_username_fails(self):
        response = self.client.post(
            reverse('accounts:signup'),
            data={
                'username': 'test@user',
                'email': 'test1@example.com',
                'password': 'StrongPass1!',
                'password_confirm': 'StrongPass1!',
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Username can only contain letters and numbers.')

    def test_signup_mismatched_passwords_fails(self):
        response = self.client.post(
            reverse('accounts:signup'),
            data={
                'username': 'tester1',
                'email': 'test2@example.com',
                'password': 'StrongPass1!',
                'password_confirm': 'StrongPass2!',
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Passwords do not match.')

    def test_signup_duplicate_email_fails(self):
        CustomUser.objects.create_user(username='existing', email='dupe@example.com', password='StrongPass1!')
        response = self.client.post(
            reverse('accounts:signup'),
            data={
                'username': 'tester2',
                'email': 'dupe@example.com',
                'password': 'StrongPass1!',
                'password_confirm': 'StrongPass1!',
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This email is already in use.')

    def test_signup_weak_password_fails(self):
        response = self.client.post(
            reverse('accounts:signup'),
            data={
                'username': 'tester3',
                'email': 'test3@example.com',
                'password': 'weakpass',
                'password_confirm': 'weakpass',
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Password must include at least one uppercase letter.')

    def test_valid_signup_redirects_to_login(self):
        response = self.client.post(
            reverse('accounts:signup'),
            data={
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password': 'StrongPass1!',
                'password_confirm': 'StrongPass1!',
            },
        )
        self.assertRedirects(response, reverse('accounts:login'))
        self.assertTrue(CustomUser.objects.filter(username='newuser').exists())

    def test_login_with_invalid_credentials_fails(self):
        CustomUser.objects.create_user(username='tester4', email='test4@example.com', password='StrongPass1!')
        response = self.client.post(
            reverse('accounts:login'),
            data={'username': 'tester4', 'password': 'WrongPass1!'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username or password.')

    def test_login_with_valid_credentials_redirects_to_dashboard(self):
        CustomUser.objects.create_user(username='tester5', email='test5@example.com', password='StrongPass1!')
        response = self.client.post(
            reverse('accounts:login'),
            data={'username': 'tester5', 'password': 'StrongPass1!'},
        )
        self.assertRedirects(response, reverse('dashboard:dashboard'))

    def test_logout_clears_session_and_redirects(self):
        user = CustomUser.objects.create_user(username='tester6', email='test6@example.com', password='StrongPass1!')
        self.client.force_login(user)
        response = self.client.get(reverse('accounts:logout'))
        self.assertRedirects(response, reverse('accounts:login'))
        follow_up = self.client.get(reverse('dashboard:dashboard'))
        self.assertEqual(follow_up.status_code, 302)
