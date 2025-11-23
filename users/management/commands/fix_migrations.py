"""
Management command to fix migration state by removing problematic recorded migrations.
This is needed when migration dependencies change and the database has old records.
"""
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Fix migration state by removing problematic recorded migrations'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Delete users.0002 migration record if it exists (it will be re-run with correct dependencies)
            cursor.execute("""
                DELETE FROM django_migrations 
                WHERE app = 'users' AND name = '0002_alter_user_options_alter_user_managers_and_more'
            """)
            
            # Delete rentals.0001 migration record if it exists (depends on fixed users.0002)
            cursor.execute("""
                DELETE FROM django_migrations 
                WHERE app = 'rentals' AND name = '0001_initial'
            """)
            
            self.stdout.write(self.style.SUCCESS('Migration records cleaned. Re-run migrations now.'))
