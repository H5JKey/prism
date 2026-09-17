import pytest
from pydantic import ValidationError

from core.constants import TAG_MIN_LENGTH, TAG_MAX_LENGTH
from schemas.tag import TagBase, TagResponse, TagResponseList
from tests.test_schemas.helpers import assert_validation_error


@pytest.fixture
def tag_base_data() -> dict:
    return {
        "project_id": 1,
        "name": "tag_name",
    }


@pytest.fixture
def tag_response_data(tag_base_data: dict) -> dict:
    return {**tag_base_data, "id": 1}


@pytest.fixture
def tag_response_list_data() -> dict:
    return {
        "tag_list": [
            {
                "id": 1,
                "project_id": 1,
                "name": "tag_name1",
            },
            {
                "id": 2,
                "project_id": 2,
                "name": "tag_name2",
            },
        ]
    }


class TestTagBase:
    def test_tag_base_valid(self, tag_base_data: dict) -> None:
        tag_base = TagBase(**tag_base_data)
        assert tag_base.model_dump() == tag_base_data

    @pytest.mark.parametrize(
        "name, expected_error",
        [
            ["a" * (TAG_MIN_LENGTH - 1), "string_too_short"],
            ["a" * (TAG_MAX_LENGTH + 1), "string_too_long"],
        ],
    )
    def test_tag_base_name_field(
        self,
        tag_base_data: dict,
        name: str,
        expected_error: str,
    ) -> None:
        tag_base_data["name"] = name
        with pytest.raises(ValidationError) as exc_info:
            TagBase(**tag_base_data)

        assert_validation_error(
            exc_info,
            expected_error,
            "name",
        )


class TestTagResponse:
    def test_tag_response_valid(self, tag_response_data: dict) -> None:
        tag_response = TagResponse(**tag_response_data)
        assert tag_response.model_dump() == tag_response_data

    @pytest.mark.parametrize(
        "field",
        ["id"],
    )
    def test_tag_response_without_required_field(
        self,
        tag_response_data: dict,
        field: str,
    ) -> None:
        tag_response_data.pop(field)
        with pytest.raises(ValidationError) as exc_info:
            TagResponse(**tag_response_data)

        assert_validation_error(
            exc_info,
            "missing",
            field,
        )


class TestTagResponseList:
    def test_tag_response_list_valid(self, tag_response_list_data: dict) -> None:
        tag_response_list = TagResponseList(**tag_response_list_data)
        assert tag_response_list.model_dump() == tag_response_list_data

    @pytest.mark.parametrize(
        "field",
        ["tag_list"],
    )
    def test_tag_response_list_without_required_field(
        self,
        tag_response_list_data: dict,
        field: str,
    ) -> None:
        tag_response_list_data.pop(field)
        with pytest.raises(ValidationError) as exc_info:
            TagResponseList(**tag_response_list_data)

        assert_validation_error(
            exc_info,
            "missing",
            field,
        )
