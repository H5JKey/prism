from datetime import datetime

import pytest
from core.exceptions.user import UserIdNotFoundError
from dependencies.services import get_user_service
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from schemas.user import UserUpdate
from services.user import UserService

from tests.test_api.utils import get_result_json


@pytest.fixture(scope="function")
def update_user_data() -> UserUpdate:
    return UserUpdate(
        surname="surname",
        name="name",
        username="username",
        email="email@email.com",
    )


class TestGetCurrentUserProfileEndpoint:
    url = "/api/v1/users/about-me"

    def test_get_current_user_profile_valid(
        self,
        application: FastAPI,
        auth_client: TestClient,
        user_service: UserService,
    ) -> None:
        application.dependency_overrides[get_user_service] = lambda: user_service
        response = auth_client.get(self.url)
        response_data = response.json()
        assert response.status_code == status.HTTP_200_OK
        expected_response_data = get_result_json(user_service, "get_profile_by_id")
        response_data["registration_date"] = datetime.fromisoformat(
            response_data["registration_date"],
        )
        assert response_data == expected_response_data

    def test_get_current_user_profile_not_found(
        self,
        application: FastAPI,
        auth_client: TestClient,
        user_service: UserService,
    ) -> None:
        user_not_found_error = UserIdNotFoundError(1)
        application.dependency_overrides[get_user_service] = lambda: user_service
        user_service.get_profile_by_id.side_effect = user_not_found_error
        response = auth_client.get(self.url)
        response_data = response.json()
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response_data["message"] == user_not_found_error.detail


class TestUpdateCurrentUserProfileEndpoint:
    url = "/api/v1/users/about-me"

    def test_update_current_user_profile_valid(
        self,
        application: FastAPI,
        auth_client: TestClient,
        user_service: UserService,
        update_user_data: UserUpdate,
    ) -> None:
        application.dependency_overrides[get_user_service] = lambda: user_service
        response = auth_client.put(self.url, json=update_user_data.model_dump())
        response_data = response.json()
        assert response.status_code == status.HTTP_200_OK
        expected_response_data = get_result_json(user_service, "update_user")
        response_data["registration_date"] = datetime.fromisoformat(
            response_data["registration_date"],
        )
        assert response_data == expected_response_data

    def test_update_current_user_profile_not_found(
        self,
        application: FastAPI,
        auth_client: TestClient,
        user_service: UserService,
        update_user_data: UserUpdate,
    ) -> None:
        user_not_found_error = UserIdNotFoundError(1)
        application.dependency_overrides[get_user_service] = lambda: user_service
        user_service.update_user.side_effect = user_not_found_error
        response = auth_client.put(self.url, json=update_user_data.model_dump())
        response_data = response.json()
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response_data["message"] == user_not_found_error.detail


class TestDeleteCurrentUserProfileEndpoint:
    url = "/api/v1/users/about-me"

    def test_delete_current_user_profile_valid(
        self,
        application: FastAPI,
        auth_client: TestClient,
        user_service: UserService,
    ) -> None:
        application.dependency_overrides[get_user_service] = lambda: user_service
        response = auth_client.delete(self.url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_current_user_profile_not_found(
        self,
        application: FastAPI,
        auth_client: TestClient,
        user_service: UserService,
    ) -> None:
        user_not_found_error = UserIdNotFoundError(1)
        application.dependency_overrides[get_user_service] = lambda: user_service
        user_service.delete_by_id.side_effect = user_not_found_error
        response = auth_client.delete(self.url)
        response_data = response.json()
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response_data["message"] == user_not_found_error.detail


class TestGetUserProfileEndpoint:
    url = "/api/v1/users/{user_id}"

    def test_get_user_profile_valid(
        self,
        application: FastAPI,
        auth_client: TestClient,
        user_service: UserService,
    ) -> None:
        application.dependency_overrides[get_user_service] = lambda: user_service
        url = self.url.format(user_id=1)
        response = auth_client.get(url)
        response_data = response.json()
        assert response.status_code == status.HTTP_200_OK
        expected_response_data = get_result_json(user_service, "get_by_id")
        response_data["registration_date"] = datetime.fromisoformat(
            response_data["registration_date"],
        )
        assert response_data == expected_response_data

    def test_get_user_profile_not_found(
        self,
        application: FastAPI,
        auth_client: TestClient,
        user_service: UserService,
    ) -> None:
        user_not_found_error = UserIdNotFoundError(1)
        application.dependency_overrides[get_user_service] = lambda: user_service
        user_service.get_by_id.side_effect = user_not_found_error
        url = self.url.format(user_id=1)
        response = auth_client.get(url)
        response_data = response.json()
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response_data["message"] == user_not_found_error.detail
