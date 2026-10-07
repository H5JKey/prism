from types import TracebackType
from typing import Self

from core.exceptions.project import ProjectIdNotFoundError
from core.interfaces.clients import AbstractS3Client, AbstractUnitOfWorkClient
from core.logging import get_logger
from infrastructure.database.repositories import (
    FileRepository,
    ProjectRepository,
    RenderRepository,
)
from schemas.event import RenderGeneratedEvent
from schemas.file import FileCreate
from schemas.project import ProjectWithRenderFileResponse

logger = get_logger(__name__)


class RenderGenerateHandlerService:
    def __init__(
        self,
        unit_of_work: AbstractUnitOfWorkClient,
    ) -> None:
        self.unit_of_work = unit_of_work
        self.project_repository = self.unit_of_work.get_repository(ProjectRepository)
        self.render_repository = self.unit_of_work.get_repository(RenderRepository)
        self.file_repository = self.unit_of_work.get_repository(FileRepository)

    async def __aenter__(self) -> "Self":
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """
        Метод для действий при выходе из контекстного менеджера.
        """

    async def handle_render_generated(
        self,
        render_generated_event: RenderGeneratedEvent,
        s3_client: AbstractS3Client,
    ) -> None:
        project_id = render_generated_event.project_id
        file_location = render_generated_event.output
        bucket = file_location.bucket
        key = file_location.key

        project = await self.project_repository.get_by_id(project_id)
        if project is None:
            raise ProjectIdNotFoundError(project_id)

        name = f"{project.name}.png"
        size = await s3_client.get_file_size(bucket, key)
        file = FileCreate(
            name=name,
            size=size,
            bucket=bucket,
            key=key,
        )
        render_file = await self.file_repository.create_file(file)
        await self.render_repository.add_render_file(
            render_id=project.render.id,
            file_id=render_file.id,
        )

        logger.info(
            "Added render to projects, project_id=%s, user_id=%s, render_id=%s, source_file_id=%s, name=%s, status=%s, visibility=%s",  # noqa: E501
            project.id,
            project.user_id,
            project.render_id,
            project.source_file_id,
            project.name,
            project.status,
            project.visibility,
        )

    async def update_project_status(
        self,
        project_id: int,
    ) -> ProjectWithRenderFileResponse:
        project = await self.project_repository.update_project_status(project_id)
        if project is None:
            raise ProjectIdNotFoundError(project_id)

        logger.info(
            "Updated projects status, project_id=%s, user_id=%s, render_id=%s, source_file_id=%s, name=%s, status=%s, visibility=%s",  # noqa: E501
            project.id,
            project.user_id,
            project.render_id,
            project.source_file_id,
            project.name,
            project.status,
            project.visibility,
        )
        return ProjectWithRenderFileResponse.model_validate(project)
