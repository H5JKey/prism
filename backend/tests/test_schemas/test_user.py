from datetime import UTC, datetime

import pytest
from core.constants import (
    USER_EMAIL_MAX_LENGTH,
    USER_ENCRYPTED_PASSWORD_MAX_LENGTH,
    USER_NAME_MAX_LENGTH,
    USER_NAME_MIN_LENGTH,
    USER_SURNAME_MAX_LENGTH,
    USER_SURNAME_MIN_LENGTH,
    USER_USERNAME_MAX_LENGTH,
    USER_USERNAME_MIN_LENGTH,
)
from pydantic import ValidationError
from schemas.user import (
    UserBase,
    UserCreate,
    UserFullResponse,
    UserResponse,
    UserUpdate,
)

from tests.test_schemas.helpers import assert_validation_error


@pytest.fixture
def user_base_data() -> dict:
    return {
        "surname": "Turner",
        "name": "Harry",
        "username": "user_harry",
    }


@pytest.fixture
def user_create_data(user_base_data: dict) -> dict:
    return {
        **user_base_data,
        "email": "test_email@gmail.com",
        "encrypted_password": "encrypted_password_value",
    }


@pytest.fixture
def user_update_data(user_base_data: dict) -> dict:
    return {
        **user_base_data,
        "email": "test_email@gmail.com",
    }


@pytest.fixture
def user_response_data(user_base_data: dict) -> dict:
    return {
        **user_base_data,
        "id": 1,
        "registration_date": datetime(2025, 6, 30, tzinfo=UTC),
    }


@pytest.fixture
def user_full_response_data(user_response_data: dict) -> dict:
    return {
        **user_response_data,
        "email": "test_email@gmail.com",
    }


class TestUserBase:
    def test_user_base_valid(self, user_base_data: dict) -> None:
        user_base = UserBase(**user_base_data)
        assert user_base.model_dump() == user_base_data

    @pytest.mark.parametrize(
        "field, value, expected_error",
        [
            ["surname", "a" * (USER_SURNAME_MIN_LENGTH - 1), "string_too_short"],
            ["surname", "a" * (USER_SURNAME_MAX_LENGTH + 1), "string_too_long"],
            ["name", "a" * (USER_NAME_MIN_LENGTH - 1), "string_too_short"],
            ["name", "a" * (USER_NAME_MAX_LENGTH + 1), "string_too_long"],
            ["username", "a" * (USER_USERNAME_MIN_LENGTH - 1), "string_too_short"],
            ["username", "a" * (USER_USERNAME_MAX_LENGTH + 1), "string_too_long"],
        ],
    )
    def test_user_base_not_valid_field_value(
        self,
        user_base_data: dict,
        field: str,
        value: str,
        expected_error: str,
    ) -> None:
        user_base_data[field] = value
        with pytest.raises(ValidationError) as exc_info:
            UserBase(**user_base_data)

        assert_validation_error(
            exc_info,
            expected_error,
            field,
        )

    @pytest.mark.parametrize(
        "field, value",
        [
            ["surname", "a" * USER_SURNAME_MIN_LENGTH],
            ["surname", "a" * USER_SURNAME_MAX_LENGTH],
            ["name", "a" * USER_NAME_MIN_LENGTH],
            ["name", "a" * USER_NAME_MAX_LENGTH],
            ["username", "a" * USER_USERNAME_MIN_LENGTH],
            ["username", "a" * USER_USERNAME_MAX_LENGTH],
        ],
    )
    def test_user_base_boundary_field_value(
        self,
        user_base_data: dict,
        field: str,
        value: str,
    ) -> None:
        user_base_data[field] = value
        user_base = UserBase(**user_base_data)
        assert user_base.model_dump() == user_base_data


