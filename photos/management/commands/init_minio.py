import boto3
from botocore.exceptions import ClientError
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Initialize MinIO bucket for photo storage'

    def handle(self, *args, **options):
        try:
            # Create S3 client
            s3_client = boto3.client(
                's3',
                endpoint_url=settings.AWS_S3_ENDPOINT_URL,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME
            )
            
            bucket_name = settings.AWS_STORAGE_BUCKET_NAME
            
            # Check if bucket exists
            try:
                s3_client.head_bucket(Bucket=bucket_name)
                self.stdout.write(
                    self.style.SUCCESS(f'Bucket "{bucket_name}" already exists')
                )
            except ClientError:
                # Create bucket
                s3_client.create_bucket(Bucket=bucket_name)
                self.stdout.write(
                    self.style.SUCCESS(f'Created bucket "{bucket_name}"')
                )
            
            # Set bucket policy to allow public read
            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": "*"},
                        "Action": ["s3:GetObject"],
                        "Resource": [f"arn:aws:s3:::{bucket_name}/*"]
                    }
                ]
            }
            
            import json
            s3_client.put_bucket_policy(
                Bucket=bucket_name,
                Policy=json.dumps(policy)
            )
            
            self.stdout.write(
                self.style.SUCCESS('MinIO initialization complete!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to initialize MinIO: {str(e)}')
            )
            raise
