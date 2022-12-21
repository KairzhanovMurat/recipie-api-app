from django.core.management import BaseCommand
from django.db.utils import OperationalError
from psycopg2 import OperationalError as Psycopg2Error
import time


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write('waiting for db connection...')
        db_ready = False
        while db_ready is False:
            try:
                self.check(databases=['default'])
                db_ready = True
            except (Psycopg2Error, OperationalError):
                self.stdout.write('unable to connect, waiting 1 more sec...')
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS('successfully connected to db'))
