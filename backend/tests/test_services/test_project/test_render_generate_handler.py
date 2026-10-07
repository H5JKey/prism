import pytest
from core.exceptions.project import ProjectIdNotFoundError
from infrastructure.database.models import File, Project
from infrastructure.minio.client import MinioClient
from pytest_mock import MockerFixture
from schemas.event import RenderGeneratedEvent
from services.project import ProjectService


class TestRenderGenerateHandler:
    async def test_handle_render_generated_valid(
        self,
        render_file: File,
        full_project: Project,
        render_generated_event: RenderGeneratedEvent,
        mocker: MockerFixture,
        minio_client: MinioClient,
        project_service: ProjectService,
    ) -> None:
        mocker.patch.object(
            project_service.project_repository,
            "get_by_id",
            return_value=full_project,
        )
        mocker.patch.object(
            minio_client,
            "get_file_size",
            return_value=1000,
        )
        mocker.patch.object(
            project_service.file_repository,
            "create_file",
            return_value=render_file,
        )
        mocker.patch.object(
            project_service.render_repository,
            "add_render_file",
            return_value=None,
        )
        await project_service.handle_render_generated(
            render_generated_event,
            minio_client,
        )

    async def test_handle_render_generated_project_not_exists(
        self,
        render_generated_event: RenderGeneratedEvent,
        mocker: MockerFixture,
        minio_client: MinioClient,
        project_service: ProjectService,
    ) -> None:
        mocker.patch.object(
            project_service.project_repository,
            "get_by_id",
            return_value=None,
        )
        with pytest.raises(ProjectIdNotFoundError):
            await project_service.handle_render_generated(
                render_generated_event,
                minio_client,
            )

    async def test_update_project_status_valid(
        self,
        full_project: Project,
        mocker: MockerFixture,
        project_service: ProjectService,
    ) -> None:
        mocker.patch.object(
            project_service.project_repository,
            "update_project_status",
            return_value=full_project,
        )
        await project_service.update_project_status(full_project.id)

    async def test_update_not_exists_project(
        self,
        full_project: Project,
        mocker: MockerFixture,
        project_service: ProjectService,
    ) -> None:
        mocker.patch.object(
            project_service.project_repository,
            "update_project_status",
            return_value=None,
        )
        with pytest.raises(ProjectIdNotFoundError):
            await project_service.update_project_status(full_project.id)
