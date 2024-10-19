from django.core.management.base import BaseCommand
from django_celery_beat.models import CrontabSchedule, PeriodicTask


class Command(BaseCommand):
    help = "Create crontab schedule for daily borrowing count task"

    def handle(self, *args, **kwargs) -> None:
        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute="0",
            hour="0",
            day_of_week="*",
            day_of_month="*",
            month_of_year="*",
        )

        task, created = PeriodicTask.objects.get_or_create(
            crontab=schedule,
            name="Daily send borrowings overdue",
            task="borrowings.tasks.send_overdue_borrowings",
            description=(
                "The task filters all borrowings, which are overdue "
                "(expected_return_date is tomorrow or less, and the book is "
                "still not returned) and send a notification to the telegram "
                "chat about each overdue with detailed information."
            ),
        )

        if created:
            self.stdout.write(self.style.SUCCESS("Successfully created periodic task"))
        else:
            self.stdout.write(self.style.SUCCESS("Periodic task already exists"))
