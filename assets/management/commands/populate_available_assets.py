# assets/management/commands/populate_available_assets.py

import csv
import os
from django.core.management.base import BaseCommand, CommandError
from assets.models import AvailableAsset

class Command(BaseCommand):
    help = 'Populates the AvailableAsset model with B3 tickers from a CSV file.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='The path to the CSV file containing B3 tickers.',
        )

    def handle(self, *args, **options):
        file_path = options['file']

        if not file_path:
            raise CommandError('Please provide the path to the CSV file using --file.')

        if not os.path.exists(file_path):
            raise CommandError(f'The file {file_path} does not exist.')

        with open(file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            count = 0
            for row in reader:
                ticker = row.get('ticker')
                name = row.get('name')

                if not ticker or not name:
                    self.stdout.write(self.style.WARNING(f'Skipping incomplete row: {row}'))
                    continue

                obj, created = AvailableAsset.objects.get_or_create(
                    ticker=ticker,
                    defaults={'name': name}
                )
                if created:
                    count += 1
                    self.stdout.write(self.style.SUCCESS(f'Added AvailableAsset: {ticker} - {name}'))
                else:
                    self.stdout.write(self.style.NOTICE(f'AvailableAsset already exists: {ticker}'))

            self.stdout.write(self.style.SUCCESS(f'Successfully added {count} new AvailableAssets.'))
