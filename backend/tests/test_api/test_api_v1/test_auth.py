import pytest
from core.exceptions.auth import InvalidPasswordError
from core.exceptions.base import ConflictError
from core.exceptions.user import (
    UserEmailAlreadyExistsError,
    UserIdNotFoundError,
    UserUsernameAlreadyExistsError,
    UserUsernameNotFoundError,
)
from dependencies.auth import get_auth_user_by_refresh_token, get_login_request
from dependencies.services import get_auth_service
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from schemas.auth import LoginRequest, RegisterRequest
from services.auth import AuthService

from tests.test_api.utils import get_result_json


@pytest.fixture(scope="function")
def register_request() -> RegisterRequest:
    register_request = RegisterRequest(
        surname="surname",
        name="name",
        username="username",
        email="email@email.com",
        password="password",
    )
    return register_request


@pytest.fixture(scope="function")
def login_request() -> LoginRequest:
    login_request = LoginRequest(
        username="username",
        password="password",
    )
    return login_request


class TestRegisterEndpoint:
    url = "/api/v1/auth/register"

    def test_register_valid(
        self,
        register_request: RegisterRequest,
        application: FastAPI,
        client: TestClient,
        auth_service: AuthService,
    ) -> None:
        application.dependency_overrides[get_auth_service] = lambda: auth_service
        response = client.post(
            self.url,
            json=register_request.model_dump(),
        )
        response_data = response.json()
        assert response.status_code == status.HTTP_201_CREATED
        assert response_data == get_result_json(auth_service, "register")

    @pytest.mark.parametrize(
        "conflict_error",
        [
            UserUsernameAlreadyExistsError("existed_username"),
            UserEmailAlreadyExistsError("existed_email@email.com"),
        ],
    )
    def test_register_conflict_error(
        self,
        register_request: RegisterRequest,
        conflict_error: ConflictError,
        application: FastAPI,
        client: TestClient,
        auth_service: AuthService,
    ) -> None:
        auth_service.register.side_effect = conflict_error
        application.dependency_overrides[get_auth_service] = lambda: auth_service
        response = client.post(
            self.url,
            json=register_request.model_dump(),
        )
        response_data = response.json()
        assert response.status_code == status.HTTP_409_CONFLICT
        assert response_data["message"] == conflict_error.detail


class TestLoginEndpoint:
    url = "/api/v1/auth/login"

    def test_login_valid(
        self,
        login_request: LoginRequest,
        application: FastAPI,
        client: TestClient,
        auth_service: AuthService,
    ) -> None:
        application.dependency_overrides[get_auth_service] = lambda: auth_service
        application.dependency_overrides[get_login_request] = lambda: login_request
        response = client.post(self.url)
        response_data = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert response_data == get_result_json(auth_service, "authenticate_user")

    def test_login_username_not_found(
        self,
        login_request: LoginRequest,
        application: FastAPI,
        client: TestClient,
        auth_service: AuthService,
    ) -> None:
        application.dependency_overrides[get_auth_service] = lambda: auth_service
        application.dependency_overrides[get_login_request] = lambda: login_request
        username_not_found_error = UserUsernameNotFoundError(login_request.username)
        auth_service.authenticate_user.side_effect = username_not_found_error
        response = client.post(self.url)
        response_data = response.json()
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response_data["message"] == username_not_found_error.detail

    def test_login_invalid_password(
        self,
        login_request: LoginRequest,
        application: FastAPI,
        client: TestClient,
        auth_service: AuthService,
    ) -> None:
        application.dependency_overrides[get_auth_service] = lambda: auth_service
        application.dependency_overrides[get_login_request] = lambda: login_request
        invalid_password_error = InvalidPasswordError(login_request.password)
        auth_service.authenticate_user.side_effect = invalid_password_error
        response = client.post(self.url)
        response_data = response.json()
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response_data["message"] == invalid_password_error.detail


class TestRefreshAccessTokenEndpoint:
    url = "/api/v1/auth/refresh"

    def test_refresh_access_token_valid(
        self,
        application: FastAPI,
        client: TestClient,
        auth_service: AuthService,
    ) -> None:
        application.dependency_overrides[get_auth_service] = lambda: auth_service
        application.dependency_overrides[get_auth_user_by_refresh_token] = lambda: 1
        response = client.get(self.url)
        response_data = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert response_data == get_result_json(
            auth_service,
            "refresh_access_token",
            exclude_unset=True,
        )

    def test_refresh_access_token_user_not_found(
        self,
        application: FastAPI,
        client: TestClient,
        auth_service: AuthService,
    ) -> None:
        user_id = 1
        application.dependency_overrides[get_auth_service] = lambda: auth_service
        application.dependency_overrides[get_auth_user_by_refresh_token] = (
            lambda: user_id
        )
        user_not_found_error = UserIdNotFoundError(user_id)
        auth_service.refresh_access_token.side_effect = user_not_found_error
        response = client.get(self.url)
        response_data = response.json()
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response_data["message"] == user_not_found_error.detail
