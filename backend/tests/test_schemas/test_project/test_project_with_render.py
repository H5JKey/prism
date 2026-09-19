import pytest
from pydantic import ValidationError

from schemas.project import (
    ProjectWithRenderFileFullResponse,
    ProjectWithRenderResponse,
    ProjectWithRenderFileResponse,
)
from tests.test_schemas.helpers import assert_validation_error


class TestProjectWithRenderFileFullResponse:
    def test_project_with_render_file_full_response_valid(
        self,
        project_with_render_file_full_response_data: dict,
    ) -> None:
        project_with_render_file_full_response = ProjectWithRenderFileFullResponse(
            **project_with_render_file_full_response_data
        )
        assert (
            project_with_render_file_full_response.model_dump()
            == project_with_render_file_full_response_data
        )

    @pytest.mark.parametrize("field", ["render"])
    def test_project_with_render_file_full_without_required_field(
        self,
        project_with_render_file_full_response_data: dict,
        field: str,
    ) -> None:
        project_with_render_file_full_response_data.pop(field)
        with pytest.raises(ValidationError) as exc_info:
            ProjectWithRenderFileFullResponse(
                **project_with_render_file_full_response_data
            )

        assert_validation_error(
            exc_info,
            "missing",
            field,
        )


class TestProjectWithRenderResponse:
    def test_project_with_render_response_valid(
        self,
        project_with_render_response_data: dict,
    ) -> None:
        project_with_render_response = ProjectWithRenderResponse(
            **project_with_render_response_data
        )
        assert (
            project_with_render_response.model_dump()
            == project_with_render_response_data
        )

    @pytest.mark.parametrize("field", ["render"])
    def test_project_with_render_response_without_required_field(
        self,
        project_with_render_response_data: dict,
        field: str,
    ) -> None:
        project_with_render_response_data.pop(field)
        with pytest.raises(ValidationError) as exc_info:
            ProjectWithRenderResponse(**project_with_render_response_data)

        assert_validation_error(
            exc_info,
            "missing",
            field,
        )


class TestProjectWithRenderFileResponse:
    def test_project_with_render_file_response_valid(
        self,
        project_with_render_file_response_data: dict,
    ) -> None:
        project_with_render_file_response = ProjectWithRenderFileResponse(
            **project_with_render_file_response_data
        )
        assert (
            project_with_render_file_response.model_dump()
            == project_with_render_file_response_data
        )

    @pytest.mark.parametrize("field", ["render"])
    def test_project_with_render_file_response_without_required_field(
        self,
        project_with_render_file_response_data: dict,
        field: str,
    ) -> None:
        project_with_render_file_response_data.pop(field)
        with pytest.raises(ValidationError) as exc_info:
            ProjectWithRenderFileResponse(**project_with_render_file_response_data)

        assert_validation_error(
            exc_info,
            "missing",
            field,
        )
