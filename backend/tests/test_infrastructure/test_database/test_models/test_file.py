import pytest
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from core.constants import (
    FILE_NAME_MAX_LENGTH,
    FILE_NAME_MIN_LENGTH,
    FILE_KEY_MAX_LENGTH,
    FILE_BUCKET_MAX_LENGTH,
    FILE_SIZE_MIN_VALUE_BYTES,
    FILE_SIZE_MAX_VALUE_BYTES,
)
from infrastructure.database.models import File
from tests.helpers import SQLState, assert_sqlstate_code


async def create_file(session: AsyncSession, **kwargs) -> File:
    file_data = {
        "name": "file_name",
        "size": 1000,
        "bucket": "test_bucket",
        "key": "test_key",
    }
    file = File(**file_data)
    for field, value in kwargs.items():
        setattr(file, field, value)

    session.add(file)
    await session.flush()
    return file


class TestFile:
    async def test_file_valid(self, session: AsyncSession) -> None:
        await create_file(session)

    async def test_file_default_fields(self, session: AsyncSession) -> None:
        file = await create_file(session)
        assert file.id is not None

    @pytest.mark.parametrize(
        "field, value, expected_sqlstate",
        [
            ["name", "a" * (FILE_NAME_MIN_LENGTH - 1), SQLState.CHECK_VIOLATION],
            ["name", "a" * (FILE_NAME_MAX_LENGTH + 1), SQLState.STRING_TOO_LONG],
            ["size", FILE_SIZE_MIN_VALUE_BYTES, SQLState.CHECK_VIOLATION],
            ["size", FILE_SIZE_MAX_VALUE_BYTES + 1, SQLState.CHECK_VIOLATION],
            ["bucket", "a" * (FILE_BUCKET_MAX_LENGTH + 1), SQLState.STRING_TOO_LONG],
            ["key", "a" * (FILE_KEY_MAX_LENGTH + 1), SQLState.STRING_TOO_LONG],
        ],
    )
    async def test_file_not_valid_field_value(
        self,
        session: AsyncSession,
        field: str,
        value: str | int,
        expected_sqlstate: str,
    ) -> None:
        params = {field: value}
        with pytest.raises(DBAPIError) as exc_info:
            await create_file(session, **params)

        assert_sqlstate_code(exc_info, expected_sqlstate)

    @pytest.mark.parametrize(
        "field, value",
        [
            ["name", "a" * FILE_NAME_MIN_LENGTH],
            ["name", "a" * FILE_NAME_MAX_LENGTH],
            ["size", FILE_SIZE_MIN_VALUE_BYTES + 1],
            ["size", FILE_SIZE_MAX_VALUE_BYTES],
            ["bucket", ""],
            ["bucket", "a" * FILE_BUCKET_MAX_LENGTH],
            ["key", ""],
            ["key", "a" * FILE_KEY_MAX_LENGTH],
        ],
    )
    async def test_file_boundary_field_value(
        self,
        session: AsyncSession,
        field: str,
        value: str | int,
    ) -> None:
        params = {field: value}
        file = await create_file(session, **params)
        assert file.id is not None

    async def test_file_path_unique_constraint_failed(
        self,
        session: AsyncSession,
    ) -> None:
        test_bucket = "test_bucket"
        test_key = "test_key"
        await create_file(session, bucket=test_bucket, key=test_key)
        with pytest.raises(DBAPIError) as exc_info:
            await create_file(session, bucket=test_bucket, key=test_key)

        assert_sqlstate_code(exc_info, SQLState.UNIQUE_VIOLATION)

    @pytest.mark.parametrize(
        "bucket1, bucket2, key1, key2",
        [
            ["bucket", "bucket", "key1", "key2"],
            ["bucket1", "bucket2", "key", "key"],
            ["bucket1", "bucket2", "key1", "key2"],
        ],
    )
    async def test_file_path_unique_constraint_passed(
        self,
        session: AsyncSession,
        bucket1: str,
        bucket2: str,
        key1: str,
        key2: str,
    ) -> None:
        file1 = await create_file(session, bucket=bucket1, key=key1)
        file2 = await create_file(session, bucket=bucket2, key=key2)
        assert file1.id is not None
        assert file2.id is not None
