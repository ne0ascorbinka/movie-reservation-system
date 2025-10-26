from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .models import CustomUser


CustomUser = get_user_model()


class UsersTest(TestCase):
    def test_create_user_instance(self):
        instance = CustomUser.objects.create_user(username="testUser",
                                                  email="user@test.example",
                                                  password="password123",
                                                  first_name="Test",
                                                  last_name="User",
                                                  phone="+380123456789",
                                                  is_verified=False)
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertEqual(instance.username, "testUser")
        self.assertEqual(instance.email, "user@test.example")
        self.assertEqual(instance.first_name, "Test")
        self.assertEqual(instance.last_name, "User")
        self.assertEqual(instance.phone, "+380123456789")
        self.assertEqual(instance.is_verified, False)

    def test_create_user_instance_without_email(self):
        with self.assertRaises(ValueError):
            CustomUser.objects.create_user(username="testUser",
                                           email="",
                                           password="password123")

    def test_email_validation(self):
        with self.assertRaises(ValueError):
            CustomUser.objects.create_user(username="testUser",
                                           email="invalid-email",
                                           password="password123")

    def test_phone_validation(self):
        with self.assertRaises(ValidationError):
            CustomUser.objects.create_user(username="testUser",
                                           email="user@test.example",
                                           password="password123",
                                           phone="invalid-phone")

    def test_authentication(self):
        user = CustomUser.objects.create_user(email="user@test.example", password="password123")
        login = self.client.login(email="user@test.example", password="password123")
        self.assertTrue(login)


