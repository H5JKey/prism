# Backend

> FastAPI backend for distributed physically based rendering

## Overview

The backend provides the HTTP API for Prism. It handles users, projects, scene files, render settings and render jobs.

The API is available under the `/api/v1` prefix.

---

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

| Component | Technology |
|-----------|------------|
| Language | Python 3.13+ |
| API | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy 2 |
| Migrations | Alembic |
| Object Storage | S3 / MinIO |
| Message Broker | Apache Kafka |
| Authentication | JWT + bcrypt |
| Validation | Pydantic 2 |

---

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

The API documentation includes available endpoints, request parameters, schemas and responses.

## Database Migrations

```bash
alembic upgrade head
alembic revision --autogenerate -m "description"
alembic downgrade -1
```
---

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
