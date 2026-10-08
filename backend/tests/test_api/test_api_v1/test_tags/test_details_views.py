import pytest
from core.exceptions.auth import PermissionDeniedError
from core.exceptions.base import NotFoundError
from core.exceptions.project import ProjectIdNotFoundError
from core.exceptions.tag import TagIdNotFoundError
from core.exceptions.user import UserIdNotFoundError
from dependencies.services import get_tag_service
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from services.tag import TagService

from tests.test_api.utils import get_result_json


class TestGetProjectTagsEndpoint:
    url = "/api/v1/tags/project/{project_id}"

    def test_get_project_tags_valid(
        self,
        application: FastAPI,
        auth_client: TestClient,
        tag_service: TagService,
    ) -> None:
        application.dependency_overrides[get_tag_service] = lambda: tag_service
        url = self.url.format(project_id=1)
        response = auth_client.get(url)
        response_data = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert response_data == get_result_json(tag_service, "get_project_tags")

    @pytest.mark.parametrize(
        "not_found_error",
        [
            ProjectIdNotFoundError(1),
            UserIdNotFoundError(1),
        ],
    )
    def test_get_project_tags_not_found_error(
        self,
        application: FastAPI,
        auth_client: TestClient,
        tag_service: TagService,
        not_found_error: NotFoundError,
    ) -> None:
        application.dependency_overrides[get_tag_service] = lambda: tag_service
        tag_service.get_project_tags.side_effect = not_found_error
        url = self.url.format(project_id=1)
        response = auth_client.get(url)
        response_data = response.json()
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response_data["message"] == not_found_error.detail

    def test_get_project_tags_permission_denied_error(
        self,
        application: FastAPI,
        auth_client: TestClient,
        tag_service: TagService,
    ) -> None:
        application.dependency_overrides[get_tag_service] = lambda: tag_service
        tag_service.get_project_tags.side_effect = PermissionDeniedError
        url = self.url.format(project_id=1)
        response = auth_client.get(url)
        response_data = response.json()
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response_data["message"] == PermissionDeniedError().detail


class TestDeleteProjectTagEndpoint:
    url = "/api/v1/tags/{tag_id}"

    def test_delete_project_tag_valid(
        self,
        application: FastAPI,
        auth_client: TestClient,
        tag_service: TagService,
    ) -> None:
        application.dependency_overrides[get_tag_service] = lambda: tag_service
        url = self.url.format(tag_id=1)
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.parametrize(
        "not_found_error",
        [
            TagIdNotFoundError(1),
            UserIdNotFoundError(1),
        ],
    )
    def test_delete_project_tag_not_found_error(
        self,
        application: FastAPI,
        auth_client: TestClient,
        tag_service: TagService,
        not_found_error: NotFoundError,
    ) -> None:
        application.dependency_overrides[get_tag_service] = lambda: tag_service
        tag_service.delete_by_id.side_effect = not_found_error
        url = self.url.format(tag_id=1)
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_project_tag_permission_denied_error(
        self,
        application: FastAPI,
        auth_client: TestClient,
        tag_service: TagService,
    ) -> None:
        application.dependency_overrides[get_tag_service] = lambda: tag_service
        tag_service.delete_by_id.side_effect = PermissionDeniedError
        url = self.url.format(tag_id=1)
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