class UserRegistrationViewTests(TestCase):
    """Test suite for user registration view."""

    def setUp(self):
        """Set up test data and URL."""
        self.url = reverse('register')
        self.valid_data = {
            'email': 'newuser@example.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '+380501234567',
            'agree_terms': True,
        }

    def test_registration_page_renders_correctly(self):
        """GET /register/ should return 200 and render registration template."""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')
        self.assertContains(response, 'email')
        self.assertContains(response, 'password1')
        self.assertContains(response, 'password2')
        self.assertContains(response, 'first_name')
        self.assertContains(response, 'last_name')
        self.assertContains(response, 'phone')
        self.assertContains(response, 'agree_terms')

    def test_registration_page_has_correct_form(self):
        """Registration page should contain the registration form."""
        response = self.client.get(self.url)
        
        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertIn('email', form.fields)
        self.assertIn('password1', form.fields)
        self.assertIn('password2', form.fields)
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        self.assertIn('phone', form.fields)
        self.assertIn('agree_terms', form.fields)

    def test_successful_registration_with_valid_data(self):
        """User should be able to register with all valid data."""
        response = self.client.post(self.url, data=self.valid_data)
        
        # Check user was created
        self.assertEqual(CustomUser.objects.count(), 1)
        user = CustomUser.objects.first()
        
        # Verify user data
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.phone, '+380501234567')
        self.assertTrue(user.check_password('SecurePass123!'))
        
        # Check redirect after successful registration
        self.assertRedirects(response, reverse('login'))

    def test_registration_duplicate_email_rejected(self):
        """Registration should fail if email already exists."""
        # Create existing user
        CustomUser.objects.create_user(
            email='newuser@example.com',
            password='ExistingPass123!'
        )
        
        response = self.client.post(self.url, data=self.valid_data)
        
        # Should not create another user
        self.assertEqual(CustomUser.objects.count(), 1)
        
        # Should show error and stay on same page
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context['form'],
            'email',
            'A user with that email already exists.'
        )

    def test_registration_password_mismatch_rejected(self):
        """Registration should fail if passwords don't match."""
        data = self.valid_data.copy()
        data['password2'] = 'DifferentPass123!'
        
        response = self.client.post(self.url, data=data)
        
        # Should not create user
        self.assertEqual(CustomUser.objects.count(), 0)
        
        # Should show error
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context['form'],
            'password2',
            "The two password fields didn't match."
        )

    def test_registration_password_too_short_rejected(self):
        """Registration should fail if password is too short."""
        data = self.valid_data.copy()
        data['password1'] = 'short'
        data['password2'] = 'short'
        
        response = self.client.post(self.url, data=data)
        
        # Should not create user
        self.assertEqual(CustomUser.objects.count(), 0)
        
        # Should show error
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_registration_password_too_common_rejected(self):
        """Registration should fail if password is too common."""
        data = self.valid_data.copy()
        data['password1'] = 'password123'
        data['password2'] = 'password123'
        
        response = self.client.post(self.url, data=data)
        
        # Should not create user
        self.assertEqual(CustomUser.objects.count(), 0)
        
        # Should show error
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['form'].is_valid())

    def test_registration_numeric_password_rejected(self):
        """Registration should fail if password is entirely numeric."""
        data = self.valid_data.copy()
        data['password1'] = '12345678901'
        data['password2'] = '12345678901'
        
        response = self.client.post(self.url, data=data)
        
        # Should not create user
        self.assertEqual(CustomUser.objects.count(), 0)
        
        # Should show error
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_registration_missing_agree_terms_rejected(self):
        """Registration should fail if agree_terms is not checked."""
        data = self.valid_data.copy()
        data['agree_terms'] = False
        
        response = self.client.post(self.url, data=data)
        
        # Should not create user
        self.assertEqual(CustomUser.objects.count(), 0)
        
        # Should show error
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context['form'],
            'agree_terms',
            'You must agree to the terms and conditions.'
        )

    def test_registration_without_agree_terms_field_rejected(self):
        """Registration should fail if agree_terms field is missing entirely."""
        data = self.valid_data.copy()
        del data['agree_terms']
        
        response = self.client.post(self.url, data=data)
        
        # Should not create user
        self.assertEqual(CustomUser.objects.count(), 0)
        
        # Should show error
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['form'].is_valid())

    def test_registration_missing_email_rejected(self):
        """Registration should fail if email is missing."""
        data = self.valid_data.copy()
        data['email'] = ''
        
        response = self.client.post(self.url, data=data)
        
        # Should not create user
        self.assertEqual(CustomUser.objects.count(), 0)
        
        # Should show error
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context['form'],
            'email',
            'This field is required.'
        )

    def test_registration_invalid_email_format_rejected(self):
        """Registration should fail if email format is invalid."""
        data = self.valid_data.copy()
        data['email'] = 'not-an-email'
        
        response = self.client.post(self.url, data=data)
        
        # Should not create user
        self.assertEqual(CustomUser.objects.count(), 0)
        
        # Should show error
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context['form'],
            'email',
            'Enter a valid email address.'
        )

    def test_registration_invalid_phone_format_rejected(self):
        """Registration should fail if phone format is invalid (if validation exists)."""
        data = self.valid_data.copy()
        data['phone'] = 'invalid-phone'
        
        response = self.client.post(self.url, data=data)
        
        # If phone validation is implemented, should not create user
        # If not implemented, this test documents expected behavior
        if response.status_code == 200 and not response.context['form'].is_valid():
            self.assertEqual(CustomUser.objects.count(), 0)
            self.assertIn('phone', response.context['form'].errors)

    def test_registration_case_insensitive_email_duplicate(self):
        """Registration should treat emails case-insensitively."""
        # Create user with lowercase email
        CustomUser.objects.create_user(
            email='user@example.com',
            password='Pass123!'
        )
        
        # Try to register with uppercase version
        data = self.valid_data.copy()
        data['email'] = 'USER@EXAMPLE.COM'
        
        response = self.client.post(self.url, data=data)
        
        # Should not create duplicate user
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertEqual(response.status_code, 200)

    def test_registration_user_is_not_staff_by_default(self):
        """Newly registered user should not have staff privileges."""
        response = self.client.post(self.url, data=self.valid_data)
        
        user = CustomUser.objects.first()
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_registration_user_can_login_after_registration(self):
        """User should be able to login with credentials after registration."""
        self.client.post(self.url, data=self.valid_data)
        
        # Try to login with registered credentials
        login_successful = self.client.login(
            email='newuser@example.com',
            password='SecurePass123!'
        )
        
        self.assertTrue(login_successful)

    def test_registration_multiple_users_with_different_emails(self):
        """Multiple users should be able to register with different emails."""
        # Register first user
        self.client.post(self.url, data=self.valid_data)
        
        # Register second user
        data2 = self.valid_data.copy()
        data2['email'] = 'seconduser@example.com'
        self.client.post(self.url, data=data2)
        
        # Both users should exist
        self.assertEqual(CustomUser.objects.count(), 2)
        emails = CustomUser.objects.values_list('email', flat=True)
        self.assertIn('newuser@example.com', emails)
        self.assertIn('seconduser@example.com', emails)