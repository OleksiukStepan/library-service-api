from decimal import Decimal

import stripe
from django.conf import settings
from django.urls import reverse

from payments.models import Payment

stripe.api_key = settings.STRIPE_API_KEY

FINE_MULTIPLIER = 2


def create_stripe_session(borrowing, request):
    """
    Create a Stripe payment session for either an initial
    borrowing payment or an overdue fine.

    If the book has already been returned, and it was returned after
    the expected return date, a fine is calculated based on the overdue
    days using the `FINE_MULTIPLIER`.
    If the book has not been returned yet, this is the initial payment
    for the borrowing, and the total price is calculated based on the days
    the user has requested to borrow the book, with payment being made
    upfront for the entire borrowing period.

    Stripe Checkout:
    - Success URL: Redirects to the success page with the Stripe session ID.
    - Cancel URL: Redirects to the cancellation page.

    Creates:
    - A `Payment` object with the relevant information about the transaction.
    """
    if borrowing.actual_return_date:
        if borrowing.actual_return_date <= borrowing.expected_return_date:
            return
        latest_date = borrowing.actual_return_date
        earliest_date = borrowing.expected_return_date
        multiplier = FINE_MULTIPLIER
        payment_type = Payment.Type.FINE
    else:
        latest_date = borrowing.expected_return_date
        earliest_date = borrowing.borrow_date
        multiplier = 1
        payment_type = Payment.Type.PAYMENT

    total_days = (latest_date - earliest_date).days
    total_price = borrowing.book.daily_fee * Decimal(total_days) * multiplier

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": borrowing.book.title,
                    },
                    "unit_amount": int(total_price * 100),
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=(
            request.build_absolute_uri(reverse("payments:payment-success"))
            + "?session_id={CHECKOUT_SESSION_ID}"
        ),
        cancel_url=request.build_absolute_uri(
            reverse("payments:payment-cancel")
        ),
    )
    payment = Payment.objects.create(
        borrowing=borrowing,
        type=payment_type,
        status=Payment.Status.PENDING,
        session_url=session.url,
        session_id=session.id,
        money_to_pay=total_price,
    )
    payment.save()
