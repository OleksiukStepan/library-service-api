from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase, RequestFactory
from rest_framework.test import APIClient
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model

from borrowings.models import Borrowing
from books.models import Book
from borrowings.serializers import (
    BorrowingSerializer,
    BorrowingReturnSerializer,
    BorrowingListSerializer,
    BorrowingDetailSerializer,
)

User = get_user_model()


class BorrowingSerializerTests(TestCase):

    @patch("notifications.tasks.send_telegram_message", autospec=True)
    @patch("notifications.run_telegram_bot.Bot", autospec=True)
    def setUp(self, mock_bot, mock_send_telegram_message):
        self.client = APIClient()
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            email="test@example.com", password="testpassword"
        )
        self.book = Book.objects.create(
            title="Test Book",
            author="Author",
            cover=Book.CoverType.SOFT,
            inventory=10,
            daily_fee=Decimal("1.99"),
            image=None,
        )
        self.borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            borrow_date="2023-01-01",
            expected_return_date="2023-02-01",
        )

    def test_borrowing_serializer(self):
        serializer = BorrowingSerializer(instance=self.borrowing)
        data = serializer.data
        self.assertEqual(
            set(data.keys()),
            {
                "id",
                "borrow_date",
                "expected_return_date",
                "actual_return_date",
                "book",
                "user",
            },
        )

    @patch("notifications.tasks.send_telegram_message", autospec=True)
    @patch("notifications.run_telegram_bot.Bot", autospec=True)
    def test_borrowing_serializer_validation(
        self, mock_bot, mock_send_telegram_message
    ):
        with self.assertRaises(ValidationError):
            self.book.inventory = 0
            self.book.save()
            serializer = BorrowingSerializer(
                data={"book": self.book.id, "user": self.user.id}
            )
            serializer.is_valid(raise_exception=True)

    @patch("notifications.tasks.send_telegram_message", autospec=True)
    @patch("notifications.run_telegram_bot.Bot", autospec=True)
    def test_borrowing_serializer_create(self, mock_bot, mock_send_telegram_message):
        data = {
            "book": self.book.id,
            "borrow_date": "2023-01-01",
            "expected_return_date": "2023-02-01",
        }
        request = self.factory.post("/api/borrowings/", data, format="json")
        request.user = self.user
        serializer = BorrowingSerializer(data=data, context={"request": request})
        self.assertTrue(serializer.is_valid())
        borrowing = serializer.save()
        self.assertEqual(borrowing.book.inventory, 9)

    @patch("notifications.tasks.send_telegram_message", autospec=True)
    @patch("notifications.run_telegram_bot.Bot", autospec=True)
    def test_borrowing_return_serializer(self, mock_bot, mock_send_telegram_message):
        serializer = BorrowingReturnSerializer(instance=self.borrowing)
        self.assertEqual(serializer.data, {})

    @patch("notifications.tasks.send_telegram_message", autospec=True)
    @patch("notifications.run_telegram_bot.Bot", autospec=True)
    def test_borrowing_list_serializer(self, mock_bot, mock_send_telegram_message):
        serializer = BorrowingListSerializer(instance=self.borrowing)
        data = serializer.data
        self.assertEqual(
            set(data.keys()),
            {
                "id",
                "borrow_date",
                "expected_return_date",
                "actual_return_date",
                "book",
                "user",
            },
        )

    @patch("notifications.tasks.send_telegram_message", autospec=True)
    @patch("notifications.run_telegram_bot.Bot", autospec=True)
    def test_borrowing_detail_serializer(self, mock_bot, mock_send_telegram_message):
        serializer = BorrowingDetailSerializer(instance=self.borrowing)
        data = serializer.data
        self.assertEqual(
            set(data.keys()),
            {
                "id",
                "borrow_date",
                "expected_return_date",
                "actual_return_date",
                "book",
                "user",
            },
        )
