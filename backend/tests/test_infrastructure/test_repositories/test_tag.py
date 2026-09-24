from infrastructure.database.repositories import TagRepository
from schemas.tag import TagCreate
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_infrastructure.test_database.test_models.factories import (
    create_default_project,
    create_default_tag,
    create_tag,
)


class TestTagRepository:
    async def test_get_by_id(
        self,
        session: AsyncSession,
        tag_repository: TagRepository,
    ) -> None:
        tag = await create_default_tag(session)
        selected_tag = await tag_repository.get_by_id(tag.id)
        session.expunge(tag)
        assert selected_tag.id == tag.id
        assert selected_tag.name == tag.name
        assert selected_tag.project_id == tag.project_id

    async def test_get_by_id_not_exists(
        self,
        tag_repository: TagRepository,
    ) -> None:
        selected_tag = await tag_repository.get_by_id(-1)
        assert selected_tag is None

    async def test_get_project_tags(
        self,
        session: AsyncSession,
        tag_repository: TagRepository,
    ) -> None:
        project = await create_default_project(session)
        tag1 = await create_tag(session, project=project, name="tag1")
        tag2 = await create_tag(session, project=project, name="tag2")
        session.expunge(tag1)
        session.expunge(tag2)
        tags = await tag_repository.get_project_tags(project.id)
        project_tags = sorted(tags, key=lambda tag: tag.id)
        expected_tags = sorted([tag1, tag2], key=lambda tag: tag.id)

        assert project_tags[0].id == expected_tags[0].id
        assert project_tags[0].name == expected_tags[0].name
        assert project_tags[0].project_id == expected_tags[0].project_id

        assert project_tags[1].id == expected_tags[1].id
        assert project_tags[1].name == expected_tags[1].name
        assert project_tags[1].project_id == expected_tags[1].project_id

    async def test_create_tag(
        self,
        session: AsyncSession,
        tag_repository: TagRepository,
    ) -> None:
        project = await create_default_project(session)
        create_tag_data = TagCreate(
            name="tag",
            project_id=project.id,
        )
        created_tag = await tag_repository.create_tag(create_tag_data)
        selected_tag = await tag_repository.get_by_id(created_tag.id)
        assert selected_tag.id is not None
        assert selected_tag.name == created_tag.name
        assert selected_tag.project_id == created_tag.project_id

    async def test_delete_by_id(
        self,
        session: AsyncSession,
        tag_repository: TagRepository,
    ) -> None:
        tag = await create_default_tag(session)
        await tag_repository.delete_by_id(tag.id)
        session.expunge(tag)
        selected_tag = await tag_repository.get_by_id(tag.id)
        assert selected_tag is None
