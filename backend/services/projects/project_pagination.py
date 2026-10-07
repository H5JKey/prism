from core.exceptions.user import UserIdNotFoundError
from core.interfaces.clients import AbstractUnitOfWorkClient
from infrastructure.database.repositories import ProjectRepository, UserRepository
from schemas.project import ProjectResponse, ProjectResponseList


class ProjectPaginationService:
    def __init__(
        self,
        unit_of_work: AbstractUnitOfWorkClient,
    ) -> None:
        self.unit_of_work = unit_of_work
        self.project_repository = self.unit_of_work.get_repository(ProjectRepository)
        self.user_repository = self.unit_of_work.get_repository(UserRepository)

    async def get_user_projects(
        self,
        user_id: int,
        size: int,
        page: int,
    ) -> ProjectResponseList:
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise UserIdNotFoundError(user_id)

        get_projects = self.project_repository.get_user_projects(
            user_id,
            size,
            page,
        )
        projects = [
            ProjectResponse.model_validate(project) for project in await get_projects
        ]
        return ProjectResponseList(
            project_list=projects,
            size=size,
            page=page,
        )

    async def get_public_projects(self, size: int, page: int) -> ProjectResponseList:
        get_projects = self.project_repository.get_public_projects(size, page)
        projects = [
            ProjectResponse.model_validate(project) for project in await get_projects
        ]
        return ProjectResponseList(
            project_list=projects,
            size=size,
            page=page,
        )

    async def get_user_public_projects(
        self,
        user_id: int,
        size: int,
        page: int,
    ) -> ProjectResponseList:
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise UserIdNotFoundError(user_id)

        get_projects = self.project_repository.get_user_public_projects(
            user_id,
            size,
            page,
        )
        projects = [
            ProjectResponse.model_validate(project) for project in await get_projects
        ]
        return ProjectResponseList(
            project_list=projects,
            size=size,
            page=page,
        )
