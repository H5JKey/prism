import pytest
from pydantic import ValidationError

from core.constants import (
    PROJECT_NAME_MIN_LENGTH,
    PROJECT_NAME_MAX_LENGTH,
    PROJECT_DESCRIPTION_MAX_LENGTH,
    PROJECT_DESCRIPTION_MIN_LENGTH,
)
from schemas.project import ProjectBase
from tests.test_schemas.helpers import assert_validation_error


class TestProjectBase:
    def test_project_base_valid(self, project_base_data: dict) -> None:
        project_base = ProjectBase(**project_base_data)
        assert project_base.model_dump() == project_base_data

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
    def test_project_base_not_valid_field_value(
        self,
        project_base_data: dict,
        field: str,
        value: str,
        expected_error: str,
    ) -> None:
        project_base_data[field] = value
        with pytest.raises(ValidationError) as exc_info:
            ProjectBase(**project_base_data)

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
    def test_project_base_boundary_field_value(
        self,
        project_base_data: dict,
        field: str,
        value: str,
    ) -> None:
        project_base_data[field] = value
        project_base = ProjectBase(**project_base_data)
        assert project_base.model_dump() == project_base_data
