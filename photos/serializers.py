"""
Serializers for the photo API.
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Photo, PhotoFavorite


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'first_name', 'last_name')
        extra_kwargs = {
            'email': {'required': True},
        }
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        return user


class PhotoSerializer(serializers.ModelSerializer):
    """Serializer for photo model."""
    
    is_favorited = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Photo
        fields = (
            'id', 'pexels_id', 'width', 'height', 'url',
            'photographer', 'photographer_url', 'photographer_id',
            'avg_color', 'alt', 'image', 'image_url',
            'src_original', 'src_large2x', 'src_large', 'src_medium',
            'src_small', 'src_portrait', 'src_landscape', 'src_tiny',
            'created_at', 'updated_at', 'is_favorited'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'image_url')
    
    def get_image_url(self, obj):
        """Get the full URL for the stored image."""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
    
    def get_is_favorited(self, obj) -> bool:
        """Check if the current user has favorited this photo."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return PhotoFavorite.objects.filter(
                user=request.user,
                photo=obj
            ).exists()
        return False


class PhotoListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for photo list views."""
    
    is_favorited = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Photo
        fields = (
            'id', 'pexels_id', 'width', 'height', 'url',
            'photographer', 'photographer_url', 'photographer_id',
            'avg_color', 'alt', 'image_url',
            'src_medium', 'src_small', 'src_tiny',
            'created_at', 'is_favorited'
        )
        read_only_fields = ('id', 'created_at', 'image_url')
    
    def get_image_url(self, obj):
        """Get the full URL for the stored image."""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
    
    def get_is_favorited(self, obj) -> bool:
        """Check if the current user has favorited this photo."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return PhotoFavorite.objects.filter(
                user=request.user,
                photo=obj
            ).exists()
        return False
