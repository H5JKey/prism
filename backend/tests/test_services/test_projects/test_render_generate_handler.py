import pytest
from core.exceptions.project import ProjectIdNotFoundError
from infrastructure.database.models import File, Project
from infrastructure.minio.client import MinioClient
from pytest_mock import MockerFixture
from schemas.event import RenderGeneratedEvent
from services.projects.render_generate_handler import RenderGenerateHandlerService


class TestRenderGenerateHandler:
    async def test_handle_render_generated_valid(
        self,
        render_file: File,
        full_project: Project,
        render_generated_event: RenderGeneratedEvent,
        mocker: MockerFixture,
        minio_client: MinioClient,
        render_generate_handler: RenderGenerateHandlerService,
    ) -> None:
        get_project_by_id_mock = mocker.patch.object(
            render_generate_handler.project_repository,
            "get_by_id",
            return_value=full_project,
        )
        get_file_size_mock = mocker.patch.object(
            minio_client,
            "get_file_size",
            return_value=1000,
        )
        create_file_mock = mocker.patch.object(
            render_generate_handler.file_repository,
            "create_file",
            return_value=render_file,
        )
        add_render_file_mock = mocker.patch.object(
            render_generate_handler.render_repository,
            "add_render_file",
            return_value=None,
        )
        await render_generate_handler.handle_render_generated(
            render_generated_event,
            minio_client,
        )

        get_project_by_id_mock.assert_called_once_with(full_project.id)
        get_file_size_mock.assert_called_once()
        create_file_mock.assert_called_once()
        add_render_file_mock.assert_called_once_with(
            render_id=full_project.render_id,
            file_id=render_file.id,
        )

    async def test_handle_render_generated_project_not_exists(
        self,
        render_generated_event: RenderGeneratedEvent,
        mocker: MockerFixture,
        minio_client: MinioClient,
        render_generate_handler: RenderGenerateHandlerService,
    ) -> None:
        get_project_by_id_mock = mocker.patch.object(
            render_generate_handler.project_repository,
            "get_by_id",
            return_value=None,
        )
        with pytest.raises(ProjectIdNotFoundError):
            await render_generate_handler.handle_render_generated(
                render_generated_event,
                minio_client,
            )

        get_project_by_id_mock.assert_called_once_with(
            render_generated_event.project_id,
        )

    async def test_update_project_status_valid(
        self,
        full_project: Project,
        mocker: MockerFixture,
        render_generate_handler: RenderGenerateHandlerService,
    ) -> None:
        update_project_status_mock = mocker.patch.object(
            render_generate_handler.project_repository,
            "update_project_status",
            return_value=full_project,
        )
        await render_generate_handler.update_project_status(full_project.id)
        update_project_status_mock.assert_called_once_with(full_project.id)

    async def test_update_not_exists_project(
        self,
        full_project: Project,
        mocker: MockerFixture,
        render_generate_handler: RenderGenerateHandlerService,
    ) -> None:
        update_project_status_mock = mocker.patch.object(
            render_generate_handler.project_repository,
            "update_project_status",
            return_value=None,
        )
        with pytest.raises(ProjectIdNotFoundError):
            await render_generate_handler.update_project_status(full_project.id)
        update_project_status_mock.assert_called_once_with(full_project.id)
