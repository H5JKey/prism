import pytest
from core.constants import ProjectVisibility
from core.exceptions.auth import PermissionDeniedError
from core.exceptions.file import FileIdNotFoundError
from core.exceptions.project import ProjectIdNotFoundError
from infrastructure.database.models import File, Project, Render, User
from infrastructure.minio.client import MinioClient
from pytest_mock import MockerFixture
from schemas.project import (
    ProjectPartialUpdate,
    ProjectWithRenderCreate,
)
from services.projects.project import ProjectService


class TestProjectService:
    async def test_get_by_id_valid(
        self,
        project_owner: User,
        full_project: Project,
        mocker: MockerFixture,
        minio_client: MinioClient,
        project_service: ProjectService,
    ) -> None:
        validator_mock = mocker.patch.object(
            project_service.project_access_validator,
            "validate_access_to_get_project",
            return_value=full_project,
            autospec=True,
        )
        get_from_database_mock = mocker.patch(
            "services.projects.project.ProjectWithRenderFileFullResponse.get_from_database",
            return_value=full_project,
            autospec=True,
        )

        await project_service.get_by_id(
            full_project.id,
            project_owner.id,
            minio_client,
        )
        validator_mock.assert_called_once_with(
            project_id=full_project.id,
            user_id=project_owner.id,
        )
        get_from_database_mock.assert_called_once()

    async def test_get_by_id_project_not_exists(
        self,
        project_owner: User,
        full_project: Project,
        mocker: MockerFixture,
        minio_client: MinioClient,
        project_service: ProjectService,
    ) -> None:
        get_project_by_id_mock = mocker.patch.object(
            project_service.project_access_validator.project_repository,
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

        get_project_by_id_mock.assert_called_once_with(project_id=full_project.id)

    async def test_get_private_project_by_id_not_by_owner(
        self,
        project_owner: User,
        full_project: Project,
        mocker: MockerFixture,
        minio_client: MinioClient,
        project_service: ProjectService,
    ) -> None:
        full_project.visibility = ProjectVisibility.private
        get_project_by_id_mock = mocker.patch.object(
            project_service.project_access_validator.project_repository,
            "get_by_id",
            return_value=full_project,
            autospec=True,
        )
        get_project_owner_mock = mocker.patch.object(
            project_service.project_access_validator.project_repository,
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

        get_project_by_id_mock.assert_called_once_with(project_id=full_project.id)
        get_project_owner_mock.assert_called_once_with(project_id=full_project.id)

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
        get_file_by_id_mock = mocker.patch.object(
            project_service.file_repository,
            "get_by_id",
            return_value=source_file,
            autospec=True,
        )
        create_render_mock = mocker.patch.object(
            project_service.render_repository,
            "create_render",
            return_value=render,
            autospec=True,
        )
        create_project_mock = mocker.patch.object(
            project_service.project_repository,
            "create_project",
            return_value=full_project,
            autospec=True,
        )
        create_event_mock = mocker.patch.object(
            project_service.outbox_repository,
            "create_event",
            return_value=None,
            autospec=True,
        )
        await project_service.create_project(
            user_id=project_owner.id,
            create_project=create_project_request,
        )

        get_file_by_id_mock.assert_called_once_with(
            file_id=create_project_request.project.source_file_id,
        )
        create_render_mock.assert_called_once()
        create_project_mock.assert_called_once()
        create_event_mock.assert_called_once()

    async def test_create_project_file_not_exists(
        self,
        create_project_request: ProjectWithRenderCreate,
        project_owner: User,
        mocker: MockerFixture,
        project_service: ProjectService,
    ) -> None:
        get_file_by_id_mock = mocker.patch.object(
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

        get_file_by_id_mock.assert_called_once_with(
            file_id=create_project_request.project.source_file_id,
        )

    async def test_partial_update_project_valid(
        self,
        project_owner: User,
        full_project: Project,
        mocker: MockerFixture,
        project_service: ProjectService,
    ) -> None:
        get_project_by_id_mock = mocker.patch.object(
            project_service.project_access_validator.project_repository,
            "get_by_id",
            return_value=full_project,
            autospec=True,
        )
        get_project_owner_mock = mocker.patch.object(
            project_service.project_access_validator.project_repository,
            "get_project_owner",
            return_value=project_owner,
            autospec=True,
        )
        partial_update_project_mock = mocker.patch.object(
            project_service.project_repository,
            "partial_update_project",
            return_value=full_project,
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

        get_project_by_id_mock.assert_called_once_with(project_id=full_project.id)
        get_project_owner_mock.assert_called_once_with(project_id=full_project.id)
        partial_update_project_mock.assert_called_once_with(
            project_id=full_project.id,
            partial_update_project_data=partial_update_project_data,
        )

    async def test_partial_update_project_not_exists(
        self,
        project_owner: User,
        full_project: Project,
        mocker: MockerFixture,
        project_service: ProjectService,
    ) -> None:
        get_project_by_id_mock = mocker.patch.object(
            project_service.project_access_validator.project_repository,
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

        get_project_by_id_mock.assert_called_once_with(full_project.id)

    async def test_partial_update_project_not_by_owner(
        self,
        project_owner: User,
        full_project: Project,
        mocker: MockerFixture,
        project_service: ProjectService,
    ) -> None:
        get_project_by_id_mock = mocker.patch.object(
            project_service.project_access_validator.project_repository,
            "get_by_id",
            return_value=full_project,
            autospec=True,
        )
        get_project_owner_mock = mocker.patch.object(
            project_service.project_access_validator.project_repository,
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

        get_project_by_id_mock.assert_called_once_with(project_id=full_project.id)
        get_project_owner_mock.assert_called_once_with(project_id=full_project.id)

    async def test_delete_by_id_valid(
        self,
        project_owner: User,
        full_project: Project,
        mocker: MockerFixture,
        project_service: ProjectService,
    ) -> None:
        get_project_by_id_mock = mocker.patch.object(
            project_service.project_access_validator.project_repository,
            "get_by_id",
            return_value=full_project,
        )
        get_project_owner_mock = mocker.patch.object(
            project_service.project_access_validator.project_repository,
            "get_project_owner",
            return_value=project_owner,
        )
        delete_project_by_id_mock = mocker.patch.object(
            project_service.project_repository,
            "delete_by_id",
            return_value=None,
        )
        await project_service.delete_by_id(full_project.id, project_owner.id)
        get_project_by_id_mock.assert_called_once_with(full_project.id)
        get_project_owner_mock.assert_called_once_with(full_project.id)
        delete_project_by_id_mock.assert_called_once_with(full_project.id)

    async def test_delete_by_id_project_not_exists(
        self,
        project_owner: User,
        full_project: Project,
        mocker: MockerFixture,
        project_service: ProjectService,
    ) -> None:
        get_project_by_id_mock = mocker.patch.object(
            project_service.project_access_validator.project_repository,
            "get_by_id",
            return_value=None,
        )
        with pytest.raises(ProjectIdNotFoundError):
            await project_service.delete_by_id(full_project.id, project_owner.id)

        get_project_by_id_mock.assert_called_once_with(full_project.id)

    async def test_delete_by_id_not_by_owner(
        self,
        project_owner: User,
        full_project: Project,
        mocker: MockerFixture,
        project_service: ProjectService,
    ) -> None:
        get_project_by_id_mock = mocker.patch.object(
            project_service.project_access_validator.project_repository,
            "get_by_id",
            return_value=full_project,
        )
        get_project_owner_mock = mocker.patch.object(
            project_service.project_access_validator.project_repository,
            "get_project_owner",
            return_value=project_owner,
        )
        with pytest.raises(PermissionDeniedError):
            await project_service.delete_by_id(full_project.id, project_owner.id + 1)

        get_project_by_id_mock.assert_called_once_with(full_project.id)
        get_project_owner_mock.assert_called_once_with(full_project.id)
