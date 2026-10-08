from collections.abc import Generator
from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from application_factory import create_app
from core.constants import BEARER_TOKEN_TYPE
from dependencies.auth import get_auth_user_by_access_token
from fastapi import FastAPI
from fastapi.testclient import TestClient
from schemas.file import FileResponse
from schemas.tag import TagResponse, TagResponseList
from schemas.token import TokenInfo
from schemas.user import UserFullResponse, UserResponse
from services.auth import AuthService
from services.file_uploader import FileUploader
from services.tag import TagService
from services.user import UserService


@pytest.fixture(scope="session")
def application() -> FastAPI:
    application = create_app()
    return application


@pytest.fixture(scope="session")
def client(application: FastAPI) -> TestClient:
    return TestClient(application)


@pytest.fixture(scope="function")
def auth_client(application: FastAPI) -> Generator[TestClient]:
    user_id = 1
    application.dependency_overrides[get_auth_user_by_access_token] = lambda: user_id
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


@pytest.fixture(scope="session")
def user_service() -> UserService:
    user_service = AsyncMock()
    user_full_response = UserFullResponse(
        id=1,
        registration_date=datetime(
            year=2025,
            month=1,
            day=1,
            hour=0,
            minute=0,
            second=0,
        ),
        surname="surname",
        name="name",
        username="username",
        email="email@email.com",
    )
    user_response = UserResponse(
        id=1,
        registration_date=datetime(
            year=2025,
            month=1,
            day=1,
            hour=0,
            minute=0,
            second=0,
        ),
        surname="surname",
        name="name",
        username="username",
    )
    user_service.get_profile_by_id = AsyncMock(return_value=user_full_response)
    user_service.update_user = AsyncMock(return_value=user_response)
    user_service.delete_by_id = AsyncMock(return_value=None)
    user_service.get_by_id = AsyncMock(return_value=user_response)
    return user_service


@pytest.fixture(scope="function")
def tag_service() -> TagService:
    tag_service = AsyncMock()
    tag_response = TagResponse(
        id=1,
        project_id=1,
        name="tag_name",
    )
    tag_response_list = TagResponseList(tag_list=[tag_response])
    tag_service.create_tag = AsyncMock(return_value=tag_response)
    tag_service.delete_by_id = AsyncMock(return_value=None)
    tag_service.get_project_tags = AsyncMock(return_value=tag_response_list)
    return tag_service
