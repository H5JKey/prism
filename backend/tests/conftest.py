from collections.abc import AsyncGenerator, Generator

import pytest
from aiobotocore import session as minio_session
from aiobotocore.client import AioBaseClient
from aiobotocore.session import AioSession
from infrastructure.database.unit_of_work import UnitOfWork
from infrastructure.minio.client import MinioClient
from services.auth import AuthService
from services.file_uploader import FileUploader
from services.user import UserService
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from testcontainers.community.minio import MinioContainer
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
def s3_container() -> Generator[MinioContainer]:
    with MinioContainer("quay.io/minio/minio") as minio_container:
        yield minio_container


@pytest.fixture(scope="session")
async def s3_session() -> AioSession:
    return minio_session.get_session()


@pytest.fixture(scope="function")
def s3_config(s3_container: MinioContainer) -> dict:
    connection_params = s3_container.get_config()
    host = s3_container.get_container_host_ip()
    endpoint_url = f"http://{host}:{s3_container.port}"
    return {
        "endpoint_url": endpoint_url,
        "aws_access_key_id": connection_params["access_key"],
        "aws_secret_access_key": connection_params["secret_key"],
    }


@pytest.fixture(scope="function")
async def s3_client(
    s3_session: AioSession,
    s3_config: dict,
) -> AsyncGenerator[AioBaseClient]:
    async with s3_session.create_client(
        "s3",
        **s3_config,
    ) as client:
        yield client


@pytest.fixture(scope="function")
def minio_client(s3_client: AioBaseClient) -> MinioClient:
    return MinioClient(s3_client)


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
