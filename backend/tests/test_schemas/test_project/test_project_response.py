import pytest
from pydantic import ValidationError

from schemas.project import ProjectResponse, ProjectFullResponse, ProjectResponseList
from tests.test_schemas.helpers import assert_validation_error


class TestProjectResponse:
    @pytest.mark.parametrize(
        "field, value",
        [
            ["visibility", "pending"],
            ["visibility", "completed"],
            ["status", "rendering"],
            ["status", "completed"],
        ],
    )
    def test_project_response_valid(
        self,
        project_response_data: dict,
        field: str,
        value: str,
    ) -> None:
        project_response = ProjectResponse(**project_response_data)
        assert project_response.model_dump() == project_response_data

    @pytest.mark.parametrize(
        "visibility",
        [
            "pending",
            "sent",
            "rendering",
            "completed",
        ],
    )
    def test_project_response_not_valid_visibility(
        self,
        project_response_data: dict,
        visibility: str,
    ) -> None:
        project_response_data["visibility"] = visibility
        with pytest.raises(ValidationError) as exc_info:
            ProjectResponse(**project_response_data)

        assert_validation_error(
            exc_info,
            "enum",
            "visibility",
        )

    @pytest.mark.parametrize(
        "status",
        [
            "pending",
            "sent",
            "public",
            "private",
        ],
    )
    def test_project_response_not_valid_status(
        self,
        project_response_data: dict,
        status: str,
    ) -> None:
        project_response_data["status"] = status
        with pytest.raises(ValidationError) as exc_info:
            ProjectResponse(**project_response_data)

        assert_validation_error(
            exc_info,
            "enum",
            "status",
        )

    @pytest.mark.parametrize(
        "field",
        ["render_id"],
    )
    def test_project_response_without_optional_field(
        self,
        project_response_data: dict,
        field: str,
    ) -> None:
        project_response_data.pop(field)
        project_response = ProjectResponse(**project_response_data)
        assert getattr(project_response, field) is None


class TestProjectFullResponse:
    def test_project_full_response_valid(
        self, project_full_response_data: dict
    ) -> None:
        project_full_response = ProjectFullResponse(**project_full_response_data)
        assert project_full_response.model_dump() == project_full_response_data

    @pytest.mark.parametrize(
        "field",
        ["url"],
    )
    def test_project_full_response_without_required_field(
        self,
        project_full_response_data: dict,
        field: str,
    ) -> None:
        project_full_response_data.pop(field)
        with pytest.raises(ValidationError) as exc_info:
            ProjectFullResponse(**project_full_response_data)

        assert_validation_error(
            exc_info,
            "missing",
            field,
        )


class TestProjectResponseList:
    def test_project_response_list_valid(
        self,
        project_response_list_data: dict,
    ) -> None:
        project_response_list = ProjectResponseList(**project_response_list_data)
        assert project_response_list.model_dump() == project_response_list_data

    @pytest.mark.parametrize(
        "field",
        ["project_list", "size", "page"],
    )
    def test_project_response_list_without_required_field(
        self,
        project_response_list_data: dict,
        field: str,
    ) -> None:
        project_response_list_data.pop(field)
        with pytest.raises(ValidationError) as exc_info:
            ProjectResponseList(**project_response_list_data)

        assert_validation_error(
            exc_info,
            "missing",
            field,
        )
