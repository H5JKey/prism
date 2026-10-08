from collections.abc import Generator
from unittest.mock import AsyncMock

import pytest
from application_factory import create_app
from core.constants import BEARER_TOKEN_TYPE
from dependencies.auth import get_auth_user_by_access_token
from fastapi import FastAPI
from fastapi.testclient import TestClient
from schemas.file import FileResponse
from schemas.token import TokenInfo
from services.auth import AuthService
from services.file_uploader import FileUploader


@pytest.fixture(scope="session")
def application() -> FastAPI:
    application = create_app()
    return application


@pytest.fixture(scope="session")
def client(application: FastAPI) -> TestClient:
    return TestClient(application)


@pytest.fixture(scope="function")
def auth_client(application: FastAPI) -> Generator[TestClient]:
    application.dependency_overrides[get_auth_user_by_access_token] = lambda: 1
    yield TestClient(application)
    application.dependency_overrides.pop(get_auth_user_by_access_token)


@pytest.fixture(scope="session")
def file_uploader() -> FileUploader:
    file_uploader = AsyncMock()
    file_response = FileResponse(
        id=1,
        name="test_name",
        size=1000,
    )
    file_uploader.upload = AsyncMock(
        return_value=file_response,
    )
    return file_uploader


@pytest.fixture(scope="session")
def auth_service() -> AuthService:
    auth_service = AsyncMock()
    register_token = TokenInfo(
        access_token="access_token",
        refresh_token="refresh_token",
        token_type=BEARER_TOKEN_TYPE,
    )
    login_token = TokenInfo(
        access_token="login_access_token",
        refresh_token="login_refresh_token",
        token_type=BEARER_TOKEN_TYPE,
    )
    refresh_access_token_response = TokenInfo(
        access_token="access_token",
        token_type=BEARER_TOKEN_TYPE,
    )

    auth_service.register = AsyncMock(
        return_value=register_token,
    )
    auth_service.authenticate_user = AsyncMock(
        return_value=login_token,
    )
    auth_service.refresh_access_token = AsyncMock(
        return_value=refresh_access_token_response,
    )
    return auth_service
