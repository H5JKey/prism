from core.config.application import settings
from core.exceptions.file import FileIdNotFoundError
from core.interfaces.clients import AbstractS3Client, AbstractUnitOfWorkClient
from core.interfaces.services import AbstractProjectAccessValidatorService
from core.logging import get_logger
from infrastructure.database.repositories import (
    FileRepository,
    OutboxRepository,
    ProjectRepository,
    RenderRepository,
)
from schemas.event import (
    CreateProjectEvent,
    EventCreate,
)
from schemas.file import FileLocationCreate
from schemas.project import (
    ProjectPartialUpdate,
    ProjectWithRenderCreate,
    ProjectWithRenderFileFullResponse,
    ProjectWithRenderFileResponse,
    ProjectWithRenderResponse,
)
from schemas.render import RenderCreate

logger = get_logger(__name__)


def generate_output_key(input_key: str) -> str:
    output_key_list = input_key.split(".")
    output_key_list[-1] = "png"
    output_key = ".".join(output_key_list)
    return output_key


class ProjectService:
    def __init__(
        self,
        unit_of_work: AbstractUnitOfWorkClient,
        project_access_validator: AbstractProjectAccessValidatorService,
    ) -> None:
        self.project_access_validator = project_access_validator
        self.unit_of_work = unit_of_work
        self.project_repository = self.unit_of_work.get_repository(ProjectRepository)
        self.render_repository = self.unit_of_work.get_repository(RenderRepository)
        self.file_repository = self.unit_of_work.get_repository(FileRepository)
        self.outbox_repository = self.unit_of_work.get_repository(OutboxRepository)

    async def get_by_id(
        self,
        project_id: int,
        user_id: int,
        s3_client: AbstractS3Client,
    ) -> ProjectWithRenderFileFullResponse:
        project = await self.project_access_validator.validate_access_to_get_project(
            project_id,
            user_id,
        )
        logger.info(
            "Received projects, project_id=%s, user_id=%s, render_id=%s, source_file_id=%s, name=%s, status=%s, visibility=%s",  # noqa: E501
            project.id,
            project.user_id,
            project.render_id,
            project.source_file_id,
            project.name,
            project.status,
            project.visibility,
        )
        return await ProjectWithRenderFileFullResponse.get_from_database(
            project,
            s3_client,
        )

    async def create_project(
        self,
        user_id: int,
        create_project: ProjectWithRenderCreate,
    ) -> ProjectWithRenderResponse:
        create_project_data = create_project.project
        create_full_render_data = create_project.render
        file_id = create_project_data.source_file_id
        file = await self.file_repository.get_by_id(file_id)
        if file is None:
            raise FileIdNotFoundError(file_id)

        create_render_data = RenderCreate.model_validate(
            create_full_render_data.model_dump(),
        )
        render = await self.render_repository.create_render(create_render_data)
        project = await self.project_repository.create_project(
            user_id=user_id,
            render_id=render.id,
            create_project_data=create_project_data,
        )
        input_file_location = FileLocationCreate(
            bucket=settings.minio.bucket.glb_sources,
            key=file.key,
        )
        output_key = generate_output_key(file.key)
        output_file_location = FileLocationCreate(
            bucket=settings.minio.bucket.renders,
            key=output_key,
        )
        event = CreateProjectEvent(
            project_id=project.id,
            input=input_file_location,
            output=output_file_location,
            render=create_full_render_data,
        )
        event_create_data = EventCreate(
            topic=settings.kafka.topic.project_created,
            message=event.model_dump(),
        )
        await self.outbox_repository.create_event(event_create_data)

        logger.info(
            "Created projects, project_id=%s, user_id=%s, render_id=%s, source_file_id=%s, name=%s, status=%s, visibility=%s",  # noqa: E501
            project.id,
            user_id,
            project.render_id,
            project.source_file_id,
            project.name,
            project.status,
            project.visibility,
        )
        return ProjectWithRenderResponse.get_from_database(project, render)

    async def partial_update_project(
        self,
        project_id: int,
        user_id: int,
        partial_update_project_data: ProjectPartialUpdate,
    ) -> ProjectWithRenderFileResponse:
        await self.project_access_validator.validate_access_to_change_project(
            project_id,
            user_id,
        )
        project = await self.project_repository.partial_update_project(
            project_id,
            partial_update_project_data,
        )
        logger.info(
            "Updated projects, project_id=%s, user_id=%s, render_id=%s, source_file_id=%s, name=%s, status=%s, visibility=%s",  # noqa: E501
            project_id,
            user_id,
            project.render_id,
            project.source_file_id,
            project.name,
            project.status,
            project.visibility,
        )
        return ProjectWithRenderFileResponse.model_validate(project)

    async def delete_by_id(
        self,
        project_id: int,
        user_id: int,
    ) -> None:
        project = await self.project_access_validator.validate_access_to_change_project(
            project_id,
            user_id,
        )
        await self.project_repository.delete_by_id(project_id)
        logger.info(
            "Deleted projects, project_id=%s, user_id=%s, render_id=%s, source_file_id=%s, name=%s, status=%s, visibility=%s",  # noqa: E501
            project_id,
            user_id,
            project.render_id,
            project.source_file_id,
            project.name,
            project.status,
            project.visibility,
        )
