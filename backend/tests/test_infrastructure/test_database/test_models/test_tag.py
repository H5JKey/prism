import pytest
from sqlalchemy import delete
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from core.constants import TAG_MIN_LENGTH, TAG_MAX_LENGTH
from infrastructure.database.models import Project, Tag
from tests.helpers import SQLState, assert_sqlstate_code
from tests.test_infrastructure.test_database.test_models.model_factories import (
    create_tag,
)


class TestTag:
    async def test_tag_valid(self, session: AsyncSession) -> None:
        tag = await create_tag(session)
        assert tag.id is not None

    @pytest.mark.parametrize(
        "field, value, expected_sqlstate",
        [
            ["name", "a" * (TAG_MIN_LENGTH - 1), SQLState.CHECK_VIOLATION],
            ["name", "a" * (TAG_MAX_LENGTH + 1), SQLState.STRING_TOO_LONG],
        ],
    )
    async def test_tag_not_valid_field_value(
        self,
        session: AsyncSession,
        field: str,
        value: str,
        expected_sqlstate: str,
    ) -> None:
        params = {field: value}
        with pytest.raises(DBAPIError) as exc_info:
            await create_tag(session, **params)

        assert_sqlstate_code(exc_info, expected_sqlstate)

    @pytest.mark.parametrize(
        "field, value",
        [
            ["name", "a" * TAG_MIN_LENGTH],
            ["name", "a" * TAG_MAX_LENGTH],
        ],
    )
    async def test_tag_boundary_field_value(
        self,
        session: AsyncSession,
        field: str,
        value: str,
    ) -> None:
        params = {field: value}
        tag = await create_tag(session, **params)
        assert tag.id is not None

    async def test_tag_without_project_id(self, session: AsyncSession) -> None:
        with pytest.raises(DBAPIError) as exc_info:
            await create_tag(session, project_id=None)

        assert_sqlstate_code(exc_info, SQLState.NOT_NULL_VIOLATION)

    async def test_tag_delete_project(self, session: AsyncSession) -> None:
        tag = await create_tag(session)
        stmt = delete(Project).where(Project.id == tag.project_id)
        await session.execute(stmt)
        session.expunge(tag)

        deleted_tag = await session.get(Tag, tag.id)
        assert deleted_tag is None
