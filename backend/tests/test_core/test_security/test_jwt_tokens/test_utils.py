from typing import Any

import pytest
from core.constants import ACCESS_TOKEN_FIELD, FIELD_SUB, TOKEN_TYPE
from core.exceptions.token import InvalidTokenPayloadError
from core.security.jwt_tokens.utils import (
    decode_jwt,
    encode_jwt,
    validate_token_payload,
)


@pytest.fixture(scope="function")
def payload() -> dict:
    return {
        TOKEN_TYPE: ACCESS_TOKEN_FIELD,
        FIELD_SUB: "1",
    }


@pytest.fixture(scope="function")
def jwt_token(payload: dict[str, Any]) -> str:
    return encode_jwt(payload)


def test_can_encode_and_decode_jwt(payload: dict[str, Any]) -> None:
    payload_copy = payload.copy()
    jwt_token = encode_jwt(payload_copy)
    decode_payload = decode_jwt(jwt_token)
    for key, value in payload.items():
        assert key in decode_payload
        assert decode_payload[key] == value


def test_decoded_jwt_payload_has_iat_field(jwt_token: str) -> None:
    payload = decode_jwt(jwt_token)
    assert payload.get("iat", 0) > 0


def test_decoded_jwt_payload_has_exp_field(jwt_token: str) -> None:
    payload = decode_jwt(jwt_token)
    assert payload.get("exp", 0) > 0


def test_validate_token_payload_no_sub(payload: dict[str, str | int]) -> None:
    payload.pop("sub")
    with pytest.raises(InvalidTokenPayloadError):
        validate_token_payload(payload, target_token_type=payload[TOKEN_TYPE])


def test_validate_token_payload_invalid_data_token_type(
    payload: dict[str, str | int],
) -> None:
    with pytest.raises(InvalidTokenPayloadError):
        validate_token_payload(
            payload,
            target_token_type="wrong_token_prefix_" + payload[TOKEN_TYPE],
        )
