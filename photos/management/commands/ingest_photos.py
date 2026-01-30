"""
Management command to ingest photos from CSV file.
"""
import csv
import os
from django.core.management.base import BaseCommand
from django.db import transaction
from photos.models import Photo


class Command(BaseCommand):
    help = 'Ingest photos from CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Path to the CSV file containing photo data'
        )
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing photos if they already exist',
        )

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        update_existing = options['update']

        if not os.path.exists(csv_file_path):
            self.stdout.write(
                self.style.ERROR(f'CSV file not found: {csv_file_path}')
            )
            return

        self.stdout.write(f'Reading photos from {csv_file_path}...')

        photos_created = 0
        photos_updated = 0
        photos_skipped = 0
        errors = []

        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                with transaction.atomic():
                    for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                        try:
                            pexels_id = int(row['id'])
                            
                            photo_data = {
                                'pexels_id': pexels_id,
                                'width': int(row['width']),
                                'height': int(row['height']),
                                'url': row['url'],
                                'photographer': row['photographer'],
                                'photographer_url': row['photographer_url'],
                                'photographer_id': int(row['photographer_id']),
                                'avg_color': row['avg_color'],
                                'alt': row.get('alt', ''),
                                'src_original': row['src.original'],
                                'src_large2x': row['src.large2x'],
                                'src_large': row['src.large'],
                                'src_medium': row['src.medium'],
                                'src_small': row['src.small'],
                                'src_portrait': row['src.portrait'],
                                'src_landscape': row['src.landscape'],
                                'src_tiny': row['src.tiny'],
                            }
                            
                            photo, created = Photo.objects.update_or_create(
                                pexels_id=pexels_id,
                                defaults=photo_data
                            )
                            
                            if created:
                                photos_created += 1
                            elif update_existing:
                                photos_updated += 1
                            else:
                                photos_skipped += 1
                                
                        except (ValueError, KeyError) as e:
                            errors.append(f'Row {row_num}: {str(e)}')
                            self.stdout.write(
                                self.style.WARNING(f'Error processing row {row_num}: {str(e)}')
                            )

            self.stdout.write(self.style.SUCCESS(
                f'\nIngestion complete!\n'
                f'  Created: {photos_created}\n'
                f'  Updated: {photos_updated}\n'
                f'  Skipped: {photos_skipped}\n'
                f'  Errors: {len(errors)}'
            ))

            if errors:
                self.stdout.write(self.style.ERROR('\nErrors encountered:'))
                for error in errors[:10]:  # Show first 10 errors
                    self.stdout.write(self.style.ERROR(f'  {error}'))
                if len(errors) > 10:
                    self.stdout.write(
                        self.style.ERROR(f'  ... and {len(errors) - 10} more errors')
                    )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to process CSV file: {str(e)}')
            )
            raise
