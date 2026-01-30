"""
Tests for photo API views.
"""
import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from photos.models import Photo, PhotoFavorite


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def photo():
    return Photo.objects.create(
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


@pytest.mark.django_db
class TestAuthentication:
    """Test authentication endpoints."""
    
    def test_register_user(self, api_client):
        """Test user registration."""
        response = api_client.post('/api/auth/register/', {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'testpass123',
            'first_name': 'New',
            'last_name': 'User',
        })
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert response.data['user']['username'] == 'newuser'
    
    def test_register_duplicate_username(self, api_client, user):
        """Test registering with duplicate username."""
        response = api_client.post('/api/auth/register/', {
            'username': 'testuser',
            'email': 'different@example.com',
            'password': 'testpass123',
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_login(self, api_client, user):
        """Test user login."""
        response = api_client.post('/api/auth/token/', {
            'username': 'testuser',
            'password': 'testpass123',
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
    
    def test_login_invalid_credentials(self, api_client):
        """Test login with invalid credentials."""
        response = api_client.post('/api/auth/token/', {
            'username': 'nonexistent',
            'password': 'wrongpass',
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestPhotoEndpoints:
    """Test photo API endpoints."""
    
    def test_list_photos_requires_auth(self, api_client):
        """Test that listing photos requires authentication."""
        response = api_client.get('/api/photos/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_list_photos(self, authenticated_client, photo):
        """Test listing photos."""
        response = authenticated_client.get('/api/photos/')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data or len(response.data) > 0
    
    def test_retrieve_photo(self, authenticated_client, photo):
        """Test retrieving a single photo."""
        response = authenticated_client.get(f'/api/photos/{photo.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['pexels_id'] == 12345
        assert response.data['photographer'] == 'Test Photographer'
    
    def test_filter_by_photographer(self, authenticated_client, photo):
        """Test filtering photos by photographer."""
        response = authenticated_client.get('/api/photos/?photographer=Test')
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_search_photos(self, authenticated_client, photo):
        """Test searching photos."""
        response = authenticated_client.get('/api/photos/?search=Test')
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_favorite_photo(self, authenticated_client, photo, user):
        """Test favoriting a photo."""
        response = authenticated_client.post(f'/api/photos/{photo.id}/favorite/')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert PhotoFavorite.objects.filter(user=user, photo=photo).exists()
    
    def test_unfavorite_photo(self, authenticated_client, photo, user):
        """Test unfavoriting a photo."""
        PhotoFavorite.objects.create(user=user, photo=photo)
        
        response = authenticated_client.delete(f'/api/photos/{photo.id}/favorite/')
        
        assert response.status_code == status.HTTP_200_OK
        assert not PhotoFavorite.objects.filter(user=user, photo=photo).exists()
    
    def test_list_favorites(self, authenticated_client, photo, user):
        """Test listing user's favorite photos."""
        PhotoFavorite.objects.create(user=user, photo=photo)
        
        response = authenticated_client.get('/api/photos/favorites/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) > 0
    
    def test_favorite_already_favorited(self, authenticated_client, photo, user):
        """Test favoriting an already favorited photo."""
        PhotoFavorite.objects.create(user=user, photo=photo)
        
        response = authenticated_client.post(f'/api/photos/{photo.id}/favorite/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'Photo is already in favorites'