class TestUserCreate:
    def test_user_create_valid(self, user_create_data: dict) -> None:
        user_create = UserCreate(**user_create_data)
        assert user_create.model_dump() == user_create_data

    @pytest.mark.parametrize(
        "field, value, expected_error",
        [
            ["email", "a" * (USER_EMAIL_MAX_LENGTH + 1) + "@mail.ru", "too_long"],
            [
                "encrypted_password",
                "a" * (USER_ENCRYPTED_PASSWORD_MAX_LENGTH + 1),
                "string_too_long",
            ],
        ],
    )
    def test_user_create_not_valid_field_value(
        self,
        user_create_data: dict,
        field: str,
        value: str,
        expected_error: str,
    ) -> None:
        user_create_data[field] = value
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_create_data)

        assert_validation_error(
            exc_info,
            expected_error,
            field,
        )

    @pytest.mark.parametrize(
        "field, value",
        [
            ["surname", "a" * USER_SURNAME_MIN_LENGTH],
            ["surname", "a" * USER_SURNAME_MAX_LENGTH],
            ["name", "a" * USER_NAME_MIN_LENGTH],
            ["name", "a" * USER_NAME_MAX_LENGTH],
            ["username", "a" * USER_USERNAME_MIN_LENGTH],
            ["username", "a" * USER_USERNAME_MAX_LENGTH],
        ],
    )
    def test_user_create_boundary_field_value(
        self,
        user_create_data: dict,
        field: str,
        value: str,
    ) -> None:
        user_create_data[field] = value
        user_create = UserCreate(**user_create_data)
        assert user_create.model_dump() == user_create_data


class TestUserUpdate:
    def test_user_update_valid(self, user_update_data: dict) -> None:
        user_update = UserUpdate(**user_update_data)
        assert user_update.model_dump() == user_update_data

    @pytest.mark.parametrize(
        "value, expected_error",
        [
            ["a" * (USER_EMAIL_MAX_LENGTH + 1) + "@mail.ru", "too_long"],
            ["mail.ru", "value_error"],
            ["@mail.ru", "value_error"],
            ["mail@mail", "value_error"],
            ["mail@mail.", "value_error"],
        ],
    )
    def test_user_update_not_valid_email(
        self,
        user_update_data: dict,
        value: str,
        expected_error: str,
    ) -> None:
        user_update_data["email"] = value
        with pytest.raises(ValidationError) as exc_info:
            UserUpdate(**user_update_data)

        assert_validation_error(
            exc_info,
            expected_error,
            "email",
        )

    def test_user_update_boundary_email_length(
        self,
        user_update_data: dict,
    ) -> None:
        user_update_data["email"] = (
            "a" * (USER_EMAIL_MAX_LENGTH - len("@mail.com")) + "@mail.com"
        )
        user_update = UserUpdate(**user_update_data)
        assert user_update.model_dump() == user_update_data


class TestUserResponse:
    def test_user_response_valid(self, user_response_data: dict) -> None:
        user_response = UserResponse(**user_response_data)
        assert user_response.model_dump() == user_response_data

    @pytest.mark.parametrize(
        "field",
        [
            "id",
            "registration_date",
        ],
    )
    def test_user_response_without_required_field(
        self,
        user_response_data: dict,
        field: str,
    ) -> None:
        user_response_data.pop(field)
        with pytest.raises(ValidationError) as exc_info:
            UserResponse(**user_response_data)

        assert_validation_error(
            exc_info,
            "missing",
            field,
        )


class TestUserFullResponse:
    def test_user_full_response_valid(self, user_full_response_data: dict) -> None:
        user_full_response = UserFullResponse(**user_full_response_data)
        assert user_full_response.model_dump() == user_full_response_data

    @pytest.mark.parametrize(
        "value, expected_error",
        [
            ["a" * (USER_EMAIL_MAX_LENGTH + 1) + "@mail.ru", "too_long"],
            ["mail.ru", "value_error"],
            ["@mail.ru", "value_error"],
            ["mail@mail", "value_error"],
            ["mail@mail.", "value_error"],
        ],
    )
    def test_user_full_response_not_valid_email(
        self,
        user_full_response_data: dict,
        value: str,
        expected_error: str,
    ) -> None:
        user_full_response_data["email"] = value
        with pytest.raises(ValidationError) as exc_info:
            UserFullResponse(**user_full_response_data)

        assert_validation_error(
            exc_info,
            expected_error,
            "email",
        )

    def test_user_full_response_boundary_email_length(
        self,
        user_full_response_data: dict,
    ) -> None:
        user_full_response_data["email"] = (
            "a" * (USER_EMAIL_MAX_LENGTH - len("@mail.com")) + "@mail.com"
        )
        user_full_response = UserFullResponse(**user_full_response_data)
        assert user_full_response.model_dump() == user_full_response_data
