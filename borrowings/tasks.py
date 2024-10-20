import datetime

from celery import shared_task
from django.utils import timezone

from borrowings.models import Borrowing
from notifications.tasks import send_telegram_message


@shared_task
def send_overdue_borrowings() -> None:
    """
    Celery task to check and send notifications for overdue borrowings.

    This task fetches borrowings from the database where the expected return date
    has passed (including today) and the actual return date is still null, indicating
    that the book has not been returned yet.

    For each overdue borrowing, a message is sent via the `send_telegram_message` function
    with details of the borrowing. If there are no overdue borrowings, a message indicating
    this is sent instead.

    The task runs as follows:
    - Retrieves today's date.
    - Filters borrowings with expected return date less than or equal to today + 1 day and actual return date is null.
    - Sends a notification for each overdue borrowing.
    - Sends a notification if no borrowings are overdue.

    Args:
        None

    Returns:
        None
    """
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
