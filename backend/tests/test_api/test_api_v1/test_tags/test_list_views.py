import pytest
from core.exceptions.auth import PermissionDeniedError
from core.exceptions.base import NotFoundError
from core.exceptions.project import ProjectIdNotFoundError
from core.exceptions.user import UserIdNotFoundError
from dependencies.services import get_tag_service
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from schemas.tag import TagCreate
from services.tag import TagService


@pytest.fixture(scope="function")
def create_tag_data() -> TagCreate:
    return TagCreate(
        name="tag_name",
        project_id=1,
    )


class TestCreateTagEndpoint:
    url = "/api/v1/tags/create"

    def test_create_tag_valid(
        self,
        application: FastAPI,
        auth_client: TestClient,
        tag_service: TagService,
        create_tag_data: TagCreate,
    ) -> None:
        application.dependency_overrides[get_tag_service] = lambda: tag_service
        response = auth_client.post(self.url, json=create_tag_data.model_dump())
        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.parametrize(
        "not_found_error",
        [
            ProjectIdNotFoundError(1),
            UserIdNotFoundError(1),
        ],
    )
    def test_create_tag_not_found_error(
        self,
        application: FastAPI,
        auth_client: TestClient,
        tag_service: TagService,
        not_found_error: NotFoundError,
        create_tag_data: TagCreate,
    ) -> None:
        application.dependency_overrides[get_tag_service] = lambda: tag_service
        tag_service.create_tag.side_effect = not_found_error
        response = auth_client.post(self.url, json=create_tag_data.model_dump())
        response_data = response.json()
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response_data["message"] == not_found_error.detail

    def test_create_tag_permission_denied_error(
        self,
        application: FastAPI,
        auth_client: TestClient,
        tag_service: TagService,
        create_tag_data: TagCreate,
    ) -> None:
        application.dependency_overrides[get_tag_service] = lambda: tag_service
        tag_service.create_tag.side_effect = PermissionDeniedError
        response = auth_client.post(self.url, json=create_tag_data.model_dump())
        response_data = response.json()
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response_data["message"] == PermissionDeniedError().detail
