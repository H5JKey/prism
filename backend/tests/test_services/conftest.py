import pytest
from core.constants import ProjectVisibility
from infrastructure.database.models import Project, Tag, User
from schemas.tag import TagCreate


@pytest.fixture
def project_owner() -> User:
    owner = User(
        id=1,
        surname="surname",
        name="name",
        username="username",
        email="email@email.com",
        encrypted_password="encrypted_password",
    )
    return owner


@pytest.fixture
def project(project_owner: User) -> Project:
    project = Project(
        id=1,
        name="name",
        description="",
        user_id=project_owner.id,
        source_file_id=1,
        render_id=1,
        visibility=ProjectVisibility.public,
    )
    return project


@pytest.fixture
def create_tag_data(project: Project) -> TagCreate:
    return TagCreate(
        name="test_tag",
        project_id=project.id,
    )


@pytest.fixture
def created_tag(create_tag_data: TagCreate) -> Tag:
    return Tag(id=1, **create_tag_data.model_dump())


@pytest.fixture
def tag(project: Project) -> Tag:
    tag = Tag(
        id=1,
        name="tag_name",
        project_id=project.id,
    )
    return tag


@pytest.fixture
def tag_with_project(tag: Tag, project: Project) -> Tag:
    tag.project = project
    return tag
