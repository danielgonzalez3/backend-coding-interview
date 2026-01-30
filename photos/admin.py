"""
Admin configuration for photos app.
"""
from django.contrib import admin
from .models import Photo, PhotoFavorite


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('pexels_id', 'photographer', 'width', 'height', 'created_at')
    list_filter = ('photographer', 'created_at')
    search_fields = ('pexels_id', 'photographer', 'alt')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(PhotoFavorite)
class PhotoFavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'photo', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'photo__pexels_id')
