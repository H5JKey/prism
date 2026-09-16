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
