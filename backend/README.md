# Backend

> FastAPI backend for distributed physically based rendering

---

## Prism Backend

<table>
  <tr>
    <td><img src="../renderer/images/cornell.png" alt="Cornell box" width="400"></td>
    <td><img src="../renderer/images/room.png" alt="Room" width="400"></td>
  </tr>
</table>

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
| POST | `/v1/auth/register` | Register a new user |
| POST | `/v1/auth/login` | Log in |
| GET | `/v1/auth/refresh` | Refresh an access token |

### Files

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/v1/files/upload` | Upload a scene file |

### Projects

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/v1/projects/create` | Create a project and render |
| GET | `/v1/projects/` | Get public projects |
| GET | `/v1/projects/about-me` | Get your projects |
| GET | `/v1/projects/user/{user_id}` | Get a user's public projects |
| GET | `/v1/projects/{project_id}` | Get a project |
| PATCH | `/v1/projects/{project_id}` | Update a project |
| DELETE | `/v1/projects/{project_id}` | Delete a project |

Render settings include resolution, samples, denoiser, GPU usage, background and sun parameters.

### Tags

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/v1/tags/create` | Add a tag to a project |
| GET | `/v1/tags/project/{project_id}` | Get project tags |
| DELETE | `/v1/tags/{tag_id}` | Delete a tag |

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/v1/users/about-me` | Get your profile |
| PUT | `/v1/users/about-me` | Update your profile |
| DELETE | `/v1/users/about-me` | Delete your account |
| GET | `/v1/users/{user_id}` | Get public user information |

---

## Render Lifecycle

Creating a project also creates its render job. The renderer worker receives the task through Kafka and processes the uploaded scene.

The project contains the current render status and, when available, access to the rendered result.

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
