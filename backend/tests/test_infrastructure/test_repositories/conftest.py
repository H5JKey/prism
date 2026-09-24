import pytest
from infrastructure.database.repositories import FileRepository, OutboxRepository
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture(scope="function")
def file_repository(session: AsyncSession) -> FileRepository:
    return FileRepository(session)


@pytest.fixture(scope="function")
def outbox_repository(session: AsyncSession) -> OutboxRepository:
    return OutboxRepository(session)
