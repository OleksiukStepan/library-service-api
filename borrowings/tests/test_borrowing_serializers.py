from decimal import Decimal
from unittest.mock import patch, MagicMock

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model

from borrowings.models import Borrowing
from books.models import Book


User = get_user_model()


class BorrowingViewSetTest(TestCase):
    """
    Test case for the Borrowing ViewSet.

    This test case includes tests for
    listing, retrieving, creating, and returning borrowings,
    ensuring that permissions and operations work correctly
    for both regular users and administrators.
    """

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create_user(
            first_name="first_name",
            last_name="last_name",
            email="test@example.com",
            password="testpassword",
        )
        self.admin = User.objects.create_superuser(
            first_name="first_admin_name",
            last_name="last_admin_name",
            email="admin@example.com",
            password="adminpassword",
        )
        self.book = Book.objects.create(
            title="Test Book",
            author="Author",
            cover=Book.CoverType.SOFT,
            inventory=10,
            daily_fee=Decimal("1.99"),
        )
        self.borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            borrow_date=timezone.now().date(),
            expected_return_date=(
                timezone.now().date() + timezone.timedelta(days=10)
            ),
        )
        self.url_list = reverse("borrowings:borrowings-list")
        self.url_detail = reverse(
            "borrowings:borrowings-detail", args=[self.borrowing.id]
        )
        self.url_return = reverse(
            "borrowings:borrowings-return-borrowing",
            args=[self.borrowing.id]
        )

    def test_get_borrowing_list(self) -> None:
        """
        Test retrieving the borrowing list.

        This test checks that an authenticated user can
        retrieve a list of borrowings.
        """

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], self.borrowing.id)

    def test_get_borrowing_detail(self) -> None:
        """
        Test retrieving borrowing details.

        This test checks that an authenticated user can
        retrieve the details of a specific borrowing.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.borrowing.id)

    @patch("borrowings.views.send_telegram_message")
    @patch("borrowings.views.create_stripe_session")
    def test_create_borrowing(
            self,
            mock_create_stripe_session: MagicMock,
            mock_send_telegram_message: MagicMock
    ) -> None:
        """
        Test creating a new borrowing.

        This test checks that an authenticated user can create a new borrowing,
        and verifies that the book inventory is updated and
        notifications are sent.
        """
        self.client.force_authenticate(user=self.user)
        data = {
            "book": self.book.id,
            "borrow_date": str(
                timezone.now().date() + timezone.timedelta(days=1)
            ),
            "expected_return_date": str(
                timezone.now().date() + timezone.timedelta(days=10)
            ),
        }
        response = self.client.post(self.url_list, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 9)
        borrowing = Borrowing.objects.get(id=response.data["id"])
        self.assertEqual(borrowing.user, self.user)
        self.assertEqual(borrowing.book, self.book)
        mock_send_telegram_message.assert_called_once()

    def test_return_borrowing_success(self) -> None:
        """
        Test successfully returning a borrowing.

        This test checks that an admin can mark a borrowing as returned,
        and verifies that the book inventory is updated.
        """

        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.url_return)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.borrowing.refresh_from_db()
        self.assertIsNotNone(self.borrowing.actual_return_date)
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 11)

    def test_return_borrowing_already_returned(self) -> None:
        """
        Test returning a borrowing that has already been returned.

        This test checks that a validation error is raised if an admin
        attempts to mark a borrowing as returned when
        it has already been returned.
        """
        self.client.force_authenticate(user=self.admin)
        self.borrowing.actual_return_date = timezone.now().date()
        self.borrowing.save()
        response = self.client.post(self.url_return)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertEqual(
            response.data["error"],
            "This book has already been returned"
        )

    def test_admin_can_see_all_borrowings(self) -> None:
        """
        Test that an admin can see all borrowings.

        This test checks that an admin can retrieve a list of all borrowings.
        """
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
