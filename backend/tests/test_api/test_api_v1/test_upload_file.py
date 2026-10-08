from dependencies.services import get_input_file_uploader
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from services.file_uploader import FileUploader

from tests.test_api.utils import get_result_json


class TestUploadFileEndpoint:
    url = "/api/v1/files/upload"

    def test_upload_file_valid(
        self,
        application: FastAPI,
        auth_client: TestClient,
        file_uploader: FileUploader,
    ) -> None:
        application.dependency_overrides[get_input_file_uploader] = (
            lambda: file_uploader
        )
        files = {"uploaded_file": ("test_file.txt", b"test file content", "text/plain")}
        response = auth_client.post(self.url, files=files)
        response_data = response.json()
        assert response.status_code == status.HTTP_201_CREATED
        assert response_data == get_result_json(file_uploader, "upload")
