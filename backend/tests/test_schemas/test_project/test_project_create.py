import pytest
from pydantic import ValidationError

from schemas.project import ProjectCreate, ProjectWithRenderCreate
from tests.test_schemas.helpers import assert_validation_error


class TestProjectCreate:
    @pytest.mark.parametrize(
        "visibility",
        ["public", "private"],
    )
    def test_project_create_valid(
        self, project_create_data: dict, visibility: str
    ) -> None:
        project_create_data["visibility"] = visibility
        project_create = ProjectCreate(**project_create_data)
        assert project_create.model_dump() == project_create_data

    @pytest.mark.parametrize(
        "visibility",
        [
            "pending",
            "sent",
            "rendering",
            "completed",
        ],
    )
    def test_project_create_not_valid_visibility(
        self,
        project_create_data: dict,
        visibility: str,
    ) -> None:
        project_create_data["visibility"] = visibility
        with pytest.raises(ValidationError) as exc_info:
            ProjectCreate(**project_create_data)

        assert_validation_error(
            exc_info,
            "enum",
            "visibility",
        )


class TestProjectWithRenderCreate:
    def test_project_with_render_create_valid(
        self, project_with_render_create_data: dict
    ) -> None:
        project_with_render_create = ProjectWithRenderCreate(
            **project_with_render_create_data
        )
        assert (
            project_with_render_create.model_dump() == project_with_render_create_data
        )

    @pytest.mark.parametrize(
        "field",
        ["render", "project"],
    )
    def test_project_with_render_create_without_required_fields(
        self,
        project_with_render_create_data: dict,
        field: str,
    ) -> None:
        project_with_render_create_data.pop(field)
        with pytest.raises(ValidationError) as exc_info:
            ProjectWithRenderCreate(**project_with_render_create_data)
        assert_validation_error(
            exc_info,
            "missing",
            field,
        )
