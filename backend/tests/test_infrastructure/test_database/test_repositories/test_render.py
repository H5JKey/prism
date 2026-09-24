from infrastructure.database.repositories import RenderRepository
from schemas.render import RenderCreate
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_infrastructure.test_database.test_models.factories import (
    create_file,
    create_render,
)


class TestRenderRepository:
    async def test_get_by_id(
        self,
        session: AsyncSession,
        render_repository: RenderRepository,
    ) -> None:
        render = await create_render(session)
        session.expunge(render)
        selected_render = await render_repository.get_by_id(render.id)
        assert selected_render.id == render.id
        assert selected_render.width == render.width
        assert selected_render.height == render.height
        assert selected_render.samples == render.samples
        assert selected_render.denoiser == render.denoiser
        assert selected_render.gpu == render.gpu
        assert selected_render.file_id == render.file_id

    async def test_get_by_id_not_exist(
        self,
        render_repository: RenderRepository,
    ) -> None:
        selected_render = await render_repository.get_by_id(-1)
        assert selected_render is None

    async def test_create_render(
        self,
        render_repository: RenderRepository,
    ) -> None:
        create_render_data = RenderCreate(
            width=1000,
            height=1000,
            samples=100,
            denoiser=False,
            gpu=False,
        )
        created_render = await render_repository.create_render(create_render_data)
        selected_render = await render_repository.get_by_id(created_render.id)
        assert selected_render.id == created_render.id
        assert selected_render.width == create_render_data.width
        assert selected_render.height == create_render_data.height
        assert selected_render.samples == create_render_data.samples
        assert selected_render.denoiser == create_render_data.denoiser
        assert selected_render.gpu == created_render.gpu
        assert selected_render.file_id == created_render.file_id

    async def test_add_render_file(
        self,
        session: AsyncSession,
        render_repository: RenderRepository,
    ) -> None:
        file = await create_file(session)
        render = await create_render(session)
        await render_repository.add_render_file(render.id, file.id)
        session.expunge(render)
        selected_render = await render_repository.get_by_id(render.id)
        assert selected_render.id == render.id
        assert selected_render.width == render.width
        assert selected_render.height == render.height
        assert selected_render.samples == render.samples
        assert selected_render.denoiser == render.denoiser
        assert selected_render.gpu == render.gpu
        assert selected_render.file_id == file.id
