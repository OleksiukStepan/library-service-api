from celery import shared_task
import stripe
from django.conf import settings

from payments.models import Payment


stripe.api_key = settings.STRIPE_API_KEY


@shared_task
def check_expired_sessions() -> None:
    pending_payments = Payment.objects.filter(status=Payment.Status.PENDING)

    for payment in pending_payments:
        try:
            session = stripe.checkout.Session.retrieve(payment.session_id)
            if session.status != "open":
                payment.status = Payment.Status.EXPIRED
                payment.save()

        except stripe.error.InvalidRequestError:
            payment.status = Payment.Status.EXPIRED
            payment.save()
