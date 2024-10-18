from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from books.models import Book
from users.models import User
from borrowings.models import Borrowing


class BorrowingModelTest(TestCase):
    @patch("notifications.tasks.send_telegram_message", autospec=True)
    @patch("notifications.run_telegram_bot.Bot", autospec=True)
    def setUp(self, mock_send_telegram_message, mock_bot):
        self.user = User.objects.create_user(
            first_name="test_name",
            last_name="test_surname",
            email="test@example.com",
            password="1qazcde3",
        )
        self.book = Book.objects.create(
            title="Test Book",
            author="Author",
            cover="HARD",
            inventory=10,
            daily_fee=1.00,
        )
        self.borrowing = Borrowing.objects.create(
            borrow_date=timezone.now().date(),
            expected_return_date=timezone.now().date() + timezone.timedelta(days=10),
            book=self.book,
            user=self.user,
        )

    @patch("notifications.tasks.send_telegram_message")
    def test_return_book_success(self, mock_send_telegram_message):
        self.borrowing.return_book()
        self.assertIsNotNone(self.borrowing.actual_return_date)
        self.assertEqual(self.book.inventory, 11)

    @patch("notifications.tasks.send_telegram_message")
    def test_return_book_already_returned(self, mock_send_telegram_message):
        self.borrowing.actual_return_date = timezone.now().date()
        self.borrowing.save()
        with self.assertRaises(ValidationError):
            self.borrowing.return_book()

