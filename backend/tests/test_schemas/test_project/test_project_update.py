import pytest
from pydantic import ValidationError

from core.constants import (
    PROJECT_NAME_MIN_LENGTH,
    PROJECT_NAME_MAX_LENGTH,
    PROJECT_DESCRIPTION_MAX_LENGTH,
    PROJECT_DESCRIPTION_MIN_LENGTH,
)
from schemas.project import ProjectPartialUpdate
from tests.test_schemas.helpers import assert_validation_error


class TestProjectPartialUpdate:
    def test_project_partial_update_valid(
        self,
        project_partial_update_data: dict,
    ) -> None:
        project_partial_update = ProjectPartialUpdate(**project_partial_update_data)
        assert project_partial_update.model_dump() == project_partial_update_data

    @pytest.mark.parametrize(
        "field, value, expected_error",
        [
            ["name", "a" * (PROJECT_NAME_MIN_LENGTH - 1), "string_too_short"],
            ["name", "a" * (PROJECT_NAME_MAX_LENGTH + 1), "string_too_long"],
            [
                "description",
                "a" * (PROJECT_DESCRIPTION_MAX_LENGTH + 1),
                "string_too_long",
            ],
        ],
    )
    def test_project_partial_update_not_valid_field_value(
        self,
        project_partial_update_data: dict,
        field: str,
        value: str,
        expected_error: str,
    ) -> None:
        project_partial_update_data[field] = value
        with pytest.raises(ValidationError) as exc_info:
            ProjectPartialUpdate(**project_partial_update_data)

        assert_validation_error(
            exc_info,
            expected_error,
            field,
        )

    @pytest.mark.parametrize(
        "field, value",
        [
            ["name", "a" * PROJECT_NAME_MIN_LENGTH],
            ["name", "a" * PROJECT_NAME_MAX_LENGTH],
            ["description", "a" * PROJECT_DESCRIPTION_MIN_LENGTH],
            ["description", "a" * PROJECT_DESCRIPTION_MAX_LENGTH],
        ],
    )
    def test_project_partial_update_boundary_field_value(
        self,
        project_partial_update_data: dict,
        field: str,
        value: str,
    ) -> None:
        project_partial_update_data[field] = value
        project_partial_update = ProjectPartialUpdate(**project_partial_update_data)
        assert project_partial_update.model_dump() == project_partial_update_data

    @pytest.mark.parametrize(
        "field",
        ["name", "description", "visibility"],
    )
    def test_project_partial_update_without_optional_field(
        self,
        project_partial_update_data: dict,
        field: str,
    ) -> None:
        project_partial_update_data.pop(field)
        project_partial_update = ProjectPartialUpdate(**project_partial_update_data)
        assert getattr(project_partial_update, field) is None

    @pytest.mark.parametrize(
        "visibility",
        [
            "pending",
            "sent",
            "rendering",
            "completed",
        ],
    )
    def test_project_partial_update_not_valid_visibility(
        self,
        project_partial_update_data: dict,
        visibility: str,
    ) -> None:
        project_partial_update_data["visibility"] = visibility
        with pytest.raises(ValidationError) as exc_info:
            ProjectPartialUpdate(**project_partial_update_data)

        assert_validation_error(
            exc_info,
            "enum",
            "visibility",
        )
