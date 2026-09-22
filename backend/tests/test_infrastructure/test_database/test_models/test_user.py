from datetime import datetime
from typing import Any

import pytest
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from core.constants import (
    USER_SURNAME_MIN_LENGTH,
    USER_SURNAME_MAX_LENGTH,
    USER_NAME_MIN_LENGTH,
    USER_NAME_MAX_LENGTH,
    USER_USERNAME_MAX_LENGTH,
    USER_USERNAME_MIN_LENGTH,
    USER_EMAIL_MIN_LENGTH,
    USER_EMAIL_MAX_LENGTH,
    USER_ENCRYPTED_PASSWORD_MAX_LENGTH,
)
from infrastructure.database.models import User
from tests.helpers import assert_sqlstate_code, SQLState


async def create_user(session: AsyncSession, **kwargs: Any) -> User:
    user_data = {
        "surname": "surname",
        "name": "name",
        "username": "username",
        "email": "email@mail.com",
        "encrypted_password": "encrypted_password",
        "registration_date": datetime(year=2025, month=12, day=31),
    }

    user = User(**user_data)
    for field, value in kwargs.items():
        setattr(user, field, value)

    session.add(user)
    await session.flush()
    return user


class TestUser:
    async def test_user_valid(self, session: AsyncSession) -> None:
        user = await create_user(session)
        assert user.id is not None

    @pytest.mark.parametrize(
        "field, value, expected_sqlstate",
        [
            ["surname", "a" * (USER_SURNAME_MIN_LENGTH - 1), SQLState.CHECK_VIOLATION],
            ["surname", "a" * (USER_SURNAME_MAX_LENGTH + 1), SQLState.STRING_TOO_LONG],
            ["name", "a" * (USER_NAME_MIN_LENGTH - 1), SQLState.CHECK_VIOLATION],
            ["name", "a" * (USER_NAME_MAX_LENGTH + 1), SQLState.STRING_TOO_LONG],
            [
                "username",
                "a" * (USER_USERNAME_MIN_LENGTH - 1),
                SQLState.CHECK_VIOLATION,
            ],
            [
                "username",
                "a" * (USER_USERNAME_MAX_LENGTH + 1),
                SQLState.STRING_TOO_LONG,
            ],
            ["email", "a" * (USER_EMAIL_MIN_LENGTH - 1), SQLState.CHECK_VIOLATION],
            ["email", "a" * (USER_EMAIL_MAX_LENGTH + 1), SQLState.STRING_TOO_LONG],
            [
                "encrypted_password",
                "a" * (USER_ENCRYPTED_PASSWORD_MAX_LENGTH + 1),
                SQLState.STRING_TOO_LONG,
            ],
        ],
    )
    async def test_user_not_valid_field_value(
        self,
        session: AsyncSession,
        field: str,
        value: str,
        expected_sqlstate: str,
    ) -> None:
        params = {field: value}
        with pytest.raises(DBAPIError) as exc_info:
            await create_user(session, **params)

        assert_sqlstate_code(exc_info, expected_sqlstate)

    @pytest.mark.parametrize(
        "field, value",
        [
            ["surname", "a" * USER_SURNAME_MIN_LENGTH],
            ["surname", "a" * USER_SURNAME_MAX_LENGTH],
            ["name", "a" * USER_NAME_MIN_LENGTH],
            ["name", "a" * USER_NAME_MAX_LENGTH],
            ["username", "a" * USER_USERNAME_MIN_LENGTH],
            ["username", "a" * USER_USERNAME_MAX_LENGTH],
            ["email", "a" * USER_EMAIL_MIN_LENGTH],
            ["email", "a" * USER_EMAIL_MAX_LENGTH],
            ["encrypted_password", "a" * USER_ENCRYPTED_PASSWORD_MAX_LENGTH],
        ],
    )
    async def test_user_boundary_field_value(
        self,
        session: AsyncSession,
        field: str,
        value: str,
    ) -> None:
        params = {field: value}
        user = await create_user(session, **params)
        assert user.id is not None

    @pytest.mark.parametrize(
        "field, value",
        [
            ["username", "username"],
            ["email", "email@mail.com"],
        ],
    )
    async def test_user_unique_constraint(
        self,
        session: AsyncSession,
        field: str,
        value: str,
    ) -> None:
        params = {field: value}
        await create_user(session, **params)
        with pytest.raises(DBAPIError) as exc_info:
            await create_user(session, **params)

        assert_sqlstate_code(exc_info, SQLState.UNIQUE_VIOLATION)

    async def test_user_default_registration_date(self, session: AsyncSession) -> None:
        user = await create_user(session, registration_date=None)
        assert user.id is not None
        assert user.registration_date is not None
