import pytest
from infrastructure.database.repositories import (
    FileRepository,
    OutboxRepository,
    ProjectRepository,
    RenderRepository,
    TagRepository,
    UserRepository,
)
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture(scope="function")
def file_repository(session: AsyncSession) -> FileRepository:
    return FileRepository(session)


@pytest.fixture(scope="function")
def outbox_repository(session: AsyncSession) -> OutboxRepository:
    return OutboxRepository(session)


@pytest.fixture(scope="function")
def user_repository(session: AsyncSession) -> UserRepository:
    return UserRepository(session)


@pytest.fixture(scope="function")
def tag_repository(session: AsyncSession) -> TagRepository:
    return TagRepository(session)


@pytest.fixture(scope="function")
def render_repository(session: AsyncSession) -> RenderRepository:
    return RenderRepository(session)


@pytest.fixture(scope="function")
def project_repository(session: AsyncSession) -> ProjectRepository:
    return ProjectRepository(session)
