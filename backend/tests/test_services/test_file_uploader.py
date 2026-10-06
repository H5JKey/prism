from services.file_uploader import FileUploader


class TestFileUploader:
    async def test_upload_valid(
        self,
        file_uploader: FileUploader,
    ) -> None:
        file = b"sequence of bytes"
        file_name = "file_name.glb"
        file_size = 1000

        file_response = await file_uploader.upload(
            file_name,
            file,
        )
        assert file_response.name == file_name
        assert file_response.size == file_size
