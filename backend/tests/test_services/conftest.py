import pytest
from core.constants import ProjectVisibility, RenderStatus
from infrastructure.database.models import File, Project, Render, Tag, User
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
        name="project_name",
        description="",
        user_id=project_owner.id,
        source_file_id=1,
        render_id=1,
        status=RenderStatus.rendering,
        visibility=ProjectVisibility.public,
    )
    return project


@pytest.fixture
def source_file() -> File:
    file = File(
        id=2,
        name="source_file_name",
        size=1000,
        bucket="source_bucket_name",
        key="source_key_name",
    )
    return file


@pytest.fixture
def render_file() -> File:
    file = File(
        id=1,
        name="file_name",
        size=1000,
        bucket="bucket_name",
        key="key_name",
    )
    return file


@pytest.fixture
def render(render_file: File) -> Render:
    render = Render(
        id=1,
        width=1000,
        height=1000,
        samples=100,
        denoiser=True,
        gpu=True,
        file_id=render_file.id,
    )
    render.file = render_file
    return render


@pytest.fixture
def full_project(project: Project, render: Render, source_file: File) -> Project:
    project.render_id = render.id
    project.render = render

    project.source_file_id = source_file.id
    project.source_file = source_file
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
