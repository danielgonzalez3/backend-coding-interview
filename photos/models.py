"""
Photo models for the photo management API.
"""
from django.db import models
from django.contrib.auth.models import User


class Photo(models.Model):
    """
    Model representing a photo from Pexels.
    """
    pexels_id = models.IntegerField(unique=True, db_index=True, help_text="Pexels photo ID")
    width = models.IntegerField(help_text="Photo width in pixels")
    height = models.IntegerField(help_text="Photo height in pixels")
    url = models.URLField(max_length=500, help_text="Pexels photo page URL")
    
    # Photographer information
    photographer = models.CharField(max_length=255, db_index=True)
    photographer_url = models.URLField(max_length=500)
    photographer_id = models.IntegerField(db_index=True)
    
    # Photo metadata
    avg_color = models.CharField(max_length=7, help_text="Average color hex code")
    alt = models.TextField(blank=True, help_text="Photo alt text/description")
    
    # Stored image file
    image = models.ImageField(upload_to='photos/', null=True, blank=True)
    
    # Original Pexels URLs for reference
    src_original = models.URLField(max_length=500)
    src_large2x = models.URLField(max_length=500)
    src_large = models.URLField(max_length=500)
    src_medium = models.URLField(max_length=500)
    src_small = models.URLField(max_length=500)
    src_portrait = models.URLField(max_length=500)
    src_landscape = models.URLField(max_length=500)
    src_tiny = models.URLField(max_length=500)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['pexels_id']),
            models.Index(fields=['photographer']),
            models.Index(fields=['photographer_id']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Photo {self.pexels_id} by {self.photographer}"


class PhotoFavorite(models.Model):
    """
    Model for user favorites/bookmarks.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'photo']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} favorited photo {self.photo.pexels_id}"
