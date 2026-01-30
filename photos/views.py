"""
Views for the photo API.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Photo, PhotoFavorite
from .serializers import PhotoSerializer, PhotoListSerializer, UserSerializer


class RegisterView(APIView):
    """User registration endpoint."""
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        request_body=UserSerializer,
        responses={201: UserSerializer, 400: 'Bad Request'}
    )
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PhotoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing photos.
    
    list: List all photos with pagination and filtering
    retrieve: Get a single photo by ID
    search: Search photos by photographer or alt text
    favorites: List user's favorite photos
    """
    queryset = Photo.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['photographer', 'alt', 'photographer_id']
    ordering_fields = ['created_at', 'pexels_id', 'photographer']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PhotoListSerializer
        return PhotoSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by photographer if provided
        photographer = self.request.query_params.get('photographer', None)
        if photographer:
            queryset = queryset.filter(photographer__icontains=photographer)
        
        # Filter by photographer_id if provided
        photographer_id = self.request.query_params.get('photographer_id', None)
        if photographer_id:
            queryset = queryset.filter(photographer_id=photographer_id)
        
        # Filter favorites only
        favorites_only = self.request.query_params.get('favorites', None)
        if favorites_only and favorites_only.lower() == 'true':
            favorite_ids = PhotoFavorite.objects.filter(
                user=self.request.user
            ).values_list('photo_id', flat=True)
            queryset = queryset.filter(id__in=favorite_ids)
        
        return queryset
    
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('photographer', openapi.IN_QUERY, description="Filter by photographer name", type=openapi.TYPE_STRING),
            openapi.Parameter('photographer_id', openapi.IN_QUERY, description="Filter by photographer ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('favorites', openapi.IN_QUERY, description="Show only favorites", type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('search', openapi.IN_QUERY, description="Search in photographer and alt text", type=openapi.TYPE_STRING),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk=None):
        """Add or remove a photo from favorites."""
        photo = self.get_object()
        
        if request.method == 'POST':
            favorite, created = PhotoFavorite.objects.get_or_create(
                user=request.user,
                photo=photo
            )
            if created:
                return Response(
                    {'message': 'Photo added to favorites'},
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {'message': 'Photo is already in favorites'},
                status=status.HTTP_200_OK
            )
        
        elif request.method == 'DELETE':
            deleted = PhotoFavorite.objects.filter(
                user=request.user,
                photo=photo
            ).delete()
            if deleted[0]:
                return Response(
                    {'message': 'Photo removed from favorites'},
                    status=status.HTTP_200_OK
                )
            return Response(
                {'message': 'Photo was not in favorites'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def favorites(self, request):
        """List all photos favorited by the current user."""
        favorite_photos = Photo.objects.filter(
            favorited_by__user=request.user
        ).distinct()
        
        page = self.paginate_queryset(favorite_photos)
        if page is not None:
            serializer = PhotoListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = PhotoListSerializer(favorite_photos, many=True, context={'request': request})
        return Response(serializer.data)
