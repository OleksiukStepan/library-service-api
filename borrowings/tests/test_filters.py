from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model

from borrowings.models import Borrowing
from books.models import Book


User = get_user_model()


class BorrowingFilterTest(TestCase):
    """
    Test case for filtering borrowings in the Borrowing ViewSet.

    This test case includes tests for filtering borrowings by active status
    and by user ID, ensuring that the filters work correctly
    for authenticated users.
    """

    def setUp(self) -> None:
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            first_name="test_name",
            last_name="test_surname",
            email="test@example.com",
            password="1qazcde3",
        )
        self.user2 = User.objects.create_user(
            first_name="test_name2",
            last_name="test_surname2",
            email="test2@example.com",
            password="1qazcde3",
        )
        self.admin = User.objects.create_superuser(
            first_name="test_admin_name",
            last_name="test_admin_surname",
            email="test_admin@example.com",
            password="1qazcde3",
        )

        self.book1 = Book.objects.create(
            title="Test Book 1",
            author="Author 1",
            cover="HARD",
            inventory=10,
            daily_fee=1.00,
        )
        self.book2 = Book.objects.create(
            title="Test Book 2",
            author="Author 2",
            cover="SOFT",
            inventory=5,
            daily_fee=1.50,
        )

        self.borrowing1 = Borrowing.objects.create(
            borrow_date="2023-01-01",
            expected_return_date="2023-01-10",
            book=self.book1,
            user=self.user1,
        )
        self.borrowing2 = Borrowing.objects.create(
            borrow_date="2023-01-05",
            expected_return_date="2023-01-15",
            book=self.book2,
            user=self.user2,
        )
        self.borrowing3 = Borrowing.objects.create(
            borrow_date="2023-01-10",
            expected_return_date="2023-01-20",
            actual_return_date="2023-01-18",
            book=self.book1,
            user=self.user1,
        )

        self.url = reverse("borrowings:borrowings-list")
        self.client.login(email="test_admin@example.com", password="1qazcde3")

    def test_filter_by_is_active(self) -> None:
        """
        Test filtering borrowings by active status.

        This test checks that an admin user can filter borrowings
        that are currently active (i.e., have not been returned yet).
        """
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url, {"is_active": "true"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        borrowings = Borrowing.objects.filter(actual_return_date__isnull=True)
        self.assertEqual(len(response.data["results"]), borrowings.count())

    def test_filter_by_user_id(self) -> None:
        """
        Test filtering borrowings by user ID.

        This test checks that an admin user can filter borrowings
        based on the user who borrowed the book.
        """
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url, {"user_id": self.user1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        borrowings = Borrowing.objects.filter(user=self.user1)
        self.assertEqual(len(response.data["results"]), borrowings.count())

    def test_filter_by_is_active_and_user_id(self) -> None:
        """
        Test filtering borrowings by active status and user ID.

        This test checks that an admin user can filter borrowings
        that are currently active and belong to a specific user.
        """

        self.client.force_authenticate(user=self.admin)
        response = self.client.get(
            self.url, {"is_active": "true", "user_id": self.user1.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        borrowings = Borrowing.objects.filter(
            actual_return_date__isnull=True, user=self.user1
        )
        self.assertEqual(len(response.data["results"]), borrowings.count())
