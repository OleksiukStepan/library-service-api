from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError

from books.models import Book
from borrowings.models import Borrowing


User = get_user_model()

class BorrowingModelTest(TestCase):
    def setUp(self):
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

    def test_return_book_success(self):
        self.borrowing.return_book()
        self.assertIsNotNone(self.borrowing.actual_return_date)
        self.assertEqual(self.book.inventory, 11)

    def test_return_book_already_returned(self):
        self.borrowing.actual_return_date = timezone.now().date()
        self.borrowing.save()
        with self.assertRaises(ValidationError):
            self.borrowing.return_book()

