import pytest
from core.exceptions.user import UserIdNotFoundError
from infrastructure.database.models import Project, User
from pytest_mock import MockerFixture
from services.projects.project_pagination import ProjectPaginationService


class TestProjectPaginationService:
    async def test_get_user_projects_valid(
        self,
        project_owner: User,
        full_project: Project,
        mocker: MockerFixture,
        project_pagination_service: ProjectPaginationService,
    ) -> None:
        mocker.patch.object(
            project_pagination_service.user_repository,
            "get_by_id",
            return_value=project_owner,
        )
        mocker.patch.object(
            project_pagination_service.project_repository,
            "get_user_projects",
            return_value=[full_project],
            autospec=True,
        )
        await project_pagination_service.get_user_projects(
            project_owner.id,
            size=10,
            page=1,
        )

    async def test_get_user_projects_user_not_exists(
        self,
        project_owner: User,
        mocker: MockerFixture,
        project_pagination_service: ProjectPaginationService,
    ) -> None:
        mocker.patch.object(
            project_pagination_service.user_repository,
            "get_by_id",
            return_value=None,
            autospec=True,
        )
        with pytest.raises(UserIdNotFoundError):
            await project_pagination_service.get_user_projects(
                project_owner.id,
                size=10,
                page=1,
            )

    async def test_get_public_projects_valid(
        self,
        full_project: Project,
        mocker: MockerFixture,
        project_pagination_service: ProjectPaginationService,
    ) -> None:
        mocker.patch.object(
            project_pagination_service.project_repository,
            "get_public_projects",
            return_value=[full_project],
            autospec=True,
        )
        await project_pagination_service.get_public_projects(
            size=10,
            page=1,
        )

    async def test_get_user_public_projects_valid(
        self,
        project_owner: User,
        mocker: MockerFixture,
        project_pagination_service: ProjectPaginationService,
    ) -> None:
        mocker.patch.object(
            project_pagination_service.user_repository,
            "get_by_id",
            return_value=project_owner,
        )
        await project_pagination_service.get_user_public_projects(
            user_id=project_owner.id,
            size=10,
            page=1,
        )

    async def test_get_user_public_projects_user_not_exists(
        self,
        project_owner: User,
        mocker: MockerFixture,
        project_pagination_service: ProjectPaginationService,
    ) -> None:
        mocker.patch.object(
            project_pagination_service.user_repository,
            "get_by_id",
            return_value=None,
        )
        with pytest.raises(UserIdNotFoundError):
            await project_pagination_service.get_user_public_projects(
                user_id=project_owner.id,
                size=10,
                page=1,
            )
