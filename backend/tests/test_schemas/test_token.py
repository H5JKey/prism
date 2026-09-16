import pytest
from pydantic import ValidationError

from core.constants import BEARER_TOKEN_TYPE
from schemas.token import TokenInfo
from tests.test_schemas.helpers import assert_validation_error


@pytest.fixture
def token_info_data() -> dict:
    return {
        "access_token": "7f3a9c2e1b8d4f6a0e5c9b2d7a1f8e3c4b6d9a0f2e5c8b1d4a7f0e3c6b9d2a5f",
        "refresh_token": "c1e4b7a0d3f6c9b2e5a8d1f4c7b0e3a6d9f2c5b8e1a4d7f0c3b6e9a2d5f8c1b4",
        "token_type": "SAML",
    }


class TestTokenInfo:
    def test_token_info_valid(self, token_info_data: dict) -> None:
        token_info = TokenInfo(**token_info_data)
        assert token_info.model_dump() == token_info_data

    def test_token_info_access_token_required_field(
        self, token_info_data: dict
    ) -> None:
        token_info_data.pop("access_token")
        with pytest.raises(ValidationError) as exc_info:
            TokenInfo(**token_info_data)

        assert_validation_error(
            exc_info,
            "missing",
            "access_token",
        )

    def test_token_info_without_refresh_token_field(
        self, token_info_data: dict
    ) -> None:
        token_info_data.pop("refresh_token")
        token_info = TokenInfo(**token_info_data)
        assert token_info.refresh_token is None

    def test_token_info_without_token_type_field(self, token_info_data: dict) -> None:
        token_info_data.pop("token_type")
        token_info = TokenInfo(**token_info_data)
        assert token_info.token_type == BEARER_TOKEN_TYPE
