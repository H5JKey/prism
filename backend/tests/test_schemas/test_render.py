import pytest
from core.constants import (
    RENDER_HEIGHT_MAX_VALUE,
    RENDER_HEIGHT_MIN_VALUE,
    RENDER_SAMPLES_MAX_VALUE,
    RENDER_SAMPLES_MIN_VALUE,
    RENDER_WIDTH_MAX_VALUE,
    RENDER_WIDTH_MIN_VALUE,
)
from pydantic import ValidationError
from schemas.render import (
    RenderBase,
    RenderCreatePayload,
    RenderFullResponse,
    RenderResponse,
    RenderWithFileFullResponse,
    RenderWithFileResponse,
    SunInfo,
)

from tests.test_schemas.helpers import assert_validation_error


class TestSunInfo:
    def test_sun_info_valid(self, sun_info_data: dict) -> None:
        sun_info = SunInfo(**sun_info_data)
        assert sun_info.model_dump() == sun_info_data

    @pytest.mark.parametrize(
        "field, value, expected_error",
        [
            ["direction", [1.0, 1.0], "too_short"],
            ["direction", [1.0, 1.0, 1.0, 1.0], "too_long"],
            ["color", [2.0, 2.0], "too_short"],
            ["color", [2.0, 2.0, 2.0, 2.0], "too_long"],
        ],
    )
    def test_sun_info_not_valid_field_value_length(
        self,
        sun_info_data: dict,
        field: str,
        value: list[float],
        expected_error: str,
    ) -> None:
        sun_info_data[field] = value
        with pytest.raises(ValidationError) as exc_info:
            SunInfo(**sun_info_data)

        assert_validation_error(
            exc_info,
            expected_error,
            field,
        )


class TestRenderBase:
    def test_render_base_valid(self, render_base_data: dict) -> None:
        render_base = RenderBase(**render_base_data)
        assert render_base.model_dump() == render_base_data

    @pytest.mark.parametrize(
        "field, value, expected_error",
        [
            ["width", RENDER_WIDTH_MIN_VALUE - 1, "greater_than_equal"],
            ["width", RENDER_WIDTH_MAX_VALUE + 1, "less_than_equal"],
            ["height", RENDER_HEIGHT_MIN_VALUE - 1, "greater_than_equal"],
            ["height", RENDER_HEIGHT_MAX_VALUE + 1, "less_than_equal"],
            ["samples", RENDER_SAMPLES_MIN_VALUE - 1, "greater_than_equal"],
            ["samples", RENDER_SAMPLES_MAX_VALUE + 1, "less_than_equal"],
        ],
    )
    def test_render_base_not_valid_field_value(
        self,
        render_base_data: dict,
        field: str,
        value: int,
        expected_error: str,
    ) -> None:
        render_base_data[field] = value
        with pytest.raises(ValidationError) as exc_info:
            RenderBase(**render_base_data)

        assert_validation_error(
            exc_info,
            expected_error,
            field,
        )

    @pytest.mark.parametrize(
        "field, value",
        [
            ["width", RENDER_WIDTH_MIN_VALUE],
            ["width", RENDER_WIDTH_MAX_VALUE],
            ["height", RENDER_HEIGHT_MIN_VALUE],
            ["height", RENDER_HEIGHT_MAX_VALUE],
            ["samples", RENDER_SAMPLES_MIN_VALUE],
            ["samples", RENDER_SAMPLES_MAX_VALUE],
        ],
    )
    def test_render_base_boundary_field_value(
        self,
        render_base_data: dict,
        field: str,
        value: int,
    ) -> None:
        render_base_data[field] = value
        render_base = RenderBase(**render_base_data)
        assert render_base.model_dump() == render_base_data


class TestRenderCreatePayload:
    def test_render_create_payload_valid(
        self,
        render_create_payload_data: dict,
    ) -> None:
        render_create_payload = RenderCreatePayload(**render_create_payload_data)
        assert render_create_payload.model_dump() == render_create_payload_data
        assert isinstance(render_create_payload.sun, SunInfo)

    @pytest.mark.parametrize(
        "field, value, expected_error",
        [
            ["background", [1.0, 1.0], "too_short"],
            ["background", [1.0, 1.0, 1.0, 1.0], "too_long"],
        ],
    )
    def test_render_create_payload_not_valid_field_length(
        self,
        render_create_payload_data: dict,
        field: str,
        value: list[float],
        expected_error: str,
    ) -> None:
        render_create_payload_data[field] = value
        with pytest.raises(ValidationError) as exc_info:
            RenderCreatePayload(**render_create_payload_data)

        assert_validation_error(
            exc_info,
            expected_error,
            field,
        )

    def test_render_create_payload_needs_sun_field(
        self,
        render_create_payload_data: dict,
    ) -> None:
        render_create_payload_data.pop("sun")
        with pytest.raises(ValidationError) as exc_info:
            RenderCreatePayload(**render_create_payload_data)

        assert_validation_error(
            exc_info,
            "missing",
            "sun",
        )


class TestRenderResponse:
    def test_render_response_valid(self, render_response_data: dict) -> None:
        render_response = RenderResponse(**render_response_data)
        assert render_response.model_dump() == render_response_data

    def test_render_response_without_file_id(
        self,
        render_response_data: dict,
    ) -> None:
        render_response_data.pop("file_id")
        render_response = RenderResponse(**render_response_data)
        assert render_response.file_id is None


class TestRenderWithFileResponse:
    def test_render_with_file_response_valid(
        self,
        render_with_file_response_data: dict,
    ) -> None:
        render_with_file_response = RenderWithFileResponse(
            **render_with_file_response_data,
        )
        assert render_with_file_response.model_dump() == render_with_file_response_data

    def test_render_with_file_response_without_file_field(
        self,
        render_with_file_response_data: dict,
    ) -> None:
        render_with_file_response_data.pop("file")
        render_with_file_response = RenderWithFileResponse(
            **render_with_file_response_data,
        )
        assert render_with_file_response.file is None


class TestRenderFullResponse:
    def test_render_full_response_valid(
        self,
        render_full_response_data: dict,
    ) -> None:
        render_full_response = RenderFullResponse(**render_full_response_data)
        assert render_full_response.model_dump() == render_full_response_data

    def test_render_full_response_without_url_field(
        self,
        render_full_response_data: dict,
    ) -> None:
        render_full_response_data.pop("url")
        render_full_response = RenderFullResponse(**render_full_response_data)
        assert render_full_response.url is None


class TestRenderWithFileFullResponse:
    def test_render_with_file_full_response_valid(
        self,
        render_with_file_full_response_data: dict,
    ) -> None:
        render_with_file_full_response = RenderWithFileFullResponse(
            **render_with_file_full_response_data,
        )
        assert (
            render_with_file_full_response.model_dump()
            == render_with_file_full_response_data
        )

    def test_render_with_file_full_response_without_file_field(
        self,
        render_with_file_full_response_data: dict,
    ) -> None:
        render_with_file_full_response_data.pop("file")
        render_with_file_full_response = RenderWithFileFullResponse(
            **render_with_file_full_response_data,
        )
        assert render_with_file_full_response.file is None
