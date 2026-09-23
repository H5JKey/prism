import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.repositories import FileRepository


@pytest.fixture(scope="function")
def file_repository(session: AsyncSession) -> FileRepository:
    return FileRepository(session)
