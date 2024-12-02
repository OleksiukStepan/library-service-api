from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError


class UserModelTests(TestCase):
    """Test suite for the custom User model"""

    def test_create_user(self):
        """Test regular user creation"""

        User = get_user_model()
        user = User.objects.create_user(
            email="testuser@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )
        self.assertEqual(user.email, "testuser@example.com")
        self.assertTrue(user.check_password("testpass123"))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        """Test admin user creation"""

        User = get_user_model()
        superuser = User.objects.create_superuser(
            email="superuser@example.com",
            password="superpass123",
            first_name="Super",
            last_name="User",
        )
        self.assertEqual(superuser.email, "superuser@example.com")
        self.assertTrue(superuser.check_password("superpass123"))
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

    def test_create_user_without_email(self):
        """Test user creation without email"""

        User = get_user_model()
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email=None,
                password="testpass123",
                first_name="Test",
                last_name="User",
            )

    def test_create_user_without_first_name(self):
        """Test user creation without first name"""

        User = get_user_model()
        user = User(
            email="testuser@example.com",
            password="testpass123",
            first_name="",
            last_name="User",
        )
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_create_user_without_last_name(self):
        """Test user creation without last name"""

        User = get_user_model()
        user = User(
            email="testuser@example.com",
            password="testpass123",
            first_name="Test",
            last_name="",
        )
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_email_unique_constraint(self):
        """Test unique email constraint"""

        User = get_user_model()
        User.objects.create_user(
            email="unique@example.com",
            password="testpass123",
            first_name="Unique",
            last_name="User",
        )
        with self.assertRaises(ValidationError):
            user = User(
                email="unique@example.com",
                password="testpass123",
                first_name="Unique2",
                last_name="User2",
            )
            user.full_clean()
