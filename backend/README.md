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

## Configuration

The backend uses environment variables for configuration.

Create a `.env` file in the `backend` directory. Nested settings use `__` as a separator.
> [!IMPORTANT]
> Environment variables take precedence over values defined in the `.env` file.

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE__USERNAME` | PostgreSQL username | `username` |
| `DATABASE__PASSWORD` | PostgreSQL password | `password` |
| `DATABASE__HOST` | PostgreSQL host | `localhost` |
| `DATABASE__PORT` | PostgreSQL port | `5432` |
| `DATABASE__DB_NAME` | PostgreSQL database name | `renderer` |
| `DATABASE__POOL_SIZE` | SQLAlchemy connection pool size | `5` |
| `DATABASE__MAX_OVERFLOW` | Maximum additional connections | `10` |
| `DATABASE__POOL_TIMEOUT` | Connection pool timeout in seconds | `30` |
| `DATABASE__POOL_RECYCLE` | Connection recycle time in seconds | `3600` |
| `DATABASE__POOL_PRE_PING` | Check connections before use | `true` |
| `DATABASE__EXPIRE_ON_COMMIT` | Expire ORM objects after commit | `true` |
| `DATABASE__ECHO` | Enable SQLAlchemy SQL logging | `false` |
| `MINIO__HOST` | S3 / MinIO host | `minio` |
| `MINIO__PORT` | S3 / MinIO port | `9000` |
| `MINIO__USERNAME` | S3 / MinIO access key | `adminadmin` |
| `MINIO__PASSWORD` | S3 / MinIO secret key | `adminadmin` |
| `MINIO__BUCKET__GLB_SOURCES` | Bucket for source GLB files | `input` |
| `MINIO__BUCKET__RENDERS` | Bucket for rendered images | `output` |
| `MINIO__PRESIGNED_URL_TTL_SECONDS` | Lifetime of generated presigned URLs | `600` |
| `KAFKA__HOST` | Kafka broker host | `kafka` |
| `KAFKA__PORT` | Kafka broker port | `9092` |
| `KAFKA__GROUP_ID` | Kafka consumer group ID | `backend` |
| `KAFKA__BASE_DELAY_SECONDS` | Initial retry delay | `1` |
| `KAFKA__MAX_DELAY_SECONDS` | Maximum retry delay | `120` |
| `KAFKA__TOPIC__PROJECT_CREATED` | Topic for project creation events | `create_project` |
| `KAFKA__TOPIC__RENDER_GENERATED` | Topic for render result events | `generate_model` |
| `KAFKA__TOPIC__DEAD_LETTER_QUEUE` | Dead letter queue topic | `dead_letter_queue` |
| `JWT__ACCESS_TOKEN_EXPIRES_IN_MINUTES` | Access token lifetime | `15` |
| `JWT__REFRESH_TOKEN_EXPIRES_IN_MINUTES` | Refresh token lifetime | `43200` |
| `JWT__ALGORITHM` | JWT signing algorithm | `RS256` |
| `JWT__PUBLIC_KEY_PATH` | Path to JWT public key | `certs/jwt-public.pem` |
| `JWT__PRIVATE_KEY_PATH` | Path to JWT private key | `certs/jwt-private.pem` |
| `LOGGING__LEVEL` | Logging level | `DEBUG` |
| `LOGGING__BASE_LOGGER_NAME` | Base logger name | `backend` |
| `LOGGING__FORMATTER__FORMAT` | Log message format | See configuration |
| `LOGGING__FORMATTER__DATEFMT` | Log date format | `%Y-%m-%d %H:%M:%S` |

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
