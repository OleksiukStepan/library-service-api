from datetime import date
from decimal import Decimal
from unittest.mock import patch, MagicMock

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import RequestFactory
from django.test import TestCase
from django.urls import reverse

from books.models import Book
from borrowings.models import Borrowing
from payments.models import Payment
from payments.stripe_helpers import create_stripe_session, renew_stripe_session

TEST_SESSION_ID = "test_session_id"
TEST_SESSION_URL = "https://test.url"
BORROWING_LIST_URL = reverse("borrowings:borrowings-list")
BORROW_DATE = date(year=2024, month=10, day=10)
EXPECTED_DATE = date(year=2024, month=10, day=17)
OVERDUE_DATE = date(year=2024, month=10, day=24)

request = RequestFactory().get(BORROWING_LIST_URL)
PAYMENT_SUCCESS_URL = (
    request.build_absolute_uri(reverse("payments:payment-success"))
    + "?session_id={CHECKOUT_SESSION_ID}"
)
PAYMENT_CANCEL_ULR = request.build_absolute_uri(
    reverse("payments:payment-cancel")
)


class TestCreateStripeSession(TestCase):
    @classmethod
    def setUpClass(cls):
        call_command("loaddata", "data.json")

    @classmethod
    def tearDownClass(cls):
        ...

    def tearDown(self):
        self.patcher.stop()

    def setUp(self):
        self.user = get_user_model().objects.get(pk=2)
        self.client.force_login(self.user)
        self.patcher = patch("stripe.checkout.Session.create")
        self.mock_stripe_create_session = self.patcher.start()
        self.mock_stripe_create_session.return_value = MagicMock(
            id=TEST_SESSION_ID, url=TEST_SESSION_URL
        )

    def test_create_stripe_session_and_primary_payment(self):
        borrowing = Borrowing.objects.create(
            user=self.user,
            book=Book.objects.first(),
            borrow_date=BORROW_DATE,
            expected_return_date=EXPECTED_DATE,
        )
        self.assertFalse(Payment.objects.filter(borrowing=borrowing).exists())

        create_stripe_session(borrowing, request)

        unit_amount = int(Decimal(7) * borrowing.book.daily_fee * 100)
        self.mock_stripe_create_session.assert_called_once_with(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {"name": borrowing.book.title},
                        "unit_amount": unit_amount,
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            locale="en",
            success_url=PAYMENT_SUCCESS_URL,
            cancel_url=PAYMENT_CANCEL_ULR,
        )

        payment = Payment.objects.get(borrowing=borrowing)

        self.assertEqual(payment.type, Payment.Type.PAYMENT)
        self.assertEqual(payment.status, Payment.Status.PENDING)
        self.assertEqual(payment.session_id, TEST_SESSION_ID)
        self.assertEqual(payment.session_url, TEST_SESSION_URL)
        self.assertEqual(payment.money_to_pay, unit_amount / 100)

    def test_create_stripe_session_and_fine_payment(self):
        borrowing = Borrowing.objects.create(
            user=self.user,
            book=Book.objects.first(),
            borrow_date=BORROW_DATE,
            expected_return_date=EXPECTED_DATE,
            actual_return_date=OVERDUE_DATE,
        )
        self.assertFalse(Payment.objects.filter(borrowing=borrowing).exists())

        create_stripe_session(borrowing, request)

        fine_unit_amount = int(Decimal(7) * borrowing.book.daily_fee * 100 * 2)
        self.mock_stripe_create_session.assert_called_once_with(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {"name": borrowing.book.title},
                        "unit_amount": fine_unit_amount,
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            locale="en",
            success_url=PAYMENT_SUCCESS_URL,
            cancel_url=PAYMENT_CANCEL_ULR,
        )

        payment = Payment.objects.get(borrowing=borrowing)

        self.assertEqual(payment.type, Payment.Type.FINE)
        self.assertEqual(payment.status, Payment.Status.PENDING)
        self.assertEqual(payment.session_id, TEST_SESSION_ID)
        self.assertEqual(payment.session_url, TEST_SESSION_URL)
        self.assertEqual(payment.money_to_pay, fine_unit_amount / 100)

    def test_no_create_stripe_session(self):
        borrowing = Borrowing.objects.first()
        payment_before = Payment.objects.filter(borrowing=borrowing)

        self.assertTrue(payment_before.exists())

        create_stripe_session(borrowing, request)
        payment_after = Payment.objects.filter(borrowing=borrowing)

        self.mock_stripe_create_session.assert_not_called()
        self.assertEqual(list(payment_before), list(payment_after))


class TestRenewStripeSession(TestCase):
    @classmethod
    def setUpClass(cls):
        call_command("loaddata", "data.json")

    @classmethod
    def tearDownClass(cls):
        ...

    def tearDown(self):
        self.patcher.stop()

    def setUp(self):
        self.patcher = patch("stripe.checkout.Session.create")
        self.mock_stripe_create_session = self.patcher.start()
        self.mock_stripe_create_session.return_value = MagicMock(
            id=TEST_SESSION_ID, url=TEST_SESSION_URL
        )

    def test_renew_stripe_session(self):
        payment = Payment.objects.filter(pk=3).select_related(
            "borrowing__book").first()
        payment.status = "EXPIRED"
        payment.save()

        renew_stripe_session(payment, request)

        self.mock_stripe_create_session.assert_called_once_with(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {"name": payment.borrowing.book.title},
                        "unit_amount": int(payment.money_to_pay * 100),
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            locale="en",
            success_url=PAYMENT_SUCCESS_URL,
            cancel_url=PAYMENT_CANCEL_ULR,
        )

        self.assertEqual(payment.status, Payment.Status.PENDING)
        self.assertEqual(payment.session_id, TEST_SESSION_ID)
        self.assertEqual(payment.session_url, TEST_SESSION_URL)
