from datetime import datetime

import pytest
from core.exceptions.user import UserIdNotFoundError
from infrastructure.database.models import User
from pytest_mock import MockerFixture
from schemas.user import UserUpdate
from services.user import UserService


@pytest.fixture(scope="function")
def user() -> User:
    user = User(
        id=1,
        surname="surname",
        name="name",
        username="username",
        email="email@mail.com",
        encrypted_password="encrypted_password",
        registration_date=datetime(year=2025, month=12, day=31),
    )
    return user


class TestUserService:
    async def test_get_profile_by_id_valid(
        self,
        user: User,
        mocker: MockerFixture,
        user_service: UserService,
    ) -> None:
        mocker.patch.object(
            user_service.user_repository,
            "get_by_id",
            autospec=True,
            return_value=user,
        )
        user_full_response = await user_service.get_profile_by_id(user.id)
        assert user_full_response.id == user.id
        assert user_full_response.surname == user.surname
        assert user_full_response.name == user.name
        assert user_full_response.username == user.username
        assert user_full_response.registration_date == user.registration_date
        assert user_full_response.email == user.email

    async def test_get_profile_by_id_user_not_exist(
        self,
        mocker: MockerFixture,
        user_service: UserService,
    ) -> None:
        mocker.patch.object(
            user_service.user_repository,
            "get_by_id",
            autospec=True,
            return_value=None,
        )
        with pytest.raises(UserIdNotFoundError):
            await user_service.get_profile_by_id(-1)

    async def test_get_by_id_valid(
        self,
        user: User,
        mocker: MockerFixture,
        user_service: UserService,
    ) -> None:
        mocker.patch.object(
            user_service.user_repository,
            "get_by_id",
            autospec=True,
            return_value=user,
        )
        user_response = await user_service.get_by_id(user.id)
        assert user_response.id == user.id
        assert user_response.surname == user.surname
        assert user_response.name == user.name
        assert user_response.username == user.username
        assert user_response.registration_date == user.registration_date
        assert getattr(user_response, "email", None) is None

    async def test_get_by_id_user_not_exist(
        self,
        mocker: MockerFixture,
        user_service: UserService,
    ) -> None:
        mocker.patch.object(
            user_service.user_repository,
            "get_by_id",
            autospec=True,
            return_value=None,
        )
        with pytest.raises(UserIdNotFoundError):
            await user_service.get_by_id(-1)

    async def test_update_user_not_exist(
        self,
        mocker: MockerFixture,
        user_service: UserService,
    ) -> None:
        mocker.patch.object(
            user_service,
            "get_by_id",
            autospec=True,
            return_value=None,
        )

        update_user_data = UserUpdate(
            surname="updated_surname",
            name="updated_name",
            username="updated_username",
            email="updated_email@email.com",
        )
        with pytest.raises(UserIdNotFoundError):
            await user_service.update_user(-1, update_user_data)

    async def test_delete_not_exist(
        self,
        mocker: MockerFixture,
        user_service: UserService,
    ) -> None:
        mocker.patch.object(
            user_service,
            "get_by_id",
            autospec=True,
            return_value=None,
        )
        with pytest.raises(UserIdNotFoundError):
            await user_service.delete_by_id(-1)
