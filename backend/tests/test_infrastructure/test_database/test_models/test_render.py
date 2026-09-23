import pytest
from core.constants import (
    RENDER_HEIGHT_MAX_VALUE,
    RENDER_HEIGHT_MIN_VALUE,
    RENDER_SAMPLES_MAX_VALUE,
    RENDER_SAMPLES_MIN_VALUE,
    RENDER_WIDTH_MAX_VALUE,
    RENDER_WIDTH_MIN_VALUE,
)
from infrastructure.database.models import File, Render
from sqlalchemy import delete
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from tests.helpers import SQLState, assert_sqlstate_code
from tests.test_infrastructure.test_database.test_models.factories import (
    create_file,
    create_project,
    create_render,
    create_user,
)


class TestRender:
    async def test_render_valid(self, session: AsyncSession) -> None:
        render = await create_render(session)
        assert render.id is not None
        assert render.file_id is None

    async def test_render_with_file_valid(self, session: AsyncSession) -> None:
        file = await create_file(session)
        render = await create_render(session, file_id=file.id)
        assert render.id is not None
        assert render.file_id == file.id

    @pytest.mark.parametrize(
        "field, value, expected_sqlstate",
        [
            ["width", RENDER_WIDTH_MIN_VALUE - 1, SQLState.CHECK_VIOLATION],
            ["width", RENDER_WIDTH_MAX_VALUE + 1, SQLState.CHECK_VIOLATION],
            ["height", RENDER_HEIGHT_MIN_VALUE - 1, SQLState.CHECK_VIOLATION],
            ["height", RENDER_HEIGHT_MAX_VALUE + 1, SQLState.CHECK_VIOLATION],
            ["samples", RENDER_SAMPLES_MIN_VALUE - 1, SQLState.CHECK_VIOLATION],
            ["samples", RENDER_SAMPLES_MAX_VALUE + 1, SQLState.CHECK_VIOLATION],
        ],
    )
    async def test_render_not_valid_field_value(
        self,
        session: AsyncSession,
        field: str,
        value: str,
        expected_sqlstate: str,
    ) -> None:
        params = {field: value}
        with pytest.raises(DBAPIError) as exc_info:
            await create_render(session, **params)

        assert_sqlstate_code(exc_info, expected_sqlstate)

    @pytest.mark.parametrize(
        "field, value",
        [
            ["width", RENDER_WIDTH_MIN_VALUE],
            ["width", RENDER_WIDTH_MAX_VALUE],
            ["height", RENDER_HEIGHT_MIN_VALUE],
            ["height", RENDER_HEIGHT_MAX_VALUE],
            ["samples", RENDER_SAMPLES_MIN_VALUE],
            ["samples", RENDER_SAMPLES_MAX_VALUE],
            ["denoiser", False],
            ["denoiser", True],
            ["gpu", False],
            ["gpu", True],
        ],
    )
    async def test_render_boundary_field_value(
        self,
        session: AsyncSession,
        field: str,
        value: str,
    ) -> None:
        params = {field: value}
        render = await create_render(session, **params)
        assert render.id is not None

    async def test_render_file_id_delete(self, session: AsyncSession) -> None:
        file = await create_file(session)
        render = await create_render(session, file_id=file.id)

        stmt = delete(File).where(File.id == file.id)
        await session.execute(stmt)

        session.expunge_all()
        deleted_render = await session.get(Render, render.id)
        assert deleted_render is None

    async def test_render_empty_file_relationship_valid(
        self,
        session: AsyncSession,
    ) -> None:
        render = await create_render(session)
        await session.refresh(render, ["file"])
        assert render.file is None

    async def test_render_file_relationship_valid(
        self,
        session: AsyncSession,
    ) -> None:
        file = await create_file(session)
        render = await create_render(session, file=file)
        await session.refresh(render, ["file"])
        assert render.file is file

    async def test_render_project_relationship_valid(
        self,
        session: AsyncSession,
    ) -> None:
        user = await create_user(session)
        file = await create_file(session)
        render = await create_render(session)
        project = await create_project(
            session,
            user=user,
            source_file=file,
            render=render,
        )
        await session.refresh(render, ["project"])
        assert render.project is project
