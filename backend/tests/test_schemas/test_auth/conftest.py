import pytest


@pytest.fixture
def login_request_data() -> dict[str, str]:
    return {
        "username": "admin",
        "password": "password",
    }


@pytest.fixture
def register_request_data() -> dict[str, str]:
    return {
        "surname": "Jones",
        "name": "Henry",
        "username": "user_john",
        "email": "john@mail.com",
        "password": "password",
    }
