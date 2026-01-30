"""
Tests for photo models.
"""
import pytest
from django.contrib.auth.models import User
from photos.models import Photo, PhotoFavorite


@pytest.mark.django_db
class TestPhotoModel:
    """Test Photo model."""
    
    def test_create_photo(self):
        """Test creating a photo."""
        photo = Photo.objects.create(
            pexels_id=12345,
            width=1920,
            height=1080,
            url='https://example.com/photo',
            photographer='Test Photographer',
            photographer_url='https://example.com/photographer',
            photographer_id=1,
            avg_color='#FFFFFF',
            alt='Test photo',
            src_original='https://example.com/original.jpg',
            src_large2x='https://example.com/large2x.jpg',
            src_large='https://example.com/large.jpg',
            src_medium='https://example.com/medium.jpg',
            src_small='https://example.com/small.jpg',
            src_portrait='https://example.com/portrait.jpg',
            src_landscape='https://example.com/landscape.jpg',
            src_tiny='https://example.com/tiny.jpg',
        )
        
        assert photo.pexels_id == 12345
        assert photo.photographer == 'Test Photographer'
        assert str(photo) == 'Photo 12345 by Test Photographer'
    
    def test_photo_unique_pexels_id(self):
        """Test that pexels_id must be unique."""
        Photo.objects.create(
            pexels_id=12345,
            width=1920,
            height=1080,
            url='https://example.com/photo1',
            photographer='Test Photographer',
            photographer_url='https://example.com/photographer',
            photographer_id=1,
            avg_color='#FFFFFF',
            src_original='https://example.com/original.jpg',
            src_large2x='https://example.com/large2x.jpg',
            src_large='https://example.com/large.jpg',
            src_medium='https://example.com/medium.jpg',
            src_small='https://example.com/small.jpg',
            src_portrait='https://example.com/portrait.jpg',
            src_landscape='https://example.com/landscape.jpg',
            src_tiny='https://example.com/tiny.jpg',
        )
        
        with pytest.raises(Exception):  # Should raise IntegrityError
            Photo.objects.create(
                pexels_id=12345,  # Duplicate
                width=1920,
                height=1080,
                url='https://example.com/photo2',
                photographer='Test Photographer',
                photographer_url='https://example.com/photographer',
                photographer_id=1,
                avg_color='#FFFFFF',
                src_original='https://example.com/original.jpg',
                src_large2x='https://example.com/large2x.jpg',
                src_large='https://example.com/large.jpg',
                src_medium='https://example.com/medium.jpg',
                src_small='https://example.com/small.jpg',
                src_portrait='https://example.com/portrait.jpg',
                src_landscape='https://example.com/landscape.jpg',
                src_tiny='https://example.com/tiny.jpg',
            )


@pytest.mark.django_db
class TestPhotoFavoriteModel:
    """Test PhotoFavorite model."""
    
    def test_create_favorite(self):
        """Test creating a favorite."""
        user = User.objects.create_user(username='testuser', password='testpass')
        photo = Photo.objects.create(
            pexels_id=12345,
            width=1920,
            height=1080,
            url='https://example.com/photo',
            photographer='Test Photographer',
            photographer_url='https://example.com/photographer',
            photographer_id=1,
            avg_color='#FFFFFF',
            src_original='https://example.com/original.jpg',
            src_large2x='https://example.com/large2x.jpg',
            src_large='https://example.com/large.jpg',
            src_medium='https://example.com/medium.jpg',
            src_small='https://example.com/small.jpg',
            src_portrait='https://example.com/portrait.jpg',
            src_landscape='https://example.com/landscape.jpg',
            src_tiny='https://example.com/tiny.jpg',
        )
        
        favorite = PhotoFavorite.objects.create(user=user, photo=photo)
        
        assert favorite.user == user
        assert favorite.photo == photo
        assert str(favorite) == 'testuser favorited photo 12345'
    
    def test_favorite_unique_per_user(self):
        """Test that a user can only favorite a photo once."""
        user = User.objects.create_user(username='testuser', password='testpass')
        photo = Photo.objects.create(
            pexels_id=12345,
            width=1920,
            height=1080,
            url='https://example.com/photo',
            photographer='Test Photographer',
            photographer_url='https://example.com/photographer',
            photographer_id=1,
            avg_color='#FFFFFF',
            src_original='https://example.com/original.jpg',
            src_large2x='https://example.com/large2x.jpg',
            src_large='https://example.com/large.jpg',
            src_medium='https://example.com/medium.jpg',
            src_small='https://example.com/small.jpg',
            src_portrait='https://example.com/portrait.jpg',
            src_landscape='https://example.com/landscape.jpg',
            src_tiny='https://example.com/tiny.jpg',
        )
        
        PhotoFavorite.objects.create(user=user, photo=photo)
        
        with pytest.raises(Exception):  # Should raise IntegrityError
            PhotoFavorite.objects.create(user=user, photo=photo)
