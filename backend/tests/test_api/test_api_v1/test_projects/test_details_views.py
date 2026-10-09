import pytest
from core.exceptions.auth import PermissionDeniedError
from core.exceptions.base import NotFoundError
from core.exceptions.file import FileIdNotFoundError
from core.exceptions.project import ProjectIdNotFoundError
from core.exceptions.user import UserIdNotFoundError
from dependencies.services import get_project_service
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from schemas.project import ProjectPartialUpdate
from services.projects.project import ProjectService

from tests.test_api.utils import get_result_json


@pytest.fixture(scope="function")
def partial_update_project_data() -> ProjectPartialUpdate:
    return ProjectPartialUpdate(
        name="project_name",
        description="description",
    )


class TestGetProjectEndpoint:
    url = "/api/v1/projects/{project_id}"

    def test_get_project_valid(
        self,
        application: FastAPI,
        auth_client: TestClient,
        project_service: ProjectService,
    ) -> None:
        application.dependency_overrides[get_project_service] = lambda: project_service
        url = self.url.format(project_id=1)
        response = auth_client.get(url)
        response_data = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert response_data == get_result_json(project_service, "get_by_id")

    @pytest.mark.parametrize(
        "not_found_error",
        [
            ProjectIdNotFoundError(1),
            UserIdNotFoundError(1),
        ],
    )
    def test_get_project_not_found_error(
        self,
        application: FastAPI,
        auth_client: TestClient,
        project_service: ProjectService,
        not_found_error: NotFoundError,
    ) -> None:
        application.dependency_overrides[get_project_service] = lambda: project_service
        project_service.get_by_id.side_effect = not_found_error
        url = self.url.format(project_id=1)
        response = auth_client.get(url)
        response_data = response.json()
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response_data["message"] == not_found_error.detail

    def test_get_project_permission_denied_error(
        self,
        application: FastAPI,
        auth_client: TestClient,
        project_service: ProjectService,
    ) -> None:
        application.dependency_overrides[get_project_service] = lambda: project_service
        permission_denied_error = PermissionDeniedError()
        project_service.get_by_id.side_effect = permission_denied_error
        url = self.url.format(project_id=1)
        response = auth_client.get(url)
        response_data = response.json()
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response_data["message"] == permission_denied_error.detail


class TestPartialUpdateProjectEndpoint:
    url = "/api/v1/projects/{project_id}"

    def test_partial_update_project_valid(
        self,
        application: FastAPI,
        auth_client: TestClient,
        project_service: ProjectService,
        partial_update_project_data: ProjectPartialUpdate,
    ) -> None:
        application.dependency_overrides[get_project_service] = lambda: project_service
        url = self.url.format(project_id=1)
        response = auth_client.patch(url, json=partial_update_project_data.model_dump())
        response_data = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert response_data == get_result_json(
            project_service,
            "partial_update_project",
        )

    def test_partial_update_project_file_not_found_error(
        self,
        application: FastAPI,
        auth_client: TestClient,
        project_service: ProjectService,
        partial_update_project_data: ProjectPartialUpdate,
    ) -> None:
        file_not_found_error = FileIdNotFoundError(1)
        application.dependency_overrides[get_project_service] = lambda: project_service
        project_service.partial_update_project.side_effect = file_not_found_error
        url = self.url.format(project_id=1)
        response = auth_client.patch(url, json=partial_update_project_data.model_dump())
        response_data = response.json()
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response_data["message"] == file_not_found_error.detail


class TestDeleteProjectEndpoint:
    url = "/api/v1/projects/{project_id}"

    def test_delete_project_valid(
        self,
        application: FastAPI,
        auth_client: TestClient,
        project_service: ProjectService,
    ) -> None:
        application.dependency_overrides[get_project_service] = lambda: project_service
        url = self.url.format(project_id=1)
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.parametrize(
        "not_found_error",
        [
            ProjectIdNotFoundError(1),
            UserIdNotFoundError(1),
        ],
    )
    def test_delete_project_not_found_error(
        self,
        application: FastAPI,
        auth_client: TestClient,
        project_service: ProjectService,
        not_found_error: NotFoundError,
    ) -> None:
        application.dependency_overrides[get_project_service] = lambda: project_service
        project_service.delete_by_id.side_effect = not_found_error
        url = self.url.format(project_id=1)
        response = auth_client.delete(url)
        response_data = response.json()
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response_data["message"] == not_found_error.detail

    def test_delete_project_permission_denied_error(
        self,
        application: FastAPI,
        auth_client: TestClient,
        project_service: ProjectService,
    ) -> None:
        application.dependency_overrides[get_project_service] = lambda: project_service
        permission_denied_error = PermissionDeniedError()
        project_service.delete_by_id.side_effect = permission_denied_error
        url = self.url.format(project_id=1)
        response = auth_client.delete(url)
        response_data = response.json()
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response_data["message"] == permission_denied_error.detail
