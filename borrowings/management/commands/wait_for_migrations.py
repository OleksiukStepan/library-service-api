import time
from django.db import connections, OperationalError, ProgrammingError
from django.core.management.base import BaseCommand
from django.db.migrations.executor import MigrationExecutor


class Command(BaseCommand):
    """Command to wait for all database migrations to be applied."""

    help = "Waits for all database migrations to be applied"

    def handle(self, *args, **kwargs) -> None:
        """Checks for unapplied migrations and waits until all are applied"""

        self.stdout.write("Checking for unapplied migrations...")
        self.wait_for_migrations()

    def wait_for_migrations(self) -> None:
        """
       Continuously checks for unapplied migrations and waits if any are found
       """

        while True:
            try:
                executor = MigrationExecutor(connections["default"])
                if executor.migration_plan(executor.loader.graph.leaf_nodes()):
                    self.stdout.write(
                        "Unapplied migrations detected, waiting 1 second..."
                    )
                    time.sleep(1)
                else:
                    self.stdout.write(
                        self.style.SUCCESS("All migrations are applied!")
                    )
                    break
            except (OperationalError, ProgrammingError):
                self.stdout.write(
                    "Migrations table not found, waiting 1 second..."
                )
                time.sleep(1)
