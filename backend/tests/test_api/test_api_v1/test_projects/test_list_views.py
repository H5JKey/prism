import pytest
from core.constants import ProjectVisibility
from core.exceptions.file import FileIdNotFoundError
from core.exceptions.user import UserIdNotFoundError
from dependencies.services import get_project_pagination_service, get_project_service
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from schemas.project import (
    ProjectBase,
    ProjectCreate,
    ProjectWithRenderCreate,
)
from schemas.render import RenderBase, RenderCreatePayload, SunInfo
from services.projects.project import ProjectService
from services.projects.project_pagination import ProjectPaginationService

from tests.test_api.utils import get_result_json


@pytest.fixture(scope="function")
def sun() -> SunInfo:
    return SunInfo(
        direction=[1.0, 1.0, 1.0],
        color=[1.0, 1.0, 1.0],
        exponent=1,
    )


@pytest.fixture(scope="function")
def render_create_payload(render_base: RenderBase, sun: SunInfo) -> RenderCreatePayload:
    return RenderCreatePayload(
        background=[1.0, 1.0, 1.0],
        sun=sun,
        **render_base.model_dump(),
    )


@pytest.fixture(scope="function")
def project_create_payload(project_base: ProjectBase) -> ProjectCreate:
    return ProjectCreate(
        visibility=ProjectVisibility.public,
        **project_base.model_dump(),
    )


@pytest.fixture(scope="function")
def create_project_data(
    render_create_payload: RenderCreatePayload,
    project_create_payload: ProjectCreate,
) -> ProjectWithRenderCreate:
    return ProjectWithRenderCreate(
        render=render_create_payload,
        project=project_create_payload,
    )


class TestCreateProjectEndpoint:
    url = "/api/v1/projects/create"

    def test_create_project_valid(
        self,
        application: FastAPI,
        auth_client: TestClient,
        project_service: ProjectService,
        create_project_data: ProjectWithRenderCreate,
    ) -> None:
        application.dependency_overrides[get_project_service] = lambda: project_service
        response = auth_client.post(self.url, json=create_project_data.model_dump())
        response_data = response.json()
        assert response.status_code == status.HTTP_201_CREATED
        assert response_data == get_result_json(
            project_service,
            "create_project",
        )

    def test_create_project_file_not_found_error(
        self,
        application: FastAPI,
        auth_client: TestClient,
        project_service: ProjectService,
        create_project_data: ProjectWithRenderCreate,
    ) -> None:
        application.dependency_overrides[get_project_service] = lambda: project_service
        file_not_found_error = FileIdNotFoundError(1)
        project_service.create_project.side_effect = file_not_found_error
        response = auth_client.post(self.url, json=create_project_data.model_dump())
        response_data = response.json()
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response_data["message"] == file_not_found_error.detail


class TestGetPublicProjects:
    url = "/api/v1/projects/"

    def test_get_public_projects_valid(
        self,
        application: FastAPI,
        auth_client: TestClient,
        project_pagination_service: ProjectPaginationService,
    ) -> None:
        application.dependency_overrides[get_project_pagination_service] = (
            lambda: project_pagination_service
        )
        response = auth_client.get(self.url)
        response_data = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert response_data == get_result_json(
            project_pagination_service,
            "get_public_projects",
        )


class TestGetCurrentUserProjects:
    url = "/api/v1/projects/about-me"

    def test_get_current_user_projects_valid(
        self,
        application: FastAPI,
        auth_client: TestClient,
        project_pagination_service: ProjectPaginationService,
    ) -> None:
        application.dependency_overrides[get_project_pagination_service] = (
            lambda: project_pagination_service
        )
        response = auth_client.get(self.url)
        response_data = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert response_data == get_result_json(
            project_pagination_service,
            "get_user_projects",
        )

    def test_get_current_user_projects_user_not_found_error(
        self,
        application: FastAPI,
        auth_client: TestClient,
        project_pagination_service: ProjectPaginationService,
    ) -> None:
        application.dependency_overrides[get_project_pagination_service] = (
            lambda: project_pagination_service
        )
        user_not_found_error = UserIdNotFoundError(1)
        project_pagination_service.get_user_projects.side_effect = user_not_found_error
        response = auth_client.get(self.url)
        response_data = response.json()
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response_data["message"] == user_not_found_error.detail


class TestGetUserPublicProjects:
    url = "/api/v1/projects/user/{user_id}"

    def test_get_user_public_projects_valid(
        self,
        application: FastAPI,
        auth_client: TestClient,
        project_pagination_service: ProjectPaginationService,
    ) -> None:
        application.dependency_overrides[get_project_pagination_service] = (
            lambda: project_pagination_service
        )
        url = self.url.format(user_id=1)
        response = auth_client.get(url)
        response_data = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert response_data == get_result_json(
            project_pagination_service,
            "get_user_public_projects",
        )

    def test_get_user_public_projects_user_not_found_error(
        self,
        application: FastAPI,
        auth_client: TestClient,
        project_pagination_service: ProjectPaginationService,
    ) -> None:
        application.dependency_overrides[get_project_pagination_service] = (
            lambda: project_pagination_service
        )
        user_not_found_error = UserIdNotFoundError(1)
        project_pagination_service.get_user_public_projects.side_effect = (
            user_not_found_error
        )
        url = self.url.format(user_id=1)
        response = auth_client.get(url)
        response_data = response.json()
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response_data["message"] == user_not_found_error.detail
