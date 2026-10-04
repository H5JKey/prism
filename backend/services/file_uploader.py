import asyncio
from typing import BinaryIO

from core.interfaces.clients import AbstractS3Client, AbstractUnitOfWorkClient
from core.interfaces.services import AbstractFileUploader
from core.logging import get_logger
from infrastructure.database.repositories.file import FileRepository
from schemas.file import FileCreate, FileResponse

logger = get_logger(__name__)


class FileUploader(AbstractFileUploader):
    def __init__(
        self,
        bucket: str,
        s3_client: AbstractS3Client,
        unit_of_work: AbstractUnitOfWorkClient,
    ) -> None:
        self.s3_client = s3_client
        self.unit_of_work = unit_of_work
        self.file_repository = self.unit_of_work.get_repository(FileRepository)
        self.bucket = bucket

    async def upload(
        self,
        file_name: str,
        file: BinaryIO,
    ) -> FileResponse:
        key = self.s3_client.generate_key(file_name)
        size = await self.s3_client.get_file_size(self.bucket, key)
        create_file_data = FileCreate(
            name=file_name,
            size=size,
            bucket=self.bucket,
            key=key,
        )
        upload_file_to_s3_coroutine = self.s3_client.put_object(
            bucket=self.bucket,
            key=key,
            file=file,
        )
        create_file_coroutine = self.file_repository.create_file(
            create_file_data=create_file_data,
        )

        created_file, _ = await asyncio.gather(
            create_file_coroutine,
            upload_file_to_s3_coroutine,
        )

        logger.info(
            "Uploaded file, bucket=%s, key=%s, name=%s, size=%s",
            self.bucket,
            key,
            file_name,
            size,
        )
        return FileResponse.model_validate(created_file)
