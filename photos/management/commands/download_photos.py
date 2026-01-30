import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from photos.models import Photo


class Command(BaseCommand):
    help = 'Download photos from Pexels and store in S3/MinIO'

    def add_arguments(self, parser):
        parser.add_argument(
            '--size',
            type=str,
            default='medium',
            choices=['original', 'large2x', 'large', 'medium', 'small', 'portrait', 'landscape', 'tiny'],
            help='Photo size to download'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit number of photos to download'
        )
        parser.add_argument(
            '--workers',
            type=int,
            default=5,
            help='Number of concurrent download workers'
        )

    def get_session(self):
        """Create a requests session with retry logic."""
        session = requests.Session()
        retry = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def download_photo(self, photo, size, session):
        """Download a single photo."""
        try:
            url = getattr(photo, f'src_{size}', None)
            
            if not url:
                return False, f'No URL for size {size}'
            
            # Stream download for large files
            response = session.get(url, timeout=30, stream=True)
            response.raise_for_status()
            
            # Read content in chunks
            content = b''
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    content += chunk
            
            # Save to S3/MinIO
            filename = f'{photo.pexels_id}_{size}.jpg'
            photo.image.save(filename, ContentFile(content), save=True)
            
            return True, None
            
        except Exception as e:
            return False, str(e)

    def handle(self, *args, **options):
        size = options['size']
        limit = options['limit']
        workers = options['workers']

        photos = Photo.objects.filter(image='')
        if limit:
            photos = photos[:limit]

        total = photos.count()
        self.stdout.write(f'Downloading {total} photos at size: {size} with {workers} workers')

        downloaded = 0
        failed = 0
        session = self.get_session()

        with ThreadPoolExecutor(max_workers=workers) as executor:
            future_to_photo = {
                executor.submit(self.download_photo, photo, size, session): photo
                for photo in photos
            }
            
            for future in as_completed(future_to_photo):
                photo = future_to_photo[future]
                try:
                    success, error = future.result()
                    if success:
                        downloaded += 1
                        if downloaded % 10 == 0:
                            self.stdout.write(f'Downloaded {downloaded}/{total}...')
                    else:
                        failed += 1
                        self.stdout.write(
                            self.style.WARNING(f'Failed photo {photo.pexels_id}: {error}')
                        )
                except Exception as e:
                    failed += 1
                    self.stdout.write(
                        self.style.ERROR(f'Error photo {photo.pexels_id}: {str(e)}')
                    )

        session.close()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nDownload complete!\n'
                f'  Downloaded: {downloaded}\n'
                f'  Failed: {failed}'
            )
        )
