"""
URL configuration for photo_api project.
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Photo Management API",
      default_version='v1',
      description="A RESTful API for managing photos from Pexels",
      contact=openapi.Contact(email="api@example.com"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('photos.urls.auth')),
    path('api/photos/', include('photos.urls.photos')),
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/openapi/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]
