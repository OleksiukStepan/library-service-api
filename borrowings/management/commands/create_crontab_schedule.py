# from django.core.management.base import BaseCommand
# from django_celery_beat.models import CrontabSchedule, PeriodicTask
#
#
# class Command(BaseCommand):
#     help = "Create crontab schedule for daily borrowing count task"
#
#     def handle(self, *args, **kwargs) -> None:
#         schedule, _ = CrontabSchedule.objects.get_or_create(
#             minute="0",
#             hour="0",
#             day_of_week="*",
#             day_of_month="*",
#             month_of_year="*",
#         )
#
#         task, created = PeriodicTask.objects.get_or_create(
#             crontab=schedule,
#             name="Daily send borrowings overdue",
#             task="borrowings.tasks.send_overdue_borrowings",
#             description=(
#                 "The task filters all borrowings, which are overdue "
#                 "(expected_return_date is tomorrow or less, and the book is "
#                 "still not returned) and send a notification to the telegram "
#                 "chat about each overdue with detailed information."
#             ),
#         )
#
#         if created:
#             self.stdout.write(self.style.SUCCESS("Successfully created periodic task"))
#         else:
#             self.stdout.write(self.style.SUCCESS("Periodic task already exists"))


from django_celery_beat.models import IntervalSchedule, PeriodicTask
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create interval schedule for sending overdue borrowing notifications every 30 seconds"

    def handle(self, *args, **kwargs) -> None:
        # Create or get an interval schedule for 30 seconds
        schedule, _ = IntervalSchedule.objects.get_or_create(
            every=30,
            period=IntervalSchedule.SECONDS,  # Set the interval period to seconds
        )

        # Create or get the periodic task
        task, created = PeriodicTask.objects.get_or_create(
            interval=schedule,  # Use the interval schedule instead of crontab
            name="Send borrowings overdue every 30 seconds",
            task="borrowings.tasks.send_overdue_borrowings",  # Replace with your task
            description=(
                "This task sends notifications for overdue borrowings "
                "every 30 seconds to the telegram chat with detailed information."
            ),
        )

        if created:
            self.stdout.write(self.style.SUCCESS("Successfully created periodic task"))
        else:
            self.stdout.write(self.style.SUCCESS("Periodic task already exists"))
