# Backend

> FastAPI backend for distributed physically based rendering

---

## Overview

The backend provides the HTTP API used to work with Prism. It handles user accounts, projects, scene files, render settings and render jobs.

The API is available under the `/v1` prefix. Once the server is running, the easiest way to explore it is through the automatically generated Swagger UI at `/docs`.

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
- **Monitoring** – Prometheus metrics for the API

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.13+ |
| API | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy 2 |
| Database Driver | asyncpg |
| Migrations | Alembic |
| Object Storage | S3 / MinIO |
| Message Broker | Apache Kafka |
| Authentication | JWT + bcrypt |
| Validation | Pydantic 2 |
| Metrics | Prometheus |

---

## Running the Backend

The backend requires Python 3.13+ and the project's infrastructure services: PostgreSQL, Kafka and an S3-compatible object store such as MinIO.

### Using Poetry

From the repository root:

```bash
cd backend
poetry install
```

Configure the required environment variables in `.env`, then apply the database migrations:

```bash
alembic upgrade head
```

Start the API:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`.

### Using Docker

Build the image from the repository root:

```bash
docker build --file backend/Dockerfile -t prism-backend .
```

Then run it with the required environment and infrastructure services:

```bash
docker run --rm -p 8000:8000 prism-backend
```

For a complete local setup, use the repository's Docker Compose configuration.

---

## Configuration

Configuration is provided through environment variables and can be stored in a `.env` file.

The exact settings are defined in `core/config`. The main groups of configuration are:

| Group | Purpose |
|-------|---------|
| Database | PostgreSQL connection |
| Kafka | Broker and render-task topics |
| MinIO / S3 | Object storage connection |
| JWT | Token signing and authentication |
| Application | General backend settings |

Do not commit secrets such as database passwords, S3 credentials or JWT signing keys.

---

## Using the API

The base URL for a local instance is:

```
http://localhost:8000/v1
```

Open `http://localhost:8000/docs` in a browser to see the complete OpenAPI documentation and try requests interactively.

Most operations require an access token. After logging in, send it as:

```
Authorization: Bearer <access_token>
```

A typical workflow is:

1. Register or log in.
2. Upload a scene file.
3. Create a project with render settings and the uploaded file.
4. Use the project endpoints to inspect the render status and result.
5. Add or manage tags if needed.

---

## Authentication

### Register

`POST /v1/auth/register`

Creates a new account and returns access and refresh tokens.

Request:

```json
{
  "surname": "Doe",
  "name": "John",
  "username": "john",
  "email": "john@example.com",
  "password": "password"
}
```

### Login

`POST /v1/auth/login`

Authenticates an existing user.

Request:

```json
{
  "username": "john",
  "password": "password"
}
```

The response contains the tokens required for authenticated requests.

### Refresh access token

`GET /v1/auth/refresh`

Uses the refresh token to obtain a new access token.

---

## Files

### Upload a file

`POST /v1/files/upload`

Uploads a file to the configured S3-compatible storage and returns its file information.

The request uses `multipart/form-data` with the file field.

Example:

```bash
curl -X POST http://localhost:8000/v1/files/upload \
  -H "Authorization: Bearer <access_token>" \
  -F "uploaded_file=@scene.glb"
```

The returned file ID is used when creating a project.

---

## Projects

Projects contain the source scene, render configuration and render status.

### Create a project

`POST /v1/projects/create`

Creates a project and its render configuration.

Example request:

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

The response contains the created project and render information.

### Get public projects

`GET /v1/projects/?page=1&size=10`

Returns a paginated list of public projects.

### Get your projects

`GET /v1/projects/about-me?page=1&size=10`

Returns projects owned by the authenticated user.

### Get a user's public projects

`GET /v1/projects/user/{user_id}?page=1&size=10`

Returns the public projects belonging to a specific user.

### Get a project

`GET /v1/projects/{project_id}`

Returns project information, render information and access URLs for stored files.

### Update a project

`PATCH /v1/projects/{project_id}`

Partially updates the project's name, description or visibility.

Example:

```json
{
  "name": "Updated Scene",
  "visibility": "private"
}
```

### Delete a project

`DELETE /v1/projects/{project_id}`

Deletes a project owned by the authenticated user.

---

## Tags

Tags can be attached to projects to make them easier to organize.

### Create a tag

`POST /v1/tags/create`

Example:

```json
{
  "name": "architecture",
  "project_id": 1
}
```

### Get project tags

`GET /v1/tags/project/{project_id}`

Returns the tags associated with a project.

### Delete a tag

`DELETE /v1/tags/{tag_id}`

Deletes a tag owned by the authenticated user.

---

## Users

### Get your profile

`GET /v1/users/about-me`

Returns the authenticated user's profile, including their email.

### Update your profile

`PUT /v1/users/about-me`

Updates the authenticated user's name, surname, username and email.

### Delete your account

`DELETE /v1/users/about-me`

Deletes the authenticated user's account.

### Get a user

`GET /v1/users/{user_id}`

Returns public information about a user.

---

## Render Lifecycle

Creating a project also creates its render job. The renderer worker receives the render task through Kafka and processes the uploaded scene.

The project response contains a render status. Once rendering is complete, the result file can be accessed through the URL returned by the project endpoint.

The backend is responsible for storing the metadata and files; the actual rendering is performed by the renderer worker.

---

## Database Migrations

Apply existing migrations:

```bash
alembic upgrade head
```

Create a new migration:

```bash
alembic revision --autogenerate -m "description"
```

Rollback the latest migration:

```bash
alembic downgrade -1
```

---

## Testing

Run the test suite with:

```bash
pytest
```

For verbose output:

```bash
pytest -v
```

---

## Code Quality

The project uses Ruff, Black and mypy.

```bash
ruff check .
black .
mypy .
```

---

## API Documentation

When the backend is running, FastAPI provides:

- `/docs` – Swagger UI
- `/redoc` – ReDoc
- `/openapi.json` – OpenAPI schema

The Swagger UI is the recommended starting point for exploring and testing the API.
