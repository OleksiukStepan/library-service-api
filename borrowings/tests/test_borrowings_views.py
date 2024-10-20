from unittest.mock import patch
from datetime import date, timedelta

from django.utils import timezone
from django.test import TestCase
from rest_framework.test import APIClient, APIRequestFactory
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model

from borrowings.models import Borrowing
from books.models import Book
from borrowings.serializers import (
    BorrowingListSerializer,
    BorrowingDetailSerializer,
)


User = get_user_model()


class BorrowingViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            first_name="test_name",
            last_name="test_surname",
            email="test@example.com",
            password="1qazcde3",
        )
        self.admin = User.objects.create_superuser(
            first_name="test_admin_name",
            last_name="test_admin_surname",
            email="test_admin@example.com",
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
            borrow_date="2023-01-01",
            expected_return_date="2023-01-10",
            book=self.book,
            user=self.user,
        )
        self.list_url = reverse("borrowings:borrowings-list")
        self.detail_url = reverse(
            "borrowings:borrowings-detail", args=[self.borrowing.pk]
        )
        self.client.force_authenticate(user=self.admin)

    def test_get_borrowings_list(self):
        response = self.client.get(self.list_url)
        borrowings = Borrowing.objects.all()
        serializer = BorrowingListSerializer(borrowings, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_get_borrowing_detail(self):
        response = self.client.get(self.detail_url)
        borrowing = Borrowing.objects.get(pk=self.borrowing.pk)
        serializer = BorrowingDetailSerializer(borrowing)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    @patch("borrowings.views.send_telegram_message")
    @patch("borrowings.views.create_stripe_session")
    def test_create_borrowing(self, mock_create_stripe_session, mock_send_telegram_message):
        future_date = (timezone.now() + timedelta(days=1)).date()
        data = {
            "borrow_date": str(future_date),
            "expected_return_date": str(future_date + timedelta(days=10)),
            "book": self.book.pk,
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.list_url, data)
        if response.status_code != status.HTTP_201_CREATED:
            print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        borrowing = Borrowing.objects.get(id=response.data["id"])
        self.assertEqual(borrowing.user, self.user)
        self.assertEqual(borrowing.book, self.book)
        mock_send_telegram_message.assert_called_once()


class BorrowingViewSetReturnTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            first_name="test_name",
            last_name="test_surname",
            email="test@example.com",
            password="1qazcde3",
        )
        self.admin = User.objects.create_superuser(
            first_name="test_admin_name",
            last_name="test_admin_surname",
            email="test_admin@example.com",
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
            borrow_date="2023-01-01",
            expected_return_date="2023-01-10",
            book=self.book,
            user=self.user,
        )
        self.return_url = reverse(
            "borrowings:borrowings-return-borrowing", args=[self.borrowing.pk]
        )
        self.client.force_authenticate(user=self.user)

    @patch("borrowings.views.create_stripe_session")
    def test_return_borrowing(self, mock_create_stripe_session):
        data = {"actual_return_date": str(date.today())}
        response = self.client.post(self.return_url, data)
        self.borrowing.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.borrowing.actual_return_date, date.today())
        self.assertEqual(response.data["message"], "The book was successfully returned")

    def test_return_borrowing_already_returned(self):
        self.borrowing.actual_return_date = "2023-01-09"
        self.borrowing.save()
        response = self.client.post(self.return_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "This book has already been returned")


class BorrowingViewSetCreateTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.factory = APIRequestFactory()
        self.book = Book.objects.create(
            title="Test Book",
            author="Author",
            cover="HARD",
            inventory=10,
            daily_fee=1.00,
        )
        self.user = User.objects.create_user(
            email="test@example.com", password="1qazcde3"
        )
        self.list_url = reverse("borrowings:borrowings-list")

    @patch("borrowings.views.send_telegram_message")
    def test_create_borrowing_sends_telegram_notification(self, mock_send_telegram_message):
        future_date = (timezone.now() + timezone.timedelta(days=1)).date()
        data = {
            "borrow_date": str(future_date),
            "expected_return_date": str(future_date + timezone.timedelta(days=10)),
            "book": self.book.pk,
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.list_url, data)
        if response.status_code != status.HTTP_201_CREATED:
            print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_send_telegram_message.assert_called_once()

