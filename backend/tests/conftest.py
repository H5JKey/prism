from collections.abc import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, create_autospec

import pytest
from infrastructure.database.unit_of_work import UnitOfWork
from infrastructure.minio.client import MinioClient
from services.auth import AuthService
from services.file_uploader import FileUploader
from services.projects.project import ProjectService
from services.projects.project_access_validator import ProjectAccessValidatorService
from services.projects.project_pagination import ProjectPaginationService
from services.projects.render_generate_handler import RenderGenerateHandlerService
from services.tag import TagService
from services.user import UserService
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from testcontainers.community.postgres import PostgresContainer

from tests.helpers import run_migrations


@pytest.fixture(scope="session")
def database_container() -> Generator[PostgresContainer]:
    with PostgresContainer(
        image="postgres:17-bookworm",
        driver="asyncpg",
    ) as postgres_container:
        run_migrations(postgres_container)
        yield postgres_container


@pytest.fixture(scope="session")
async def engine(
    database_container: PostgresContainer,
) -> AsyncGenerator[AsyncEngine]:
    database_url = database_container.get_connection_url()
    engine = create_async_engine(database_url)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="session")
async def session_factory(
    engine: AsyncEngine,
) -> AsyncGenerator[async_sessionmaker]:
    session_maker = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )
    yield session_maker


@pytest.fixture(scope="function")
async def session(
    session_factory: async_sessionmaker,
) -> AsyncGenerator[AsyncSession]:
    async with session_factory() as session:
        yield session


@pytest.fixture(scope="function")
async def unit_of_work(
    session: AsyncSession,
) -> AsyncGenerator[UnitOfWork]:
    unit_of_work = UnitOfWork(session)
    yield unit_of_work
    await unit_of_work.rollback()


@pytest.fixture(scope="function")
async def auth_service(
    unit_of_work: UnitOfWork,
) -> AuthService:
    auth_service = AuthService(unit_of_work)
    return auth_service


@pytest.fixture(scope="function")
async def user_service(
    unit_of_work: UnitOfWork,
) -> UserService:
    user_service = UserService(unit_of_work)
    return user_service


@pytest.fixture(scope="function")
def minio_client() -> MinioClient:
    minio_client = create_autospec(MinioClient, instance=True)
    minio_client.get_file_size = AsyncMock(return_value=1000)
    minio_client.generate_presigned_url = MagicMock(return_value="presigned_url")
    minio_client.get_object = AsyncMock(return_value=b"test_object")
    minio_client.put_object = AsyncMock(return_value=None)
    minio_client.delete_object = AsyncMock(return_value=None)
    minio_client.generate_key = MagicMock(return_value="generated_key")
    return minio_client


@pytest.fixture(scope="function")
async def file_uploader(
    minio_client: MinioClient,
    unit_of_work: UnitOfWork,
) -> FileUploader:
    file_uploader = FileUploader(
        bucket="bucket",
        s3_client=minio_client,
        unit_of_work=unit_of_work,
    )
    return file_uploader


@pytest.fixture(scope="function")
def project_access_validator(
    unit_of_work: UnitOfWork,
) -> ProjectAccessValidatorService:
    project_access_validator = ProjectAccessValidatorService(unit_of_work)
    return project_access_validator


@pytest.fixture(scope="function")
def project_service(
    unit_of_work: UnitOfWork,
    project_access_validator: ProjectAccessValidatorService,
) -> ProjectService:
    project_service = ProjectService(unit_of_work, project_access_validator)
    return project_service


@pytest.fixture(scope="function")
def project_pagination_service(
    unit_of_work: UnitOfWork,
) -> ProjectPaginationService:
    project_pagination_service = ProjectPaginationService(unit_of_work)
    return project_pagination_service


@pytest.fixture(scope="function")
def render_generate_handler(
    unit_of_work: UnitOfWork,
) -> RenderGenerateHandlerService:
    render_generate_handler_service = RenderGenerateHandlerService(unit_of_work)
    return render_generate_handler_service


@pytest.fixture(scope="function")
def tag_service(
    unit_of_work: UnitOfWork,
) -> TagService:
    tag_service = TagService(unit_of_work)
    return tag_service
