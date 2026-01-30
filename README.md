# Photo Management API

Django REST API for managing photos with PostgreSQL and MinIO storage.

## Tech Stack
- Django REST Framework + PostgreSQL + MinIO (S3-compatible storage)
- JWT authentication with djangorestframework-simplejwt
- Swagger/OpenAPI documentation with drf-yasg

## Quick Start

```bash
# Start services
docker-compose up -d

# Setup (migrations, initialize MinIO, ingest photos)
python manage.py migrate
python manage.py init_minio
python manage.py ingest_photos photos.csv

# Download photos to MinIO (optional)
python manage.py download_photos --size medium --workers 5

# Run server
python manage.py runserver
```

**Access:**
- API Docs: http://localhost:8000/api/docs/
- MinIO: http://localhost:9001 (minioadmin/minioadmin)

## API Endpoints

**Auth:** `/api/auth/register/`, `/api/auth/token/`, `/api/auth/token/refresh/`
**Photos:** `/api/photos/` (list, search, filter), `/api/photos/{id}/` (detail), `/api/photos/{id}/favorite/` (add/remove), `/api/photos/favorites/` (list favorites)
**Docs:** `/api/docs/` (Swagger), `/api/redoc/` (ReDoc)

## Features

- JWT authentication with token refresh
- Photo CRUD with pagination (20/page)
- Search & filter (photographer, photographer_id, favorites)
- Favorites system (add/remove/list)
- S3/MinIO storage for photos
- CSV ingestion with error handling
- Concurrent photo downloads with retry logic
- Comprehensive test suite

## Architecture

- **PostgreSQL** - Indexed on pexels_id, photographer, photographer_id, created_at
- **MinIO/S3** - Object storage for scalable photo storage
- **JWT** - Stateless authentication
- **REST** - Resource-based URL design, proper HTTP status codes
- **Separation** - Photos app with models, views, serializers, tests

## Testing

```bash
pytest                          # Run all tests
pytest --cov=photos            # With coverage
```

## Future Improvements

- Rate limiting & Redis caching
- Full-text search (PostgreSQL/Elasticsearch)
- Photo collections/albums
- Bulk operations
- CI/CD pipeline

## Assumptions

- Single-tenant application
- Read-heavy workload (optimized for browsing)
- MinIO for local dev, S3 for production
- Stateless JWT (no token blacklisting)
