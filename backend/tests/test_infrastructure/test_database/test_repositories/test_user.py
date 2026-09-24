from typing import cast

from infrastructure.database.repositories import UserRepository
from pydantic import EmailStr
from schemas.user import UserCreate, UserUpdate
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_infrastructure.test_database.test_models.factories import create_user


class TestUserRepository:
    async def test_get_by_id(
        self,
        session: AsyncSession,
        user_repository: UserRepository,
    ) -> None:
        user = await create_user(session)
        session.expunge(user)
        selected_user = await user_repository.get_by_id(user.id)
        assert selected_user.id == user.id
        assert selected_user.surname == user.surname
        assert selected_user.name == user.name
        assert selected_user.username == user.username
        assert selected_user.email == user.email
        assert selected_user.encrypted_password == user.encrypted_password

    async def test_get_by_id_not_exists(
        self,
        user_repository: UserRepository,
    ) -> None:
        selected_user = await user_repository.get_by_id(-1)
        assert selected_user is None

    async def test_get_by_email(
        self,
        session: AsyncSession,
        user_repository: UserRepository,
    ) -> None:
        user = await create_user(session)
        session.expunge(user)
        email = cast(EmailStr, user.email)
        selected_user = await user_repository.get_by_email(email)
        assert selected_user.id == user.id
        assert selected_user.surname == user.surname
        assert selected_user.name == user.name
        assert selected_user.username == user.username
        assert selected_user.email == user.email
        assert selected_user.encrypted_password == user.encrypted_password

    async def test_get_by_email_not_exists(
        self,
        user_repository: UserRepository,
    ) -> None:
        selected_user = await user_repository.get_by_email("bot_exists_email@mail.ru")
        assert selected_user is None

    async def test_get_by_username(
        self,
        session: AsyncSession,
        user_repository: UserRepository,
    ) -> None:
        user = await create_user(session)
        session.expunge(user)
        selected_user = await user_repository.get_by_username(user.username)
        assert selected_user.id == user.id
        assert selected_user.surname == user.surname
        assert selected_user.name == user.name
        assert selected_user.username == user.username
        assert selected_user.email == user.email
        assert selected_user.encrypted_password == user.encrypted_password

    async def test_get_by_username_not_exists(
        self,
        user_repository: UserRepository,
    ) -> None:
        selected_user = await user_repository.get_by_username("not_exists_username")
        assert selected_user is None

    async def test_create_user(
        self,
        session: AsyncSession,
        user_repository: UserRepository,
    ) -> None:
        user_create_data = UserCreate(
            surname="surname",
            name="name",
            username="username",
            email="email@email.com",
            encrypted_password="encrypted_password",  # noqa: S106
        )
        created_user = await user_repository.create_user(user_create_data)
        session.expunge(created_user)
        selected_user = await user_repository.get_by_id(created_user.id)
        assert selected_user.id is not None
        assert selected_user.surname == user_create_data.surname
        assert selected_user.name == user_create_data.name
        assert selected_user.username == user_create_data.username
        assert selected_user.email == user_create_data.email
        assert selected_user.encrypted_password == user_create_data.encrypted_password

    async def test_update_user(
        self,
        session: AsyncSession,
        user_repository: UserRepository,
    ) -> None:
        user = await create_user(session)
        updated_user_data = UserUpdate(
            surname="updated_surname",
            name="updated_name",
            username="updated_username",
            email="updated_email@email.com",
        )
        await user_repository.update_user(user.id, updated_user_data)
        session.expunge(user)
        selected_user = await user_repository.get_by_id(user.id)
        assert selected_user.id is not None
        assert selected_user.surname == updated_user_data.surname
        assert selected_user.name == updated_user_data.name
        assert selected_user.username == updated_user_data.username
        assert selected_user.email == updated_user_data.email
        assert selected_user.encrypted_password == user.encrypted_password

    async def test_delete_by_id(
        self,
        session: AsyncSession,
        user_repository: UserRepository,
    ) -> None:
        user = await create_user(session)
        await user_repository.delete_by_id(user.id)
        session.expunge(user)
        selected_user = await user_repository.get_by_id(user.id)
        assert selected_user is None
