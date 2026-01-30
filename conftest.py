"""
Pytest configuration and fixtures.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'photo_api.settings')
django.setup()
