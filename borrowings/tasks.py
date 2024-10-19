import datetime

from celery import shared_task
from django.utils import timezone

from borrowings.models import Borrowing
from notifications.tasks import send_telegram_message


@shared_task
def send_overdue_borrowings() -> None:
    today = timezone.now().date()
    overdue_borrowings = Borrowing.objects.filter(
        expected_return_date__lte=today + datetime.timedelta(days=1),
        actual_return_date__isnull=True,
    )
    if overdue_borrowings.exists():
        for borrowing in overdue_borrowings:
            message = (
                f"Overdue Borrowing (ID: {borrowing.id}):\n"
                f"User: {borrowing.user}\n"
                f"Book: {borrowing.book.title}\n"
                f"Borrow Date: {borrowing.borrow_date}\n"
                f"Expected Return Date: {borrowing.expected_return_date}\n"
            )
            send_telegram_message(message)
    else:
        send_telegram_message("No borrowings overdue today!")
