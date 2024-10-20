from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, IntervalSchedule


class Command(BaseCommand):
    help = "Create interval schedule for checking expired Stripe sessions."

    def handle(self, *args, **kwargs) -> None:
        schedule, _ = IntervalSchedule.objects.get_or_create(
            every=1, period=IntervalSchedule.MINUTES
        )

        task, created = PeriodicTask.objects.get_or_create(
            interval=schedule,
            name="Check Stripe sessions each minute",
            task="payments.tasks.check_expired_sessions",
        )

        if created:
            self.stdout.write(self.style.SUCCESS("Successfully created interval task"))
        else:
            self.stdout.write(self.style.SUCCESS("Interval task already exists"))
