import pytest


@pytest.fixture
def event_create_data() -> dict:
    return {
        "topic": "generate_render",
        "message": {
            "field1": "value1",
            "field2": "value2",
            "field3": "value3",
            "field4": "value4",
        },
    }


@pytest.fixture
def file_location_data() -> dict:
    return {
        "bucket": "test_bucket",
        "key": "test_key",
    }


@pytest.fixture
def render_data() -> dict:
    return {
        "width": 200,
        "height": 200,
        "samples": 10,
        "denoiser": True,
        "gpu": False,
        "background": [0, 0, 0],
        "sun": {
            "direction": [0, 0, 0],
            "color": [0, 0, 0],
            "exponent": 2,
        },
    }


@pytest.fixture
def create_project_event_data(file_location_data: dict, render_data: dict) -> dict:
    return {
        "project_id": 1,
        "input": file_location_data,
        "output": file_location_data,
        "render": render_data,
    }


@pytest.fixture
def render_generated_event_data(
    file_location_data,
) -> dict:
    return {
        "project_id": 1,
        "output": file_location_data,
    }


@pytest.fixture
def dlq_message_data() -> dict:
    return {
        "error": "test error description",
        "message": {
            "field1": "value1",
            "field2": "value2",
            "field3": 0,
            "field4": True,
        },
    }


@pytest.fixture
def file_base_data() -> dict:
    return {
        "name": "file_name",
        "size": 1000,
    }


@pytest.fixture
def file_create_data(file_base_data: dict, file_location_data: dict) -> dict:
    data = {**file_base_data, **file_location_data}
    return data


@pytest.fixture
def file_response_data(file_base_data: dict) -> dict:
    file_base_data["id"] = 1
    return file_base_data


@pytest.fixture
def sun_info_data() -> dict:
    return {
        "direction": [1.0, 1.0, 1.0],
        "color": [2.0, 2.0, 2.0],
        "exponent": 5,
    }


@pytest.fixture
def render_base_data() -> dict:
    return {
        "width": 1000,
        "height": 1000,
        "samples": 150,
        "denoiser": True,
        "gpu": False,
    }


@pytest.fixture
def render_create_data(render_base_data: dict) -> dict:
    return {
        **render_base_data,
    }


@pytest.fixture
def render_create_payload_data(render_create_data: dict, sun_info_data: dict) -> dict:
    return {
        **render_create_data,
        "background": [1.0, 1.0, 1.0],
        "sun": sun_info_data,
    }


@pytest.fixture
def render_response_data(render_base_data: dict) -> dict:
    return {
        **render_base_data,
        "id": 1,
        "file_id": 1,
    }


@pytest.fixture
def render_full_response_data(render_response_data: dict) -> dict:
    return {
        **render_response_data,
        "url": "http://example.com",
    }


@pytest.fixture
def render_with_file_response_data(
    render_response_data: dict, file_response_data: dict
) -> dict:
    return {
        **render_response_data,
        "file": file_response_data,
    }


@pytest.fixture
def render_with_file_full_response_data(
    render_full_response_data: dict,
    file_response_data: dict,
) -> dict:
    return {
        **render_full_response_data,
        "file": file_response_data,
    }
