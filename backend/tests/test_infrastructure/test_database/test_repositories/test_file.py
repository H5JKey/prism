from infrastructure.database.repositories import FileRepository
from schemas.file import FileCreate
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_infrastructure.test_database.test_models.factories import create_file


class TestFileRepository:
    async def test_get_by_id(
        self,
        session: AsyncSession,
        file_repository: FileRepository,
    ) -> None:
        file = await create_file(session)
        session.expunge(file)
        selected_file = await file_repository.get_by_id(file.id)
        assert selected_file.id == file.id
        assert selected_file.name == file.name
        assert selected_file.size == file.size
        assert selected_file.bucket == file.bucket
        assert selected_file.key == file.key

    async def test_get_by_id_not_exists_file(
        self,
        file_repository: FileRepository,
    ) -> None:
        selected_file = await file_repository.get_by_id(-1)
        assert selected_file is None

    async def test_create_file(
        self,
        session: AsyncSession,
        file_repository: FileRepository,
    ) -> None:
        create_file_data = FileCreate(
            name="file_name",
            size=1024,
            bucket="bucket",
            key="key",
        )
        created_file = await file_repository.create_file(create_file_data)
        session.expunge(created_file)
        selected_file = await file_repository.get_by_id(created_file.id)
        assert selected_file is not None
        assert selected_file.name == create_file_data.name
        assert selected_file.size == create_file_data.size
        assert selected_file.bucket == create_file_data.bucket
        assert selected_file.key == create_file_data.key

    async def test_delete_by_id(
        self,
        session: AsyncSession,
        file_repository: FileRepository,
    ) -> None:
        file = await create_file(session)
        await file_repository.delete_by_id(file.id)
        session.expunge(file)
        deleted_file = await file_repository.get_by_id(file.id)
        assert deleted_file is None
