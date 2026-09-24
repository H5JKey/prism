import pytest
from core.constants import ProjectVisibility, RenderStatus
from infrastructure.database.repositories import ProjectRepository
from schemas.project import ProjectCreate, ProjectPartialUpdate
from sqlalchemy.ext.asyncio import AsyncSession

from tests.helpers import model_to_dictionary
from tests.test_infrastructure.test_database.test_models.factories import (
    create_default_project,
    create_file,
    create_project,
    create_render,
    create_user,
)


class TestProjectRepository:
    async def test_get_by_id(
        self,
        session: AsyncSession,
        project_repository: ProjectRepository,
    ) -> None:
        user = await create_user(session)
        source_file = await create_file(
            session,
            bucket="fsource_file_bucket",
            key="source_file_key",
        )
        file = await create_file(
            session,
            bucket="file_bucket",
            key="file_key",
        )
        render = await create_render(session, file=file)
        project = await create_project(
            session,
            user=user,
            source_file=source_file,
            render=render,
        )
        selected_project = await project_repository.get_by_id(project.id)
        session.expunge_all()
        assert model_to_dictionary(selected_project) == model_to_dictionary(project)
        assert model_to_dictionary(selected_project.render) == model_to_dictionary(
            render,
        )
        assert model_to_dictionary(selected_project.render.file) == model_to_dictionary(
            file,
        )
        assert model_to_dictionary(selected_project.source_file) == model_to_dictionary(
            source_file,
        )

    async def test_get_by_id_not_exist(
        self,
        project_repository: ProjectRepository,
    ) -> None:
        selected_project = await project_repository.get_by_id(-1)
        assert selected_project is None

    async def test_get_project_owner(
        self,
        session: AsyncSession,
        project_repository: ProjectRepository,
    ) -> None:
        project_owner = await create_user(session)
        source_file = await create_file(
            session,
            bucket="fsource_file_bucket",
            key="source_file_key",
        )
        render = await create_render(session)
        project = await create_project(
            session,
            user=project_owner,
            source_file=source_file,
            render=render,
        )
        selected_project_owner = await project_repository.get_project_owner(project.id)
        assert model_to_dictionary(selected_project_owner) == model_to_dictionary(
            project_owner,
        )

    async def test_get_project_owner_not_exist(
        self,
        project_repository: ProjectRepository,
    ) -> None:
        selected_project_owner = await project_repository.get_project_owner(-1)
        assert selected_project_owner is None

    async def test_get_public_projects(
        self,
        session: AsyncSession,
        project_repository: ProjectRepository,
    ) -> None:
        project = await create_default_project(
            session,
            visibility=ProjectVisibility.public,
        )
        selected_public_projects = await project_repository.get_public_projects(
            size=10,
            page=1,
        )
        assert len(selected_public_projects) == 1
        assert model_to_dictionary(selected_public_projects[0]) == model_to_dictionary(
            project,
        )

    async def test_get_public_projects_not_exists(
        self,
        session: AsyncSession,
        project_repository: ProjectRepository,
    ) -> None:
        await create_default_project(session, visibility=ProjectVisibility.private)
        selected_public_projects = await project_repository.get_public_projects(
            size=10,
            page=1,
        )
        assert len(selected_public_projects) == 0

    @pytest.mark.parametrize(
        "visibility",
        [
            ProjectVisibility.public,
            ProjectVisibility.private,
        ],
    )
    async def test_get_user_projects(
        self,
        session: AsyncSession,
        project_repository: ProjectRepository,
        visibility: str,
    ) -> None:
        project_owner = await create_user(session)
        source_file = await create_file(
            session,
            bucket="fsource_file_bucket",
            key="source_file_key",
        )
        render = await create_render(session)
        project = await create_project(
            session,
            user=project_owner,
            source_file=source_file,
            render=render,
            visibility=visibility,
        )
        selected_user_projects = await project_repository.get_user_projects(
            project_owner.id,
            size=10,
            page=1,
        )
        assert len(selected_user_projects) == 1
        assert model_to_dictionary(selected_user_projects[0]) == model_to_dictionary(
            project,
        )

    async def test_get_user_public_projects(
        self,
        session: AsyncSession,
        project_repository: ProjectRepository,
    ) -> None:
        project_owner = await create_user(session)
        source_file = await create_file(
            session,
            bucket="fsource_file_bucket",
            key="source_file_key",
        )
        render = await create_render(session)
        public_project = await create_project(
            session,
            user=project_owner,
            source_file=source_file,
            render=render,
            visibility="public",
        )
        await create_project(
            session,
            user=project_owner,
            source_file=source_file,
            render=render,
            visibility="private",
        )
        selected_user_public_projects = (
            await project_repository.get_user_public_projects(
                project_owner.id,
                size=10,
                page=1,
            )
        )
        assert len(selected_user_public_projects) == 1
        assert model_to_dictionary(
            selected_user_public_projects[0],
        ) == model_to_dictionary(
            public_project,
        )

    async def test_update_project_status(
        self,
        session: AsyncSession,
        project_repository: ProjectRepository,
    ) -> None:
        project = await create_default_project(session)
        await project_repository.update_project_status(project.id)
        expected_project_data = model_to_dictionary(project)
        expected_project_data["status"] = RenderStatus.completed
        assert model_to_dictionary(project) == expected_project_data

    async def test_create_project(
        self,
        session: AsyncSession,
        project_repository: ProjectRepository,
    ) -> None:
        user = await create_user(session)
        source_file = await create_file(session)
        render = await create_render(session)
        create_project_data = ProjectCreate(
            name="project_name",
            description="description",
            source_file_id=source_file.id,
            visibility=ProjectVisibility.public,
        )
        created_project = await project_repository.create_project(
            user.id,
            render.id,
            create_project_data,
        )
        session.expunge(created_project)
        selected_project = await project_repository.get_by_id(created_project.id)
        assert selected_project.name == create_project_data.name
        assert selected_project.description == create_project_data.description
        assert selected_project.visibility == create_project_data.visibility
        assert selected_project.user_id == user.id
        assert selected_project.source_file_id == source_file.id
        assert selected_project.render_id == render.id
        assert selected_project.status == RenderStatus.rendering

    async def test_partial_update_project(
        self,
        session: AsyncSession,
        project_repository: ProjectRepository,
    ) -> None:
        project = await create_default_project(session)
        partial_update_project_data = ProjectPartialUpdate(
            name="updated_project_name",
            description="updated_description",
            visibility=ProjectVisibility.private,
        )
        await project_repository.partial_update_project(
            project.id,
            partial_update_project_data,
        )
        session.expunge(project)
        selected_project = await project_repository.get_by_id(project.id)
        assert selected_project.name == partial_update_project_data.name
        assert selected_project.description == partial_update_project_data.description
        assert selected_project.visibility == partial_update_project_data.visibility
        assert selected_project.user_id == project.user_id
        assert selected_project.source_file_id == project.source_file_id
        assert selected_project.render_id == project.render_id
        assert selected_project.status == project.status

    async def test_delete_by_id(
        self,
        session: AsyncSession,
        project_repository: ProjectRepository,
    ) -> None:
        project = await create_default_project(session)
        await project_repository.delete_by_id(project.id)
        session.expunge(project)
        deleted_project = await project_repository.get_by_id(project.id)
        assert deleted_project is None
