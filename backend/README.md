# Backend

> FastAPI backend for distributed physically based rendering

---

## Overview

The backend provides the HTTP API for Prism. It handles users, projects, scene files, render settings and render jobs.

The API is available under the `/api/v1` prefix.

Interactive API documentation is available throught Swagger UI at  `/docs`.

---

## Key Features

- **REST API** – FastAPI-based HTTP API
- **Authentication** – JWT access and refresh tokens
- **Projects** – Create and manage rendering projects
- **File Storage** – Upload scene files and access rendered results through S3-compatible storage
- **Render Jobs** – Submit rendering tasks through Kafka
- **Async Database** – PostgreSQL with SQLAlchemy and asyncpg
- **Tags** – Organize projects with tags
- **Validation** – Request and response validation with Pydantic

---

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

The backend requires Python 3.13+ and PostgreSQL, Kafka and an S3-compatible object store.

### Poetry

```bash
cd backend
poetry install
source $(poetry env info --path)/bin/activate
```

Configure the required environment variables, then apply migrations:

```bash
alembic upgrade head
```

Start the application:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Docker

```bash
docker build --file backend/Dockerfile -t prism-backend .
docker run --rm -p 8000:8000 prism-backend
```

For a complete setup, use the repository's Docker Compose configuration.

---

## Configuration

Configuration is provided through environment variables and can be stored in a `.env` file.

The main configuration groups are:

| Group | Purpose |
|-------|---------|
| Database | PostgreSQL connection |
| Kafka | Broker and render-task topics |
| MinIO / S3 | Object storage |
| JWT | Authentication |
| Application | General backend settings |

---

## API

Most operations require an access token:

```
Authorization: Bearer <access_token>
```

A typical workflow is:

1. Register or log in.
2. Upload a scene file.
3. Create a project with render settings.
4. Monitor the project render status.
5. Access the rendered result when it is ready.

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register a new user |
| POST | `/api/v1/auth/login` | Log in |
| GET | `/api/v1/auth/refresh` | Refresh an access token |

### Files

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/files/upload` | Upload a scene file |

The uploaded file ID is used when creating a project.

### Projects

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/projects/create` | Create a project and render |
| GET | `/api/v1/projects/` | Get public projects |
| GET | `/api/v1/projects/about-me` | Get your projects |
| GET | `/api/v1/projects/user/{user_id}` | Get a user's public projects |
| GET | `/api/v1/projects/{project_id}` | Get a project |
| PATCH | `/api/v1/projects/{project_id}` | Update a project |
| DELETE | `/api/v1/projects/{project_id}` | Delete a project |

A render is configured when the project is created. The render settings include resolution, samples, denoiser, GPU usage, background and sun parameters.

Example:

```json
{
  "project": {
    "name": "My Scene",
    "description": "Test render",
    "source_file_id": 1,
    "visibility": "public"
  },
  "render": {
    "width": 1920,
    "height": 1080,
    "samples": 128,
    "denoiser": true,
    "gpu": true,
    "background": [0.1, 0.1, 0.1],
    "sun": {
      "direction": [0.0, 1.0, 0.0],
      "color": [1.0, 0.8, 0.5],
      "exponent": 10
    }
  }
}
```

### Tags

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/tags/create` | Add a tag to a project |
| GET | `/api/v1/tags/project/{project_id}` | Get project tags |
| DELETE | `/api/v1/tags/{tag_id}` | Delete a tag |

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/users/about-me` | Get your profile |
| PUT | `/api/v1/users/about-me` | Update your profile |
| DELETE | `/api/v1/users/about-me` | Delete your account |
| GET | `/api/v1/users/{user_id}` | Get public user information |

---

## Database Migrations

```bash
alembic upgrade head
alembic revision --autogenerate -m "description"
alembic downgrade -1
```

---

## Testing

```bash
pytest
```

## Code Quality

```bash
ruff check .
black .
mypy .
```
