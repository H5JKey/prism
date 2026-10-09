from collections.abc import Generator
from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from application_factory import create_app
from core.constants import BEARER_TOKEN_TYPE, ProjectVisibility, RenderStatus
from dependencies.auth import get_auth_user_by_access_token
from fastapi import FastAPI
from fastapi.testclient import TestClient
from schemas.file import FileResponse
from schemas.project import (
    ProjectBase,
    ProjectFullResponse,
    ProjectResponse,
    ProjectResponseList,
    ProjectWithRenderFileFullResponse,
    ProjectWithRenderFileResponse,
    ProjectWithRenderResponse,
)
from schemas.render import (
    RenderBase,
    RenderFullResponse,
    RenderResponse,
    RenderWithFileFullResponse,
    RenderWithFileResponse,
)
from schemas.tag import TagResponse, TagResponseList
from schemas.token import TokenInfo
from schemas.user import UserFullResponse, UserResponse
from services.auth import AuthService
from services.file_uploader import FileUploader
from services.projects.project_pagination import ProjectPaginationService
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
def render_base() -> RenderBase:
    return RenderBase(
        width=1000,
        height=1000,
        samples=100,
        denoiser=True,
        gpu=True,
    )


@pytest.fixture(scope="function")
def render_response(render_base: RenderBase) -> RenderResponse:
    return RenderResponse(
        id=1,
        file_id=None,
        **render_base.model_dump(),
    )


@pytest.fixture(scope="function")
def render_full_response(render_response: RenderResponse) -> RenderFullResponse:
    return RenderFullResponse(
        url=None,
        **render_response.model_dump(),
    )


@pytest.fixture(scope="function")
def render_with_file_full_response(
    render_full_response: RenderFullResponse,
) -> RenderWithFileFullResponse:
    return RenderWithFileFullResponse(
        file=None,
        **render_full_response.model_dump(),
    )


@pytest.fixture(scope="function")
def project_base() -> ProjectBase:
    return ProjectBase(
        name="project_name",
        description="description",
        source_file_id=1,
    )


@pytest.fixture(scope="function")
def project_response(
    project_base: ProjectBase,
) -> ProjectResponse:
    return ProjectResponse(
        visibility=ProjectVisibility.public,
        status=RenderStatus.completed,
        user_id=1,
        render_id=None,
        id=1,
        **project_base.model_dump(),
    )


@pytest.fixture(scope="function")
def project_full_response(
    project_response: ProjectResponse,
) -> ProjectFullResponse:
    return ProjectFullResponse(
        url="test_url",
        **project_response.model_dump(),
    )


@pytest.fixture(scope="function")
def project_with_render_file_full_response(
    project_full_response: ProjectFullResponse,
    render_with_file_full_response: RenderWithFileFullResponse,
) -> ProjectWithRenderFileFullResponse:
    return ProjectWithRenderFileFullResponse(
        render=render_with_file_full_response,
        **project_full_response.model_dump(),
    )


@pytest.fixture(scope="function")
def project_with_render_response(
    render_response: RenderResponse,
    project_response: ProjectResponse,
) -> ProjectWithRenderResponse:
    return ProjectWithRenderResponse(
        render=render_response,
        **project_response.model_dump(),
    )


@pytest.fixture(scope="function")
def render_with_file_response(
    render_response: RenderResponse,
) -> RenderWithFileResponse:
    return RenderWithFileResponse(
        file=None,
        **render_response.model_dump(),
    )


@pytest.fixture(scope="function")
def project_with_render_file_response(
    project_response: ProjectResponse,
    render_with_file_response: RenderWithFileResponse,
) -> ProjectWithRenderFileResponse:
    return ProjectWithRenderFileResponse(
        render=render_with_file_response,
        **project_response.model_dump(),
    )


@pytest.fixture(scope="function")
def project_service(
    project_with_render_file_full_response: ProjectWithRenderFileFullResponse,
    project_with_render_response: ProjectWithRenderResponse,
    project_with_render_file_response: ProjectWithRenderFileResponse,
) -> TagService:
    project_service = AsyncMock()
    project_service.get_by_id = AsyncMock(
        return_value=project_with_render_file_full_response,
    )
    project_service.create_project = AsyncMock(
        return_value=project_with_render_response,
    )
    project_service.partial_update_project = AsyncMock(
        return_value=project_with_render_file_response,
    )
    project_service.delete_by_id = AsyncMock(return_value=None)
    return project_service


@pytest.fixture(scope="function")
def project_response_list(project_response: ProjectResponse) -> ProjectResponseList:
    return ProjectResponseList(
        project_list=[project_response],
        size=10,
        page=1,
    )


@pytest.fixture(scope="function")
def project_pagination_service(
    project_response_list: ProjectResponseList,
) -> ProjectPaginationService:
    project_pagination_service = AsyncMock()
    project_pagination_service.get_user_projects = AsyncMock(
        return_value=project_response_list,
    )
    project_pagination_service.get_public_projects = AsyncMock(
        return_value=project_response_list,
    )
    project_pagination_service.get_user_public_projects = AsyncMock(
        return_value=project_response_list,
    )
    return project_pagination_service


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
