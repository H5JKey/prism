import pytest
from core.constants import ProjectVisibility
from core.exceptions.auth import PermissionDeniedError
from core.exceptions.file import FileIdNotFoundError
from core.exceptions.project import ProjectIdNotFoundError
from core.exceptions.user import UserIdNotFoundError
from infrastructure.database.models import File, Project, Render, User
from infrastructure.minio.client import MinioClient
from pytest_mock import MockerFixture
from schemas.event import RenderGeneratedEvent
from schemas.project import (
    ProjectPartialUpdate,
    ProjectWithRenderCreate,
)
from services.project import ProjectService


class TestProjectService:
    async def test_get_by_id_valid(
        self,
        project_owner: User,
        full_project: Project,
        mocker: MockerFixture,
        minio_client: MinioClient,
        project_service: ProjectService,
    ) -> None:
        mocker.patch.object(
            project_service,
            "_validate_access_to_get_project",
            return_value=full_project,
            autospec=True,
        )

        mocker.patch(
            "services.project.ProjectWithRenderFileFullResponse.get_from_database",
            return_value=full_project,
            autospec=True,
        )

        await project_service.get_by_id(
            full_project.id,
            project_owner.id,
            minio_client,
        )

    async def test_get_by_id_project_not_exists(
        self,
        project_owner: User,
        full_project: Project,
        mocker: MockerFixture,
        minio_client: MinioClient,
        project_service: ProjectService,
    ) -> None:
        mocker.patch.object(
            project_service.project_repository,
            "get_by_id",
            return_value=None,
            autospec=True,
        )
        with pytest.raises(ProjectIdNotFoundError):
            await project_service.get_by_id(
                full_project.id,
                project_owner.id,
                minio_client,
            )

    async def test_get_private_project_by_id_not_by_owner(
        self,
        project_owner: User,
        full_project: Project,
        mocker: MockerFixture,
        minio_client: MinioClient,
        project_service: ProjectService,
    ) -> None:
        full_project.visibility = ProjectVisibility.private
        mocker.patch.object(
            project_service.project_repository,
            "get_by_id",
            return_value=full_project,
            autospec=True,
        )
        mocker.patch.object(
            project_service.project_repository,
            "get_project_owner",
            return_value=project_owner,
            autospec=True,
        )
        with pytest.raises(PermissionDeniedError):
            await project_service.get_by_id(
                full_project.id,
                project_owner.id + 1,
                minio_client,
            )

    async def test_get_user_projects_valid(
        self,
        project_owner: User,
        full_project: Project,
        mocker: MockerFixture,
        project_service: ProjectService,
    ) -> None:
        mocker.patch.object(
            project_service.user_repository,
            "get_by_id",
            return_value=project_owner,
        )
        mocker.patch.object(
            project_service.project_repository,
            "get_user_projects",
            return_value=[full_project],
            autospec=True,
        )
        await project_service.get_user_projects(
            project_owner.id,
            size=10,
            page=1,
        )

    async def test_get_user_projects_user_not_exists(
        self,
        project_owner: User,
        mocker: MockerFixture,
        project_service: ProjectService,
    ) -> None:
        mocker.patch.object(
            project_service.user_repository,
            "get_by_id",
            return_value=None,
            autospec=True,
        )
        with pytest.raises(UserIdNotFoundError):
            await project_service.get_user_projects(
                project_owner.id,
                size=10,
                page=1,
            )

    async def test_get_public_projects_valid(
        self,
        full_project: Project,
        mocker: MockerFixture,
        project_service: ProjectService,
    ) -> None:
        mocker.patch.object(
            project_service.project_repository,
            "get_public_projects",
            return_value=[full_project],
            autospec=True,
        )
        await project_service.get_public_projects(
            size=10,
            page=1,
        )

    async def test_get_user_public_projects_valid(
        self,
        project_owner: User,
        mocker: MockerFixture,
        project_service: ProjectService,
    ) -> None:
        mocker.patch.object(
            project_service.user_repository,
            "get_by_id",
            return_value=project_owner,
        )
        await project_service.get_user_public_projects(
            user_id=project_owner.id,
            size=10,
            page=1,
        )

    async def test_get_user_public_projects_user_not_exists(
        self,
        project_owner: User,
        mocker: MockerFixture,
        project_service: ProjectService,
    ) -> None:
        mocker.patch.object(
            project_service.user_repository,
            "get_by_id",
            return_value=None,
        )
        with pytest.raises(UserIdNotFoundError):
            await project_service.get_user_public_projects(
                user_id=project_owner.id,
                size=10,
                page=1,
            )

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

    async def test_create_project_valid(
        self,
        create_project_request: ProjectWithRenderCreate,
        render: Render,
        source_file: File,
        project_owner: User,
        full_project: Project,
        mocker: MockerFixture,
        project_service: ProjectService,
    ) -> None:
        mocker.patch.object(
            project_service.file_repository,
            "get_by_id",
            return_value=source_file,
            autospec=True,
        )
        mocker.patch.object(
            project_service.render_repository,
            "create_render",
            return_value=render,
            autospec=True,
        )
        mocker.patch.object(
            project_service.project_repository,
            "create_project",
            return_value=full_project,
            autospec=True,
        )
        mocker.patch.object(
            project_service.outbox_repository,
            "create_event",
            return_value=None,
            autospec=True,
        )

        await project_service.create_project(
            user_id=project_owner.id,
            create_project=create_project_request,
        )

    async def test_create_project_file_not_exists(
        self,
        create_project_request: ProjectWithRenderCreate,
        project_owner: User,
        mocker: MockerFixture,
        project_service: ProjectService,
    ) -> None:
        mocker.patch.object(
            project_service.file_repository,
            "get_by_id",
            return_value=None,
            autospec=True,
        )
        with pytest.raises(FileIdNotFoundError):
            await project_service.create_project(
                user_id=project_owner.id,
                create_project=create_project_request,
            )

    async def test_partial_update_project_valid(
        self,
        project_owner: User,
        full_project: Project,
        mocker: MockerFixture,
        project_service: ProjectService,
    ) -> None:
        mocker.patch.object(
            project_service.project_repository,
            "get_by_id",
            return_value=full_project,
            autospec=True,
        )

        mocker.patch.object(
            project_service.project_repository,
            "get_project_owner",
            return_value=project_owner,
            autospec=True,
        )
        partial_update_project_data = ProjectPartialUpdate(
            visibility=ProjectVisibility.private,
        )
        await project_service.partial_update_project(
            full_project.id,
            project_owner.id,
            partial_update_project_data,
        )

    async def test_partial_update_project_not_exists(
        self,
        project_owner: User,
        full_project: Project,
        mocker: MockerFixture,
        project_service: ProjectService,
    ) -> None:
        mocker.patch.object(
            project_service.project_repository,
            "get_by_id",
            return_value=None,
            autospec=True,
        )
        partial_update_project_data = ProjectPartialUpdate(
            visibility=ProjectVisibility.private,
        )
        with pytest.raises(ProjectIdNotFoundError):
            await project_service.partial_update_project(
                full_project.id,
                project_owner.id,
                partial_update_project_data,
            )

    async def test_partial_update_project_not_by_owner(
        self,
        project_owner: User,
        full_project: Project,
        mocker: MockerFixture,
        project_service: ProjectService,
    ) -> None:
        mocker.patch.object(
            project_service.project_repository,
            "get_by_id",
            return_value=full_project,
            autospec=True,
        )
        mocker.patch.object(
            project_service.project_repository,
            "get_project_owner",
            return_value=project_owner,
            autospec=True,
        )
        partial_update_project_data = ProjectPartialUpdate(
            description="new description",
        )
        with pytest.raises(PermissionDeniedError):
            await project_service.partial_update_project(
                full_project.id,
                project_owner.id + 1,
                partial_update_project_data,
            )

    async def test_delete_by_id_valid(
        self,
        project_owner: User,
        full_project: Project,
        mocker: MockerFixture,
        project_service: ProjectService,
    ) -> None:
        mocker.patch.object(
            project_service.project_repository,
            "get_by_id",
            return_value=full_project,
        )
        mocker.patch.object(
            project_service.project_repository,
            "get_project_owner",
            return_value=project_owner,
        )
        await project_service.delete_by_id(full_project.id, project_owner.id)

    async def test_delete_by_id_project_not_exists(
        self,
        project_owner: User,
        full_project: Project,
        mocker: MockerFixture,
        project_service: ProjectService,
    ) -> None:
        mocker.patch.object(
            project_service.project_repository,
            "get_by_id",
            return_value=None,
        )
        with pytest.raises(ProjectIdNotFoundError):
            await project_service.delete_by_id(full_project.id, project_owner.id)

    async def test_delete_by_id_not_by_owner(
        self,
        project_owner: User,
        full_project: Project,
        mocker: MockerFixture,
        project_service: ProjectService,
    ) -> None:
        mocker.patch.object(
            project_service.project_repository,
            "get_by_id",
            return_value=None,
        )
        mocker.patch.object(
            project_service.project_repository,
            "get_project_owner",
            return_value=project_owner,
        )
        with pytest.raises(ProjectIdNotFoundError):
            await project_service.delete_by_id(full_project.id, project_owner.id + 1)
