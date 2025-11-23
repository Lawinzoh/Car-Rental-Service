"""
Management command to completely reset migration state.
WARNING: This deletes all migration records and re-applies migrations from scratch.
"""
from django.core.management.base import BaseCommand
from django.db import connection
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Reset all migration records and re-apply from scratch'

    def handle(self, *args, **options):
        try:
            with connection.cursor() as cursor:
                # Clear ALL migration records
                cursor.execute("TRUNCATE TABLE django_migrations CASCADE")
                self.stdout.write(self.style.SUCCESS('Cleared all migration records'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Could not clear migrations: {str(e)}'))
            return

        # Now run migrations fresh
        self.stdout.write(self.style.SUCCESS('Running migrations from scratch...'))
        try:
            call_command('migrate', verbosity=2)
            self.stdout.write(self.style.SUCCESS('Migrations completed successfully'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Migration failed: {str(e)}'))
