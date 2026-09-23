import pytest
from sqlalchemy import delete
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from core.constants import (
    PROJECT_NAME_MIN_LENGTH,
    PROJECT_NAME_MAX_LENGTH,
    PROJECT_DESCRIPTION_MAX_LENGTH,
    PROJECT_DESCRIPTION_MIN_LENGTH,
)
from infrastructure.database.models import User, Project, File, Render
from tests.helpers import SQLState, assert_sqlstate_code
from tests.test_infrastructure.test_database.test_models.factories.custom_factories import (
    create_project,
)
from tests.test_infrastructure.test_database.test_models.factories.default_factories import (
    create_default_project,
)


class TestProject:
    async def test_project_valid(self, session: AsyncSession) -> None:
        project = await create_default_project(session)
        assert project.id is not None

    @pytest.mark.parametrize(
        "field, value, expected_sqlstate",
        [
            ["name", "a" * (PROJECT_NAME_MIN_LENGTH - 1), SQLState.CHECK_VIOLATION],
            ["name", "a" * (PROJECT_NAME_MAX_LENGTH + 1), SQLState.STRING_TOO_LONG],
            [
                "description",
                "a" * (PROJECT_DESCRIPTION_MAX_LENGTH + 1),
                SQLState.STRING_TOO_LONG,
            ],
        ],
    )
    async def test_project_not_valid_field_value(
        self,
        session: AsyncSession,
        field: str,
        value: str,
        expected_sqlstate: str,
    ) -> None:
        params = {field: value}
        with pytest.raises(DBAPIError) as exc_info:
            await create_default_project(session, **params)

        assert_sqlstate_code(exc_info, expected_sqlstate)

    @pytest.mark.parametrize(
        "field, value",
        [
            ["name", "a" * PROJECT_NAME_MIN_LENGTH],
            ["name", "a" * PROJECT_NAME_MAX_LENGTH],
            ["description", "a" * PROJECT_DESCRIPTION_MIN_LENGTH],
            ["description", "a" * PROJECT_DESCRIPTION_MAX_LENGTH],
        ],
    )
    async def test_project_boundary_field_value(
        self,
        session: AsyncSession,
        field: str,
        value: str,
    ) -> None:
        params = {field: value}
        project = await create_default_project(session, **params)
        assert project.id is not None

    async def test_project_default_create_date(self, session: AsyncSession) -> None:
        project = await create_default_project(session, create_date=None)
        assert project.id is not None
        assert project.create_date is not None

    @pytest.mark.parametrize(
        "status",
        [
            "rendering",
            "completed",
        ],
    )
    async def test_project_status_valid(
        self, session: AsyncSession, status: str
    ) -> None:
        project = await create_default_project(session, status=status)
        assert project.id is not None
        assert project.status == status

    @pytest.mark.parametrize(
        "status",
        [
            "pending",
            "sent",
            "public",
            "private",
        ],
    )
    async def test_project_status_not_valid(
        self,
        session: AsyncSession,
        status: str,
    ) -> None:
        with pytest.raises(DBAPIError) as exc_info:
            await create_default_project(session, status=status)

        assert_sqlstate_code(exc_info, SQLState.WRONG_ENUM_TYPE)

    @pytest.mark.parametrize(
        "visibility",
        [
            "public",
            "private",
        ],
    )
    async def test_project_visibility_valid(
        self,
        session: AsyncSession,
        visibility: str,
    ) -> None:
        project = await create_default_project(session, visibility=visibility)
        assert project.id is not None
        assert project.visibility == visibility

    @pytest.mark.parametrize(
        "visibility",
        [
            "pending",
            "sent",
            "rendering",
            "completed",
        ],
    )
    async def test_project_visibility_not_valid(
        self,
        session: AsyncSession,
        visibility: str,
    ) -> None:
        with pytest.raises(DBAPIError) as exc_info:
            await create_default_project(session, visibility=visibility)

        assert_sqlstate_code(exc_info, SQLState.WRONG_ENUM_TYPE)

    @pytest.mark.parametrize(
        "foreign_key",
        [
            "user_id",
            "source_file_id",
            "render_id",
        ],
    )
    async def test_project_without_required_foreign_key(
        self, session: AsyncSession, foreign_key: str
    ) -> None:
        params = {foreign_key: None}
        with pytest.raises(DBAPIError) as exc_info:
            await create_default_project(session, **params)

        assert_sqlstate_code(exc_info, SQLState.NOT_NULL_VIOLATION)

    async def test_project_delete_user(self, session: AsyncSession) -> None:
        project = await create_default_project(session)
        stmt = delete(User).where(User.id == project.user_id)
        await session.execute(stmt)
        session.expunge(project)

        deleted_project = await session.get(Project, project.id)
        assert deleted_project is None

    async def test_project_delete_source_file(self, session: AsyncSession) -> None:
        project = await create_default_project(session)
        stmt = delete(File).where(File.id == project.source_file_id)
        await session.execute(stmt)
        session.expunge(project)

        deleted_project = await session.get(Project, project.id)
        assert deleted_project is None

    async def test_project_delete_render(self, session: AsyncSession) -> None:
        project = await create_default_project(session)
        stmt = delete(Render).where(Render.id == project.render_id)
        await session.execute(stmt)
        session.expunge(project)

        deleted_project = await session.get(Project, project.id)
        assert deleted_project is None
