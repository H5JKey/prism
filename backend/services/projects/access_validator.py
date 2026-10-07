from core.constants import ProjectVisibility
from core.exceptions.auth import PermissionDeniedError
from core.exceptions.project import ProjectIdNotFoundError
from core.exceptions.user import UserIdNotFoundError
from core.interfaces.clients import AbstractUnitOfWorkClient
from infrastructure.database.models import Project
from infrastructure.database.repositories import (
    ProjectRepository,
)


class ProjectAccessValidatorService:
    def __init__(
        self,
        unit_of_work: AbstractUnitOfWorkClient,
    ) -> None:
        self.unit_of_work = unit_of_work
        self.project_repository = self.unit_of_work.get_repository(ProjectRepository)

    async def validate_access_to_change_project(
        self,
        project_id: int,
        user_id: int,
    ) -> Project:
        project = await self.project_repository.get_by_id(
            project_id,
        )
        if project is None:
            raise ProjectIdNotFoundError(project_id)

        await self.validate_project_owner(project_id, user_id)
        return project  # type: ignore[no-any-return]

    async def validate_access_to_get_project(
        self,
        project_id: int,
        user_id: int,
    ) -> Project:
        project = await self.project_repository.get_by_id(
            project_id,
        )
        if project is None:
            raise ProjectIdNotFoundError(project_id)

        if project.visibility == ProjectVisibility.private:
            await self.validate_project_owner(project_id, user_id)

        return project  # type: ignore[no-any-return]

    async def validate_project_owner(self, project_id: int, user_id: int) -> None:
        get_owner_coroutine = self.project_repository.get_project_owner(
            project_id,
        )
        project_owner = await get_owner_coroutine
        if project_owner is None:
            raise UserIdNotFoundError(user_id)
        if project_owner.id != user_id:
            raise PermissionDeniedError
