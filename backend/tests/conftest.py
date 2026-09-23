from collections.abc import AsyncGenerator, Generator

import pytest
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
