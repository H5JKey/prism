import pytest
from core.constants import ProjectVisibility
from infrastructure.database.models import Project, Render
from schemas.event import RenderGeneratedEvent
from schemas.file import FileLocationCreate
from schemas.project import ProjectBase, ProjectCreate, ProjectWithRenderCreate
from schemas.render import RenderBase, RenderCreatePayload, SunInfo


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
