import pytest
from application_factory import create_app
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def test_application() -> FastAPI:
    application = create_app()
    return application


@pytest.fixture(scope="session")
def client(test_application: FastAPI) -> TestClient:
    return TestClient(test_application)
