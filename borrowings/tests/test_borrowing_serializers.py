from django.test import TestCase
from rest_framework.exceptions import ValidationError

from books.models import Book
from users.models import User
from borrowings.serializers import BorrowingSerializer


class BorrowingSerializerTest(TestCase):
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
        self.borrowing_data = {
            "borrow_date": "2023-01-01",
            "expected_return_date": "2023-01-10",
            "book": self.book.id,
            "user": self.user.id,
        }

    def test_borrowing_serializer_valid(self):
        serializer = BorrowingSerializer(data=self.borrowing_data)
        self.assertTrue(serializer.is_valid())

    def test_borrowing_serializer_invalid_inventory(self):
        self.book.inventory = 0
        self.book.save()
        serializer = BorrowingSerializer(data=self.borrowing_data)
        self.assertTrue(serializer.is_valid())
        with self.assertRaises(ValidationError) as context:
            serializer.save()
        self.assertEqual(str(context.exception.detail[0]), "This book is currently out of stock")
