import pytest
from core.constants import (
    USER_EMAIL_MAX_LENGTH,
    USER_NAME_MAX_LENGTH,
    USER_NAME_MIN_LENGTH,
    USER_PASSWORD_MAX_LENGTH,
    USER_PASSWORD_MIN_LENGTH,
    USER_SURNAME_MAX_LENGTH,
    USER_SURNAME_MIN_LENGTH,
    USER_USERNAME_MAX_LENGTH,
    USER_USERNAME_MIN_LENGTH,
)
from pydantic import ValidationError
from schemas.auth import RegisterRequest

from tests.test_schemas.helpers import assert_validation_error


class TestRegisterRequest:
    def test_register_request_valid(
        self,
        register_request_data: dict[str, str],
    ) -> None:
        self._assert_all_fields_correct(register_request_data)

    @pytest.mark.parametrize(
        "email, expected_error_type",
        [
            ["mail.ru", "value_error"],
            ["@mail.ru", "value_error"],
            ["mail@mail", "value_error"],
            ["mail@mail.", "value_error"],
        ],
    )
    def test_register_request_invalid_email(
        self,
        register_request_data: dict[str, str],
        email: str,
        expected_error_type: str,
    ) -> None:
        register_request_data["email"] = email
        with pytest.raises(ValidationError) as exc_info:
            RegisterRequest(**register_request_data)

        assert_validation_error(
            exc_info,
            expected_error_type,
            "email",
        )

    @pytest.mark.parametrize(
        "field, value",
        [
            [
                "surname",
                "a" * USER_SURNAME_MIN_LENGTH,
            ],
            [
                "surname",
                "a" * USER_SURNAME_MAX_LENGTH,
            ],
            [
                "name",
                "a" * USER_NAME_MIN_LENGTH,
            ],
            [
                "name",
                "a" * USER_NAME_MAX_LENGTH,
            ],
            [
                "username",
                "a" * USER_USERNAME_MIN_LENGTH,
            ],
            [
                "username",
                "a" * USER_USERNAME_MAX_LENGTH,
            ],
            [
                "email",
                "a@a.a",
            ],
            [
                "email",
                "a" * (USER_EMAIL_MAX_LENGTH - len("@a.a")) + "@a.a",
            ],
            [
                "password",
                "a" * USER_PASSWORD_MIN_LENGTH,
            ],
            [
                "password",
                "a" * USER_PASSWORD_MAX_LENGTH,
            ],
        ],
        ids=(
            "Surname has minimum length",
            "Surname has maximum length",
            "Name has minimum length",
            "Name has maximum length",
            "Username has minimum length",
            "Username has maximum length",
            "Email has minimum length",
            "Email has maximum length",
            "Password has minimum length",
            "Password has maximum length",
        ),
    )
    def test_register_request_has_boundary_length(
        self,
        register_request_data: dict[str, str],
        field: str,
        value: str,
    ) -> None:
        register_request_data[field] = value
        self._assert_all_fields_correct(register_request_data)

    @pytest.mark.parametrize(
        "invalid_field, value, expected_error_type",
        [
            [
                "surname",
                "a" * (USER_SURNAME_MIN_LENGTH - 1),
                "string_too_short",
            ],
            [
                "surname",
                "a" * (USER_SURNAME_MAX_LENGTH + 1),
                "string_too_long",
            ],
            [
                "name",
                "a" * (USER_NAME_MIN_LENGTH - 1),
                "string_too_short",
            ],
            [
                "name",
                "a" * (USER_NAME_MAX_LENGTH + 1),
                "string_too_long",
            ],
            [
                "username",
                "a" * (USER_USERNAME_MIN_LENGTH - 1),
                "string_too_short",
            ],
            [
                "username",
                "a" * (USER_USERNAME_MAX_LENGTH + 1),
                "string_too_long",
            ],
            [
                "email",
                "a" * (USER_EMAIL_MAX_LENGTH + 1) + "@gmail.com",
                "too_long",
            ],
            [
                "password",
                "a" * (USER_PASSWORD_MIN_LENGTH - 1),
                "string_too_short",
            ],
            [
                "password",
                "a" * (USER_PASSWORD_MAX_LENGTH + 1),
                "string_too_long",
            ],
        ],
        ids=(
            "Too short surname",
            "Too long surname",
            "Too short name",
            "Too long name",
            "Too short username",
            "Too long username",
            "Too long email",
            "Too short password",
            "Too long password",
        ),
    )
    def test_register_request_not_valid_length(
        self,
        register_request_data: dict[str, str],
        invalid_field: str,
        value: str,
        expected_error_type: str,
    ) -> None:
        register_request_data[invalid_field] = value
        with pytest.raises(ValidationError) as exc_info:
            RegisterRequest(**register_request_data)

        assert_validation_error(
            exc_info,
            expected_error_type,
            invalid_field,
        )

    def _assert_all_fields_correct(
        self,
        register_request_data: dict[str, str],
    ) -> None:
        register_request = RegisterRequest(**register_request_data)
        assert register_request.surname == register_request_data["surname"]
        assert register_request.name == register_request_data["name"]
        assert register_request.username == register_request_data["username"]
        assert register_request.email == register_request_data["email"]
        assert register_request.password == register_request_data["password"]
