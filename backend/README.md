# Backend

> FastAPI backend for distributed physically based rendering

---

## Prism Backend

~~~text
                         ┌─────────────────┐
                         │     Client      │
                         └────────┬────────┘
                                  │ HTTP
                                  ▼
                         ┌─────────────────┐
                         │    FastAPI      │
                         │      API        │
                         └───────┬─────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
              ▼                  ▼                  ▼
        ┌───────────┐      ┌───────────┐      ┌───────────┐
        │ PostgreSQL│      │  S3/MinIO │      │   Kafka   │
        │  Database │      │  Storage   │      │   Queue   │
        └───────────┘      └───────────┘      └─────┬─────┘
                                                    │
                                                    ▼
                                           ┌─────────────────┐
                                           │ Renderer Worker │
                                           └─────────────────┘
~~~

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

~~~bash
cd backend
poetry install
~~~

Configure the required environment variables, then apply migrations:

~~~bash
alembic upgrade head
~~~

Start the application:

~~~bash
uvicorn main:app --host 0.0.0.0 --port 8000
~~~

### Docker

~~~bash
docker build --file backend/Dockerfile -t prism-backend .
docker run --rm -p 8000:8000 prism-backend
~~~

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

The API base path is `/api/v1`. Most operations require an access token:

~~~text
Authorization: Bearer <access_token>
~~~

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

Render settings include resolution, samples, denoiser, GPU usage, background and sun parameters.

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

## Render Lifecycle

Creating a project also creates its render job.

~~~text
Client          API           Kafka        Renderer        Storage
  │              │              │             │               │
  │ Create       │              │             │               │
  │ project ────►│              │             │               │
  │              │ Render task │             │               │
  │              ├─────────────►│             │               │
  │              │              │ Task        │               │
  │              ├─────────────►│────────────►│               │
  │              │              │             │ Render        │
  │              │              │             ├──────────────►│
  │              │              │             │               │
  │              │              │ Result      │               │
  │              │◄─────────────┼─────────────┤               │
  │ Result       │              │             │               │
  │◄─────────────│              │             │               │
~~~

---

## Database Migrations

~~~bash
alembic upgrade head
alembic revision --autogenerate -m "description"
alembic downgrade -1
~~~

---

## Testing

~~~bash
pytest
~~~

## Code Quality

~~~bash
ruff check .
black .
mypy .
~~~
