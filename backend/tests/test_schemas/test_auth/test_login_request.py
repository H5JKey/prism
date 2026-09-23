import pytest
from core.constants import (
    USER_PASSWORD_MAX_LENGTH,
    USER_PASSWORD_MIN_LENGTH,
    USER_USERNAME_MAX_LENGTH,
    USER_USERNAME_MIN_LENGTH,
)
from pydantic import ValidationError
from schemas.auth import LoginRequest

from tests.test_schemas.helpers import assert_validation_error


class TestLoginRequest:
    def test_login_request_valid(
        self,
        login_request_data: dict[str, str],
    ) -> None:
        login_request = LoginRequest(**login_request_data)
        assert login_request.username == login_request_data["username"]
        assert login_request.password == login_request_data["password"]

    @pytest.mark.parametrize(
        "username",
        [
            "a" * USER_USERNAME_MIN_LENGTH,
            "a" * USER_USERNAME_MAX_LENGTH,
        ],
        ids=(
            "Username has minimum length",
            "Username has maximum length",
        ),
    )
    def test_login_request_has_boundaries_username_length(
        self,
        login_request_data: dict[str, str],
        username: str,
    ) -> None:
        login_request_data["username"] = username
        login_request = LoginRequest(**login_request_data)
        assert login_request.username == login_request_data["username"]
        assert login_request.password == login_request_data["password"]

    @pytest.mark.parametrize(
        "username, expected_error_type",
        [
            ["a" * (USER_USERNAME_MIN_LENGTH - 1), "string_too_short"],
            ["a" * (USER_USERNAME_MAX_LENGTH + 1), "string_too_long"],
        ],
        ids=(
            "Too short username",
            "Too long username",
        ),
    )
    def test_login_request_not_valid_username(
        self,
        login_request_data: dict[str, str],
        username: str,
        expected_error_type: str,
    ) -> None:
        login_request_data["username"] = username
        with pytest.raises(ValidationError) as exc_info:
            LoginRequest(**login_request_data)

        assert_validation_error(
            exc_info,
            expected_error_type,
            "username",
        )

    @pytest.mark.parametrize(
        "password",
        [
            "a" * USER_PASSWORD_MIN_LENGTH,
            "a" * USER_PASSWORD_MAX_LENGTH,
        ],
        ids=(
            "Password has minimum length",
            "Password has maximum length",
        ),
    )
    def test_login_request_has_boundaries_password_length(
        self,
        login_request_data: dict[str, str],
        password: str,
    ) -> None:
        login_request_data["password"] = password
        login_request = LoginRequest(**login_request_data)
        assert login_request.username == login_request_data["username"]
        assert login_request.password == login_request_data["password"]

    @pytest.mark.parametrize(
        "password, expected_error_type",
        [
            [
                "a" * (USER_PASSWORD_MIN_LENGTH - 1),
                "string_too_short",
            ],
            [
                "a" * (USER_PASSWORD_MAX_LENGTH + 1),
                "string_too_long",
            ],
        ],
        ids=(
            "Too short password",
            "Too long password",
        ),
    )
    def test_login_request_not_valid_password_length(
        self,
        login_request_data: dict[str, str],
        password: str,
        expected_error_type: str,
    ) -> None:
        login_request_data["password"] = password
        with pytest.raises(ValidationError) as exc_info:
            LoginRequest(**login_request_data)

        assert_validation_error(
            exc_info,
            expected_error_type,
            "password",
        )
