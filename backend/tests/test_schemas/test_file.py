import pytest
from pydantic import ValidationError

from core.constants import (
    FILE_NAME_MIN_LENGTH,
    FILE_NAME_MAX_LENGTH,
    FILE_SIZE_MIN_VALUE_BYTES,
    FILE_SIZE_MAX_VALUE_BYTES,
    FILE_BUCKET_MAX_LENGTH,
    FILE_KEY_MAX_LENGTH,
)
from schemas.file import FileBase, FileResponse, FileCreate, FileLocationCreate
from tests.test_schemas.helpers import assert_validation_error


@pytest.fixture
def file_base_data() -> dict:
    return {
        "name": "file_name",
        "size": 1000,
    }


@pytest.fixture
def file_create_data(file_base_data: dict, file_location_data: dict) -> dict:
    data = {**file_base_data, **file_location_data}
    return data


@pytest.fixture
def file_response_data(file_base_data: dict) -> dict:
    file_base_data["id"] = 1
    return file_base_data


class TestFileBase:
    def test_file_base_valid(self, file_base_data: dict) -> None:
        file_base = FileBase(**file_base_data)
        assert file_base.model_dump() == file_base_data

    @pytest.mark.parametrize(
        "field, value, expected_error",
        [
            ("name", "a" * (FILE_NAME_MIN_LENGTH - 1), "string_too_short"),
            ("name", "a" * (FILE_NAME_MAX_LENGTH + 1), "string_too_long"),
            ("size", FILE_SIZE_MIN_VALUE_BYTES - 1, "greater_than"),
            ("size", FILE_SIZE_MAX_VALUE_BYTES + 1, "less_than_equal"),
        ],
    )
    def test_file_base_not_valid_field_value(
        self,
        file_base_data: dict,
        field: str,
        value: str,
        expected_error: str,
    ) -> None:
        file_base_data[field] = value
        with pytest.raises(ValidationError) as exc_info:
            FileBase(**file_base_data)

        assert_validation_error(
            exc_info,
            expected_error,
            field,
        )

    @pytest.mark.parametrize(
        "field, value",
        [
            ("name", "a" * FILE_NAME_MIN_LENGTH),
            ("name", "a" * FILE_NAME_MAX_LENGTH),
            ("size", FILE_SIZE_MIN_VALUE_BYTES + 1),
            ("size", FILE_SIZE_MAX_VALUE_BYTES),
        ],
    )
    def test_file_base_boundary_field_value(
        self,
        file_base_data: dict,
        field: str,
        value: str,
    ) -> None:
        file_base_data[field] = value
        file_base = FileBase(**file_base_data)
        assert file_base.model_dump() == file_base_data


class TestFileLocationCreate:
    def test_file_location_create_valid(self, file_location_data: dict) -> None:
        file_location_create = FileLocationCreate(**file_location_data)
        assert file_location_create.model_dump() == file_location_data

    @pytest.mark.parametrize(
        "field, value, expected_error",
        [
            ("bucket", "a" * (FILE_BUCKET_MAX_LENGTH + 1), "string_too_long"),
            ("key", "a" * (FILE_KEY_MAX_LENGTH + 1), "string_too_long"),
        ],
    )
    def test_file_location_create_not_valid_field_value(
        self,
        file_location_data: dict,
        field: str,
        value: str,
        expected_error: str,
    ) -> None:
        file_location_data[field] = value
        with pytest.raises(ValidationError) as exc_info:
            FileLocationCreate(**file_location_data)

        assert_validation_error(
            exc_info,
            expected_error,
            field,
        )

    @pytest.mark.parametrize(
        "field, value",
        [
            ("key", "a" * FILE_KEY_MAX_LENGTH),
            ("bucket", "a" * FILE_BUCKET_MAX_LENGTH),
        ],
    )
    def test_file_location_create_field_value(
        self,
        file_location_data: dict,
        field: str,
        value: str,
    ) -> None:
        file_location_data[field] = value
        file_location_create = FileLocationCreate(**file_location_data)
        assert file_location_create.model_dump() == file_location_data


class TestFileCreate:
    def test_file_create_valid(self, file_create_data: dict) -> None:
        file_create = FileCreate(**file_create_data)
        assert isinstance(file_create, FileBase)
        assert isinstance(file_create, FileLocationCreate)
        assert file_create.model_dump() == file_create_data


class TestFileResponse:
    def test_file_response_valid(self, file_response_data: dict) -> None:
        file_response = FileResponse(**file_response_data)
        assert file_response.model_dump() == file_response_data

    def test_file_response_id_required(self, file_response_data: dict) -> None:
        file_response_data.pop("id")
        with pytest.raises(ValidationError) as exc_info:
            FileResponse(**file_response_data)

        assert_validation_error(
            exc_info,
            "missing",
            "id",
        )
