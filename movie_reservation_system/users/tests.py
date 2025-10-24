from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import CustomUser


class UsersTest(TestCase):
    def test_create_user_instance(self):
        instance = CustomUser.objects.create_user(username="testuser",
                                                  email="user@test.example",
                                                  password="password123",
                                                  first_name="Test",
                                                  last_name="User",
                                                  phone="+380123456789",
                                                  is_verified=False)
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertEqual(instance.username, "testuser")
        self.assertEqual(instance.email, "user@test.example")
        self.assertEqual(instance.first_name, "Test")
        self.assertEqual(instance.last_name, "User")
        self.assertEqual(instance.phone, "+380123456789")
        self.assertEqual(instance.is_verified, False)

    def test_create_user_instance_without_email(self):
        with self.assertRaises(ValueError):
            CustomUser.objects.create_user(username="testuser",
                                           email="",
                                           password="password123")

    def test_email_validation(self):
        with self.assertRaises(ValueError):
            CustomUser.objects.create_user(username="testuser",
                                           email="invalid-email",
                                           password="password123")

    def test_phone_validation(self):
        with self.assertRaises(ValidationError):
            CustomUser.objects.create_user(username="testuser",
                                           email="user@test.example",
                                           password="password123",
                                           phone="invalid-phone")