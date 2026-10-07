from fastapi import status
from fastapi.testclient import TestClient


class TestReadRootEndpoint:
    def test_read_root(self, client: TestClient) -> None:
        name = "test_name"
        response = client.get("/", params={"name": name})
        response_data = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert name in response_data["message"]
        assert response_data.get("docs_url") is not None

    def test_read_root_default_query_params(self, client: TestClient) -> None:
        response = client.get("/")
        response_data = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert response_data.get("message") is not None
        assert response_data.get("docs_url") is not None


class TestCheckHealthEndpoint:
    def test_check_health(self, client: TestClient) -> None:
        response = client.get("/health")
        response_data = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert response_data["status"] == "ok"
