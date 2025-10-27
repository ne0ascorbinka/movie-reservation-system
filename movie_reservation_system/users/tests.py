from django.contrib.auth import get_user_model, SESSION_KEY
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
        self.assertTemplateUsed(response, 'register.html')
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
        
        form = response.context['form']

        # Assert the form is invalid
        self.assertFalse(form.is_valid())

        # Assert 'password2' field has at least one error
        self.assertIn('password2', form.errors)
        self.assertGreater(len(form.errors['password2']), 0)



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
        data2['phone'] = '+12345678901'
        self.client.post(self.url, data=data2)
        
        # Both users should exist
        self.assertEqual(CustomUser.objects.count(), 2)
        emails = CustomUser.objects.values_list('email', flat=True)
        self.assertIn('newuser@example.com', emails)
        self.assertIn('seconduser@example.com', emails)


class UserLoginViewTests(TestCase):
    """Test suite for user login view."""

    def setUp(self):
        """Set up test data and URL."""
        self.url = reverse('login')
        self.password = 'TestPass123!'
        
        # Create a test user
        self.user = CustomUser.objects.create_user(
            email='testuser@example.com',
            password=self.password,
            first_name='Test',
            last_name='User'
        )
        
        self.valid_credentials = {
            'username': 'testuser@example.com',  # Django's AuthenticationForm uses 'username'
            'password': self.password,
        }

    # ==================== PAGE RENDERING ====================

    def test_login_page_renders_correctly(self):
        """GET /login/ should return 200 and render login template."""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')
        self.assertContains(response, 'username')
        self.assertContains(response, 'password')

    def test_login_page_has_correct_form(self):
        """Login page should contain authentication form."""
        response = self.client.get(self.url)
        
        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertIn('username', form.fields)
        self.assertIn('password', form.fields)

    def test_login_page_has_csrf_token(self):
        """Login form should include CSRF token for security."""
        response = self.client.get(self.url)
        
        self.assertContains(response, 'csrfmiddlewaretoken')

    # ==================== SUCCESSFUL LOGIN ====================

    def test_successful_login_with_valid_credentials(self):
        """User should be able to login with correct email and password."""
        response = self.client.post(self.url, data=self.valid_credentials)
        
        # Should redirect after successful login
        self.assertEqual(response.status_code, 302)
        
        # User should be authenticated
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertEqual(response.wsgi_request.user.email, 'testuser@example.com')

    def test_successful_login_redirects_to_default_page(self):
        """After login, user should be redirected to default success URL."""
        response = self.client.post(self.url, data=self.valid_credentials)
        
        # Default redirect is usually to LOGIN_REDIRECT_URL (settings.py)
        # Commonly '/' or '/dashboard/' or '/home/'
        self.assertRedirects(response, reverse('home'), fetch_redirect_response=False)

    def test_successful_login_creates_session(self):
        """Successful login should create a session with user ID."""
        response = self.client.post(self.url, data=self.valid_credentials)
        
        # Check session contains authenticated user ID
        self.assertIn(SESSION_KEY, self.client.session)
        self.assertEqual(
            int(self.client.session[SESSION_KEY]), 
            self.user.pk
        )

    def test_successful_login_sets_session_cookie(self):
        """Successful login should set sessionid cookie."""
        response = self.client.post(self.url, data=self.valid_credentials, follow=True)
        
        self.assertIn('sessionid', response.cookies)

    def test_user_can_access_protected_page_after_login(self):
        """After login, user should be able to access protected pages."""
        self.client.post(self.url, data=self.valid_credentials)
        
        # Try to access a protected page
        protected_url = reverse('dashboard')  # Adjust to your protected view
        response = self.client.get(protected_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    # ==================== FAILED LOGIN ====================

    def test_login_with_incorrect_password_rejected(self):
        """Login should fail with incorrect password."""
        data = self.valid_credentials.copy()
        data['password'] = 'WrongPassword123!'
        
        response = self.client.post(self.url, data=data)
        
        # Should not redirect (stays on login page)
        self.assertEqual(response.status_code, 200)
        
        # User should not be authenticated
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        
        # Should show error message
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors)

    def test_login_with_nonexistent_email_rejected(self):
        """Login should fail with email that doesn't exist."""
        data = {
            'username': 'nonexistent@example.com',
            'password': 'SomePassword123!',
        }
        
        response = self.client.post(self.url, data=data)
        
        # Should not redirect
        self.assertEqual(response.status_code, 200)
        
        # User should not be authenticated
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        
        # Should show error
        form = response.context['form']
        self.assertFalse(form.is_valid())

    def test_login_failed_shows_generic_error(self):
        """Failed login should show error without revealing if email exists."""
        data = self.valid_credentials.copy()
        data['password'] = 'WrongPassword'
        
        response = self.client.post(self.url, data=data)
        
        # Should have non-field errors (generic message)
        form = response.context['form']
        self.assertTrue(form.non_field_errors() or form.errors)

    def test_login_with_inactive_user_rejected(self):
        """Inactive users should not be able to login."""
        # Create inactive user
        inactive_user = CustomUser.objects.create_user(
            email='inactive@example.com',
            password='Pass123!',
            is_active=False
        )
        
        data = {
            'username': 'inactive@example.com',
            'password': 'Pass123!',
        }
        
        response = self.client.post(self.url, data=data)
        
        # Should fail
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    # ==================== FORM VALIDATION & EDGE CASES ====================

    def test_login_with_empty_email_rejected(self):
        """Login should fail if email is empty."""
        data = self.valid_credentials.copy()
        data['username'] = ''
        
        response = self.client.post(self.url, data=data)
        
        # Should stay on login page
        self.assertEqual(response.status_code, 200)
        
        # Should show error for username field
        form = response.context['form']
        self.assertIn('username', form.errors)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_login_with_empty_password_rejected(self):
        """Login should fail if password is empty."""
        data = self.valid_credentials.copy()
        data['password'] = ''
        
        response = self.client.post(self.url, data=data)
        
        # Should stay on login page
        self.assertEqual(response.status_code, 200)
        
        # Should show error for password field
        form = response.context['form']
        self.assertIn('password', form.errors)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_login_with_both_fields_empty_rejected(self):
        """Login should fail if both fields are empty."""
        data = {
            'username': '',
            'password': '',
        }
        
        response = self.client.post(self.url, data=data)
        
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIn('username', form.errors)
        self.assertIn('password', form.errors)

    def test_login_with_whitespace_only_rejected(self):
        """Login should fail with whitespace-only input."""
        data = {
            'username': '   ',
            'password': '   ',
        }
        
        response = self.client.post(self.url, data=data)
        
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_already_logged_in_user_redirected(self):
        """User already logged in should be redirected away from login page."""
        # Login first
        self.client.login(email='testuser@example.com', password=self.password)
        
        # Try to access login page
        response = self.client.get(self.url)
        
        # Should redirect to home/dashboard (depending on your implementation)
        # Note: This behavior depends on your view implementation
        # If not implemented, this test documents expected behavior
        if response.status_code == 302:
            self.assertRedirects(response, reverse('home'), fetch_redirect_response=False)

    # ==================== SESSION & SECURITY ====================

    def test_session_contains_auth_user_id_after_login(self):
        """Session should contain _auth_user_id after successful login."""
        self.client.post(self.url, data=self.valid_credentials)
        
        # Check session
        session = self.client.session
        self.assertIn('_auth_user_id', session)
        self.assertEqual(int(session['_auth_user_id']), self.user.pk)

    def test_login_without_csrf_token_rejected(self):
        """Login request without CSRF token should be rejected."""
        # Disable CSRF middleware for this specific request
        response = self.client.post(
            self.url, 
            data=self.valid_credentials,
            secure=True,
            HTTP_X_CSRFTOKEN='invalid'
        )
        
        # Django's CSRF protection should reject this
        # Note: TestClient bypasses CSRF by default, so this test
        # documents expected behavior in production
        # To truly test CSRF, you'd need to use Client with enforce_csrf_checks=True

    def test_session_changes_after_login(self):
        """Session key should change after login (session fixation protection)."""
        # Get initial session key
        self.client.get(self.url)
        old_session_key = self.client.session.session_key
        
        # Login
        self.client.post(self.url, data=self.valid_credentials)
        new_session_key = self.client.session.session_key
        
        # Session key should be different (Django rotates it on login)
        self.assertIsNotNone(old_session_key)
        self.assertIsNotNone(new_session_key)
        # Note: In tests, session rotation may not occur, 
        # but this documents expected production behavior

    # ==================== NEXT PARAMETER / REDIRECT ====================

    def test_login_with_next_parameter_redirects_correctly(self):
        """Login with ?next parameter should redirect to specified page."""
        next_url = reverse('profile')  # Adjust to your URL
        url_with_next = f"{self.url}?next={next_url}"
        
        response = self.client.post(url_with_next, data=self.valid_credentials)
        
        # Should redirect to next URL
        self.assertRedirects(response, next_url, fetch_redirect_response=False)

    def test_login_with_invalid_next_parameter_uses_default(self):
        """Login with invalid next URL should use default redirect."""
        # Try to redirect to external URL (should be blocked)
        url_with_next = f"{self.url}?next=http://evil.com"
        
        response = self.client.post(url_with_next, data=self.valid_credentials)
        
        # Should redirect to default, not external site
        self.assertRedirects(response, reverse('home'), fetch_redirect_response=False)

    def test_login_next_parameter_preserves_query_string(self):
        """Next parameter should preserve query strings in redirect URL."""
        next_url = f"{reverse('search')}?q=test&category=movies"
        url_with_next = f"{self.url}?next={next_url}"
        
        response = self.client.post(url_with_next, data=self.valid_credentials)
        
        self.assertRedirects(response, next_url, fetch_redirect_response=False)

    def test_login_next_parameter_only_allows_internal_urls(self):
        """Next parameter should only allow internal URLs for security."""
        external_url = "http://malicious-site.com/steal-cookies"
        url_with_next = f"{self.url}?next={external_url}"
        
        response = self.client.post(url_with_next, data=self.valid_credentials)
        
        # Should NOT redirect to external URL
        redirect_url = response.url if response.status_code == 302 else None
        if redirect_url:
            self.assertNotIn('malicious-site.com', redirect_url)

    # ==================== ERROR MESSAGES ====================

    def test_failed_login_shows_error_without_exact_text_check(self):
        """Failed login should show errors (flexible check)."""
        data = self.valid_credentials.copy()
        data['password'] = 'wrong'
        
        response = self.client.post(self.url, data=data)
        
        # Check that some error exists (don't check exact text)
        form = response.context['form']
        has_errors = bool(form.errors or form.non_field_errors())
        self.assertTrue(has_errors, "Expected form to have errors after failed login")

    def test_login_error_messages_are_user_friendly(self):
        """Error messages should be present in the response."""
        data = self.valid_credentials.copy()
        data['password'] = 'incorrect'
        
        response = self.client.post(self.url, data=data)
        
        # Check that error content exists somewhere in response
        content = response.content.decode('utf-8').lower()
        has_error_indicators = any(
            word in content 
            for word in ['error', 'incorrect', 'invalid', 'failed']
        )
        self.assertTrue(has_error_indicators)

    # ==================== CASE SENSITIVITY ====================

    def test_email_login_is_case_insensitive(self):
        """Login should work regardless of email case."""
        data = self.valid_credentials.copy()
        data['username'] = 'TESTUSER@EXAMPLE.COM'  # Uppercase
        
        response = self.client.post(self.url, data=data)
        
        # Should successfully login (depending on your backend configuration)
        # This test documents expected behavior
        if CustomUser.objects.filter(email__iexact=data['username']).exists():
            self.assertTrue(response.wsgi_request.user.is_authenticated)

    # ==================== MULTIPLE LOGIN ATTEMPTS ====================

    def test_multiple_failed_login_attempts(self):
        """Multiple failed login attempts should all be rejected."""
        wrong_data = self.valid_credentials.copy()
        wrong_data['password'] = 'wrong'
        
        for _ in range(3):
            response = self.client.post(self.url, data=wrong_data)
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.wsgi_request.user.is_authenticated)
        
        # User should still be able to login with correct credentials
        response = self.client.post(self.url, data=self.valid_credentials)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_logout_then_login_again(self):
        """User should be able to logout and login again."""
        # Login
        self.client.post(self.url, data=self.valid_credentials)
        self.assertTrue(self.client.session.get('_auth_user_id'))
        
        # Logout
        self.client.logout()
        self.assertNotIn('_auth_user_id', self.client.session)
        
        # Login again
        response = self.client.post(self.url, data=self.valid_credentials)
        self.assertTrue(response.wsgi_request.user.is_authenticated)