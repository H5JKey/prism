import pytest
from pydantic import ValidationError

from core.constants import (
    PROJECT_NAME_MIN_LENGTH,
    PROJECT_NAME_MAX_LENGTH,
    PROJECT_DESCRIPTION_MAX_LENGTH,
    PROJECT_DESCRIPTION_MIN_LENGTH,
)
from schemas.project import (
    ProjectBase,
    ProjectCreate,
    ProjectWithRenderCreate,
    ProjectPartialUpdate,
    ProjectResponse,
    ProjectFullResponse,
    ProjectWithRenderFileFullResponse,
    ProjectWithRenderResponse,
    ProjectWithRenderFileResponse,
    ProjectResponseList,
)
from tests.test_schemas.helpers import assert_validation_error


@pytest.fixture
def project_base_data() -> dict:
    return {
        "name": "project_name",
        "description": "description",
        "source_file_id": 1,
    }


@pytest.fixture
def project_create_data(project_base_data: dict) -> dict:
    return {
        **project_base_data,
        "visibility": "public",
    }


@pytest.fixture
def project_with_render_create_data(
    render_create_payload_data: dict,
    project_create_data: dict,
) -> dict:
    return {
        "render": render_create_payload_data,
        "project": project_create_data,
    }


@pytest.fixture
def project_partial_update_data() -> dict:
    return {
        "name": "project_name",
        "description": "description",
        "visibility": "public",
    }


@pytest.fixture
def project_response_data(project_base_data: dict) -> dict:
    return {
        **project_base_data,
        "visibility": "public",
        "status": "rendering",
        "user_id": 1,
        "render_id": 1,
        "id": 1,
    }


@pytest.fixture
def project_full_response_data(project_response_data: dict) -> dict:
    return {
        **project_response_data,
        "url": "http://example.com",
    }


@pytest.fixture
def project_with_render_file_full_response_data(
    project_full_response_data: dict,
    render_with_file_full_response_data: dict,
) -> dict:
    return {
        **project_full_response_data,
        "render": render_with_file_full_response_data,
    }


@pytest.fixture
def project_with_render_response_data(
    project_response_data: dict,
    render_response_data: dict,
) -> dict:
    return {
        **project_response_data,
        "render": render_response_data,
    }


@pytest.fixture
def project_with_render_file_response_data(
    project_response_data: dict,
    render_with_file_response_data: dict,
) -> dict:
    return {
        **project_response_data,
        "render": render_with_file_response_data,
    }


@pytest.fixture
def project_response_list_data() -> dict:
    return {
        "project_list": [
            {
                "name": "project_name1",
                "description": "description1",
                "source_file_id": 1,
                "visibility": "public",
                "status": "rendering",
                "user_id": 1,
                "render_id": 1,
                "id": 1,
            },
            {
                "name": "project_name2",
                "description": "description2",
                "source_file_id": 2,
                "visibility": "private",
                "status": "rendering",
                "user_id": 2,
                "render_id": 2,
                "id": 2,
            },
        ],
        "size": 1,
        "page": 1,
    }


@pytest.fixture
def project_with_render_file_response_list_data() -> dict:
    return {
        "visibility": "public",
        "status": "rendering",
        "user_id": 1,
        "render_id": 1,
        "id": 1,
        "render": {
            "width": 1000,
            "height": 1000,
            "samples": 150,
            "denoiser": True,
            "gpu": False,
            "id": 1,
            "file_id": 1,
            "file": {
                "name": "file_name",
                "size": 1000,
                "id": 1,
            },
        },
    }


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
