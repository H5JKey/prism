import pytest


@pytest.fixture
def project_base_data() -> dict:
    return {
        "name": "name",
        "description": "description",
        "source_file_id": 1,
    }


@pytest.fixture
def project_create_data(project_base_data: dict) -> dict:
    return {
        **project_base_data,
        "visibility": "public",
    }


@pytest.fixture
def project_with_render_create_data(
    render_create_payload_data: dict,
    project_create_data: dict,
) -> dict:
    return {
        "render": render_create_payload_data,
        "project": project_create_data,
    }


@pytest.fixture
def project_partial_update_data() -> dict:
    return {
        "name": "name",
        "description": "description",
        "visibility": "public",
    }


@pytest.fixture
def project_response_data() -> dict:
    return {
        "visibility": "public",
        "status": "rendering",
        "user_id": 1,
        "render_id": 1,
        "id": 1,
    }


@pytest.fixture
def project_full_response_data(project_response_data: dict) -> dict:
    return {
        **project_response_data,
        "url": "http://example.com",
    }


@pytest.fixture
def project_with_render_file_full_response_data(
    project_full_response_data: dict,
    render_with_file_full_response: dict,
) -> dict:
    return {
        **project_full_response_data,
        "render": render_with_file_full_response,
    }


@pytest.fixture
def project_with_render_response_data(
    project_response_data: dict,
    render_response_data: dict,
) -> dict:
    return {
        **project_response_data,
        "render": render_response_data,
    }


@pytest.fixture
def project_with_render_file_response_data(
    project_response_data: dict,
    render_with_file_response_data: dict,
) -> dict:
    return {
        **project_response_data,
        "render": render_with_file_response_data,
    }


@pytest.fixture
def project_response_list_data() -> dict:
    return {
        "project_list": [
            {
                "visibility": "public",
                "status": "rendering",
                "user_id": 1,
                "render_id": 1,
                "id": 1,
            },
            {
                "visibility": "private",
                "status": "rendering",
                "user_id": 2,
                "render_id": 2,
                "id": 2,
            },
        ],
        "size": 1,
        "page": 1,
    }


@pytest.fixture
def project_with_render_file_response_list_data() -> dict:
    return {
        "visibility": "public",
        "status": "rendering",
        "user_id": 1,
        "render_id": 1,
        "id": 1,
        "render": {
            "width": 1000,
            "height": 1000,
            "samples": 150,
            "denoiser": True,
            "gpu": False,
            "id": 1,
            "file_id": 1,
            "file": {
                "name": "file_name",
                "size": 1000,
                "id": 1,
            },
        },
    }
