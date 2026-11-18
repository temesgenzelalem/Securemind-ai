import time
from django.core.management.base import BaseCommand
from django.db import connection
from django.db.utils import OperationalError

class Command(BaseCommand):
    """Django command to pause execution until database is available"""
    help = 'Pauses execution until the default database is available'

    def handle(self, *args, **options):
        self.stdout.write('Waiting for database connection...')
        db_up = False
        attempts = 0
        max_attempts = 30
        while not db_up and attempts < max_attempts:
            try:
                connection.ensure_connection()
                db_up = True
            except OperationalError:
                attempts += 1
                self.stdout.write(f'Database unavailable, waiting 1 second... (attempt {attempts}/{max_attempts})')
                time.sleep(1)

        if db_up:
            self.stdout.write(self.style.SUCCESS('Database is ready!'))
        else:
            self.stdout.write(self.style.ERROR('Database connection failed after maximum attempts.'))
            raise OperationalError('Database connection timed out')
