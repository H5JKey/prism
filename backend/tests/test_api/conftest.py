from collections.abc import Generator
from unittest.mock import AsyncMock

import pytest
from application_factory import create_app
from dependencies.auth import get_auth_user_by_access_token
from fastapi import FastAPI
from fastapi.testclient import TestClient
from schemas.file import FileResponse
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
