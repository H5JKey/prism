import pytest
from core.constants import ProjectVisibility
from core.exceptions.auth import PermissionDeniedError
from core.exceptions.project import ProjectIdNotFoundError
from core.exceptions.tag import TagIdNotFoundError
from core.exceptions.user import UserIdNotFoundError
from infrastructure.database.models import Project, Tag, User
from pytest_mock import MockerFixture
from schemas.tag import TagCreate
from services.tag import TagService


class TestTagService:
    async def test_get_project_tags_valid(
        self,
        project_owner: User,
        project: Project,
        tag: Tag,
        mocker: MockerFixture,
        tag_service: TagService,
    ) -> None:
        get_project_by_id_mock = mocker.patch.object(
            tag_service.project_repository,
            "get_by_id",
            return_value=project,
            autospec=True,
        )
        get_project_owner_mock = mocker.patch.object(
            tag_service.project_repository,
            "get_project_owner",
            return_value=project_owner,
            autospec=True,
        )
        get_project_tags_mock = mocker.patch.object(
            tag_service.tag_repository,
            "get_project_tags",
            return_value=[tag],
            autospec=True,
        )

        tags = await tag_service.get_project_tags(
            project_id=project.id,
            user_id=project_owner.id + 1,
        )
        get_project_by_id_mock.assert_called_once_with(project.id)
        get_project_owner_mock.assert_called_once_with(project.id)
        get_project_tags_mock.assert_called_once_with(project.id)

        assert len(tags.tag_list) == 1
        selected_tag = tags.tag_list[0]
        assert selected_tag.id == tag.id
        assert selected_tag.name == tag.name
        assert selected_tag.project_id == tag.project_id

    async def test_get_project_tags_project_not_exists(
        self,
        mocker: MockerFixture,
        tag_service: TagService,
    ) -> None:
        get_project_by_id_mock = mocker.patch.object(
            tag_service.project_repository,
            "get_by_id",
            return_value=None,
            autospec=True,
        )
        project_id, user_id = 1, 1
        with pytest.raises(ProjectIdNotFoundError):
            await tag_service.get_project_tags(project_id=project_id, user_id=user_id)
        get_project_by_id_mock.assert_called_once_with(project_id)

    async def test_get_project_tags_user_not_exists(
        self,
        project: Project,
        mocker: MockerFixture,
        tag_service: TagService,
    ) -> None:
        get_project_by_id_mock = mocker.patch.object(
            tag_service.project_repository,
            "get_by_id",
            return_value=project,
            autospec=True,
        )
        get_project_owner_mock = mocker.patch.object(
            tag_service.project_repository,
            "get_project_owner",
            return_value=None,
            autospec=True,
        )
        project_id, user_id = 1, 1
        with pytest.raises(UserIdNotFoundError):
            await tag_service.get_project_tags(project_id=project_id, user_id=user_id)
        get_project_by_id_mock.assert_called_once_with(project.id)
        get_project_owner_mock.assert_called_once_with(project.id)

    async def test_get_private_project_tags_not_by_owner(
        self,
        project_owner: User,
        project: Project,
        mocker: MockerFixture,
        tag_service: TagService,
    ) -> None:
        project.visibility = ProjectVisibility.private
        get_project_by_id_mock = mocker.patch.object(
            tag_service.project_repository,
            "get_by_id",
            return_value=project,
            autospec=True,
        )
        get_project_owner_mock = mocker.patch.object(
            tag_service.project_repository,
            "get_project_owner",
            return_value=project_owner,
            autospec=True,
        )
        with pytest.raises(PermissionDeniedError):
            await tag_service.get_project_tags(
                project_id=project.id,
                user_id=project_owner.id + 1,
            )
        get_project_by_id_mock.assert_called_once_with(project.id)
        get_project_owner_mock.assert_called_once_with(project.id)

    async def test_create_tag_valid(
        self,
        project_owner: User,
        project: Project,
        created_tag: Tag,
        create_tag_data: TagCreate,
        mocker: MockerFixture,
        tag_service: TagService,
    ) -> None:
        get_project_by_id_mock = mocker.patch.object(
            tag_service.project_repository,
            "get_by_id",
            return_value=project,
            autospec=True,
        )
        get_project_owner_mock = mocker.patch.object(
            tag_service.project_repository,
            "get_project_owner",
            return_value=project_owner,
            autospec=True,
        )
        create_tag_mock = mocker.patch.object(
            tag_service.tag_repository,
            "create_tag",
            return_value=created_tag,
            autospec=True,
        )
        created_tag = await tag_service.create_tag(create_tag_data, project_owner.id)
        get_project_by_id_mock.assert_called_once_with(project.id)
        get_project_owner_mock.assert_called_once_with(project.id)
        create_tag_mock.assert_called_once_with(create_tag_data)

        assert created_tag.name == create_tag_data.name
        assert created_tag.project_id == create_tag_data.project_id

    async def test_create_tag_project_not_exists(
        self,
        mocker: MockerFixture,
        project_owner: User,
        create_tag_data: TagCreate,
        tag_service: TagService,
    ) -> None:
        get_project_by_id_mock = mocker.patch.object(
            tag_service.project_repository,
            "get_by_id",
            return_value=None,
            autospec=True,
        )
        with pytest.raises(ProjectIdNotFoundError):
            await tag_service.create_tag(create_tag_data, project_owner.id)
        get_project_by_id_mock.assert_called_once_with(create_tag_data.project_id)

    async def test_create_tag_user_not_exists(
        self,
        mocker: MockerFixture,
        project: Project,
        create_tag_data: TagCreate,
        tag_service: TagService,
    ) -> None:
        get_project_by_id_mock = mocker.patch.object(
            tag_service.project_repository,
            "get_by_id",
            return_value=project,
            autospec=True,
        )
        get_project_owner_mock = mocker.patch.object(
            tag_service.project_repository,
            "get_project_owner",
            return_value=None,
            autospec=True,
        )
        with pytest.raises(UserIdNotFoundError):
            await tag_service.create_tag(create_tag_data, user_id=-1)

        get_project_by_id_mock.assert_called_once_with(project.id)
        get_project_owner_mock.assert_called_once_with(project.id)

    async def test_create_tag_by_not_project_owner(
        self,
        mocker: MockerFixture,
        project_owner: Project,
        project: Project,
        create_tag_data: TagCreate,
        tag_service: TagService,
    ) -> None:
        get_project_by_id_mock = mocker.patch.object(
            tag_service.project_repository,
            "get_by_id",
            return_value=project,
            autospec=True,
        )
        get_project_owner_mock = mocker.patch.object(
            tag_service.project_repository,
            "get_project_owner",
            return_value=project_owner,
            autospec=True,
        )
        with pytest.raises(PermissionDeniedError):
            await tag_service.create_tag(create_tag_data, project_owner.id + 1)
        get_project_by_id_mock.assert_called_once_with(project.id)
        get_project_owner_mock.assert_called_once_with(project.id)

    async def test_delete_by_id_valid(
        self,
        mocker: MockerFixture,
        project_owner: User,
        tag_with_project: Tag,
        tag_service: TagService,
    ) -> None:
        get_tag_by_id_mock = mocker.patch.object(
            tag_service.tag_repository,
            "get_by_id",
            return_value=tag_with_project,
            autospec=True,
        )
        get_project_owner_mock = mocker.patch.object(
            tag_service.project_repository,
            "get_project_owner",
            return_value=project_owner,
            autospec=True,
        )
        delete_tag_by_id_mock = mocker.patch.object(
            tag_service.tag_repository,
            "delete_by_id",
            return_value=None,
            autospec=True,
        )
        await tag_service.delete_by_id(tag_with_project.id, project_owner.id)
        get_tag_by_id_mock.assert_called_once_with(tag_with_project.id)
        get_project_owner_mock.assert_called_once_with(project_owner.id)
        delete_tag_by_id_mock.assert_called_once_with(tag_with_project.id)

    async def test_delete_by_id_tag_not_exists(
        self,
        mocker: MockerFixture,
        tag_service: TagService,
    ) -> None:
        get_tag_by_id_mock = mocker.patch.object(
            tag_service.tag_repository,
            "get_by_id",
            return_value=None,
            autospec=True,
        )
        tag_id = 1
        with pytest.raises(TagIdNotFoundError):
            await tag_service.delete_by_id(tag_id=tag_id, user_id=1)
        get_tag_by_id_mock.assert_called_once_with(tag_id)

    async def test_delete_by_id_user_not_exists(
        self,
        mocker: MockerFixture,
        tag_with_project: Tag,
        tag_service: TagService,
    ) -> None:
        get_tag_by_id_mock = mocker.patch.object(
            tag_service.tag_repository,
            "get_by_id",
            return_value=tag_with_project,
            autospec=True,
        )
        get_project_owner_mock = mocker.patch.object(
            tag_service.project_repository,
            "get_project_owner",
            return_value=None,
            autospec=True,
        )
        user_id = 1
        with pytest.raises(UserIdNotFoundError):
            await tag_service.delete_by_id(tag_id=tag_with_project.id, user_id=user_id)
        get_tag_by_id_mock.assert_called_once_with(tag_with_project.id)
        get_project_owner_mock.assert_called_once_with(user_id)

    async def test_delete_by_id_not_by_project_owner(
        self,
        mocker: MockerFixture,
        project_owner: User,
        tag_with_project: Tag,
        tag_service: TagService,
    ) -> None:
        get_tag_by_id_mock = mocker.patch.object(
            tag_service.tag_repository,
            "get_by_id",
            return_value=tag_with_project,
            autospec=True,
        )
        get_project_owner_mock = mocker.patch.object(
            tag_service.project_repository,
            "get_project_owner",
            return_value=project_owner,
            autospec=True,
        )
        with pytest.raises(PermissionDeniedError):
            await tag_service.delete_by_id(
                tag_id=tag_with_project.id,
                user_id=project_owner.id + 1,
            )

        get_tag_by_id_mock.assert_called_once_with(tag_with_project.id)
        get_project_owner_mock.assert_called_once_with(project_owner.id)
