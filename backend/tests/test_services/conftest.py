import pytest
from core.constants import ProjectVisibility, RenderStatus
from infrastructure.database.models import File, Project, Render, Tag, User
from schemas.event import RenderGeneratedEvent
from schemas.file import FileLocationCreate
from schemas.project import ProjectBase, ProjectCreate, ProjectWithRenderCreate
from schemas.render import RenderBase, RenderCreatePayload, SunInfo
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


@pytest.fixture(scope="function")
def output(render_file: Render) -> FileLocationCreate:
    output = FileLocationCreate(
        bucket=render_file.bucket,
        key=render_file.key,
    )
    return output


@pytest.fixture(scope="function")
def render_generated_event(
    full_project: Project,
    output: FileLocationCreate,
) -> RenderGeneratedEvent:
    render_generated_event = RenderGeneratedEvent(
        project_id=full_project.id,
        output=output,
    )
    return render_generated_event


@pytest.fixture(scope="function")
def render_base_data() -> RenderBase:
    return RenderBase(
        width=1000,
        height=1000,
        samples=100,
        denoiser=True,
        gpu=True,
    )


@pytest.fixture(scope="function")
def sun() -> SunInfo:
    return SunInfo(
        direction=[1.0, 1.0, 1.0],
        color=[1.0, 1.0, 1.0],
        exponent=100,
    )


@pytest.fixture(scope="function")
def render_create_data(
    render_base_data: RenderBase,
    sun: SunInfo,
) -> RenderCreatePayload:
    return RenderCreatePayload(
        background=[1.0, 1.0, 1.0],
        sun=sun,
        **render_base_data.model_dump(),
    )


@pytest.fixture(scope="function")
def project_base_data() -> ProjectBase:
    return ProjectBase(
        name="project_name",
        description="",
        source_file_id=1,
    )


@pytest.fixture(scope="function")
def project_create_data(
    project_base_data: ProjectBase,
) -> ProjectCreate:
    return ProjectCreate(
        visibility=ProjectVisibility.public,
        **project_base_data.model_dump(),
    )


@pytest.fixture(scope="function")
def create_project_request(
    render_create_data: RenderCreatePayload,
    project_create_data: ProjectCreate,
) -> ProjectWithRenderCreate:
    return ProjectWithRenderCreate(
        render=render_create_data,
        project=project_create_data,
    )
