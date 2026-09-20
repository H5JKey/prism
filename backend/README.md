# Backend

> FastAPI backend for distributed physically based rendering

## Overview

The backend provides the HTTP API for PriZm. It handles users, projects, scene files, render settings and render jobs.

The API is available under the `/api/v1` prefix.

## Key Features

- REST API — FastAPI-based HTTP API
- Authentication — JWT access and refresh tokens
- Projects — Create and manage rendering projects
- File Storage — Upload scene files and access rendered results through S3-compatible storage
- Render Jobs — Submit rendering tasks through Kafka
- Async Database — PostgreSQL with SQLAlchemy and asyncpg
- Tags — Organize projects with tags
- Validation — Request and response validation with Pydantic

## Tech Stack

- Python 3.13+
- FastAPI
- PostgreSQL
- SQLAlchemy 2
- Alembic
- S3 / MinIO
- Apache Kafka
- JWT + bcrypt
- Pydantic 2

## Running the Backend

### Poetry

```bash
cd backend
poetry install
source $(poetry env info --path)/bin/activate
alembic upgrade head
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Docker

```bash
docker build --file backend/Dockerfile -t prism-backend .
docker run --rm -p 8000:8000 prism-backend
```

Configure the required environment variables before starting the application.

## API Documentation

Interactive API documentation is available through Swagger UI at `/docs`.

An alternative ReDoc interface is available at `/redoc`.

The API documentation includes available endpoints, request parameters, schemas and responses.

## Typical Workflow

1. Register or log in
2. Upload a scene
3. Create a rendering project
4. Configure render settings
5. Submit and monitor the render job
6. Access the rendered result

## Database Migrations

Apply migrations:

```bash
alembic upgrade head
```

Create a new migration:

```bash
alembic revision --autogenerate -m "description"
```

Downgrade one migration:

```bash
alembic downgrade -1
```

## Testing

Run tests with:

```bash
pytest
```

## Code Quality

```bash
ruff check .
black .
mypy .
```
