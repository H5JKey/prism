# Backend

> FastAPI backend for distributed physically based rendering

---

## Architecture

The backend provides the API and server-side infrastructure for Prism. It manages users, projects, files and render jobs, while communicating with the renderer through Kafka and storing scene and result files in S3-compatible storage.

```
                         ┌─────────────────┐
                         │    Frontend     │
                         └────────┬────────┘
                                  │ HTTP
                                  ▼
                         ┌─────────────────┐
                         │     FastAPI     │
                         │      API        │
                         └───────┬─────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
              ▼                  ▼                  ▼
        ┌───────────┐      ┌───────────┐      ┌───────────┐
        │ PostgreSQL│      │   MinIO   │      │   Kafka   │
        │  Database │      │ S3 Storage│      │   Queue   │
        └───────────┘      └───────────┘      └─────┬─────┘
                                                    │
                                                    ▼
                                           ┌─────────────────┐
                                           │     Renderer    │
                                           │     Worker      │
                                           └─────────────────┘
```

---

## Key Features

- **REST API** – FastAPI-based HTTP API
- **Authentication** – JWT access and refresh tokens
- **Projects** – Create and manage rendering projects
- **File Storage** – Upload and download scene and render files through S3-compatible storage
- **Render Jobs** – Submit rendering tasks through Kafka
- **Async Database** – PostgreSQL with SQLAlchemy and asyncpg
- **Migrations** – Database schema management with Alembic
- **Outbox Worker** – Reliable publishing of database events to Kafka
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
| Authentication | JWT |
| Validation | Pydantic 2 |
| Metrics | Prometheus |

---

## Project Structure

```
backend/
├── api/                  # HTTP API and exception handlers
│   └── api_v1/           # Versioned API endpoints
├── core/                 # Application configuration and shared logic
├── dependencies/         # FastAPI dependencies
├── infrastructure/       # Database, Kafka and storage infrastructure
├── migrations/           # Alembic database migrations
├── outbox_worker/        # Transactional outbox publisher
├── schemas/              # Pydantic request/response schemas
├── services/             # Application services
├── tests/                # Backend tests
├── application_factory.py
├── lifespan.py
├── main.py
├── prestart.sh
├── Dockerfile
└── pyproject.toml
```

---

## Required Services

The backend depends on the following services:

- PostgreSQL
- Kafka
- S3-compatible object storage (MinIO in the development environment)

The renderer worker consumes render tasks from Kafka and writes rendered output to object storage.

---

## Configuration

The backend is configured through environment variables and supports a `.env` file.

Typical configuration includes:

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection URL |
| `KAFKA_HOST` | Kafka broker address |
| `KAFKA_TOPIC_TASKS` | Kafka topic for render tasks |
| `KAFKA_TOPIC_OUTPUT` | Kafka topic for renderer results |
| `S3_HOST` | S3-compatible storage endpoint |
| `S3_ACCESS_KEY` | S3 access key |
| `S3_SECRET_KEY` | S3 secret key |
| `JWT_SECRET_KEY` | Secret used to sign JWT tokens |

> [!NOTE]
> Refer to the configuration classes in `core/config` for the complete list of supported settings.

---

## Installation

### Poetry

The backend requires Python 3.13 or newer.

```bash
cd backend
poetry install
```

Run database migrations:

```bash
alembic upgrade head
```

Start the API:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The API is then available at `http://localhost:8000`.

FastAPI also provides interactive API documentation at:

- `/docs` – Swagger UI
- `/redoc` – ReDoc

### Docker

Build the backend image from the repository root:

```bash
docker build --file backend/Dockerfile -t prism-backend .
```

Run it with the required environment variables and services configured:

```bash
docker run --rm -p 8000:8000 prism-backend
```

For local development, the repository Docker Compose configuration can be used to start the backend together with its dependencies.

---

## Render Job Flow

A render request follows this general flow:

```
Client
  │
  │ HTTP
  ▼
FastAPI
  │
  ├──► PostgreSQL
  │       └── project / render state
  │
  ├──► S3 / MinIO
  │       └── scene / rendered image
  │
  ▼
Kafka
  │
  ▼
Renderer Worker
  │
  ▼
Kafka
  │
  ▼
FastAPI / Outbox
  │
  ▼
PostgreSQL + S3
```

The API creates the render job and publishes a task for the renderer. The worker processes the scene and reports the result back through Kafka.

---

## Authentication

The API uses JWT-based authentication.

Access and refresh tokens are issued during authentication. Protected endpoints require a valid access token.

The backend also provides password hashing using bcrypt.

---

## Testing

Run the test suite with:

```bash
pytest
```

For asynchronous tests:

```bash
pytest -v
```

---

## Code Quality

The project uses:

- **Ruff** for linting
- **Black** for formatting
- **mypy** for static type checking
- **pytest-asyncio** for asynchronous tests

Example:

```bash
ruff check .
black .
mypy .
```

---

## Database Migrations

Create a new migration:

```bash
alembic revision --autogenerate -m "description"
```

Apply migrations:

```bash
alembic upgrade head
```

Rollback the latest migration:

```bash
alembic downgrade -1
```

---

## API

The API is versioned under `api/api_v1`.

FastAPI automatically exposes the OpenAPI schema and interactive documentation when the application is running.

---

## Related Components

- [Renderer](../renderer/README.md) – physically based path tracing engine and distributed worker
- [Frontend](../frontend/README.md) – web interface for Prism
