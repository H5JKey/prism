import pytest
from core.constants import (
    USER_EMAIL_MAX_LENGTH,
    USER_EMAIL_MIN_LENGTH,
    USER_ENCRYPTED_PASSWORD_MAX_LENGTH,
    USER_NAME_MAX_LENGTH,
    USER_NAME_MIN_LENGTH,
    USER_SURNAME_MAX_LENGTH,
    USER_SURNAME_MIN_LENGTH,
    USER_USERNAME_MAX_LENGTH,
    USER_USERNAME_MIN_LENGTH,
)
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from tests.helpers import SQLState, assert_sqlstate_code
from tests.test_infrastructure.test_database.test_models.factories import (
    create_file,
    create_project,
    create_render,
    create_user,
)


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

    async def test_user_projects_relationship_valid(
        self,
        session: AsyncSession,
    ) -> None:
        user = await create_user(session)
        file1 = await create_file(session, bucket="bucket1", key="key1")
        render1 = await create_render(session, file=file1)
        file2 = await create_file(session, bucket="bucket2", key="key2")
        render2 = await create_render(session, file=file2)
        project1 = await create_project(
            session,
            user=user,
            source_file=file1,
            render=render1,
        )
        project2 = await create_project(
            session,
            user=user,
            source_file=file2,
            render=render2,
        )
        created_projects = [project1, project2]
        created_projects.sort(key=lambda project: project.id)
        await session.refresh(user, ["projects"])
        user_projects = sorted(user.projects, key=lambda project: project.id)
        assert user_projects == created_projects
