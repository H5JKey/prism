import pytest
from core.constants import BEARER_TOKEN_TYPE, FIELD_SUB
from core.exceptions.auth import InvalidPasswordError
from core.exceptions.user import (
    UserEmailAlreadyExistsError,
    UserIdNotFoundError,
    UserUsernameAlreadyExistsError,
    UserUsernameNotFoundError,
)
from core.security.jwt_tokens.utils import decode_jwt
from schemas.auth import LoginRequest, RegisterRequest
from services.auth import AuthService


@pytest.fixture(scope="function")
def register_user_data() -> RegisterRequest:
    register_user_data = RegisterRequest(
        surname="surname",
        name="name",
        username="username",
        email="email@email.com",
        password="password",
    )
    return register_user_data


class TestAuthService:
    async def test_register_valid(
        self,
        register_user_data: RegisterRequest,
        auth_service: AuthService,
    ) -> None:
        token = await auth_service.register(register_user_data)
        assert token.access_token is not None
        assert token.refresh_token is not None
        assert token.token_type == BEARER_TOKEN_TYPE

    async def test_register_not_unique_username(
        self,
        register_user_data: RegisterRequest,
        auth_service: AuthService,
    ) -> None:
        await auth_service.register(register_user_data)
        register_user_data.email = "email2@email.com"
        with pytest.raises(UserUsernameAlreadyExistsError):
            await auth_service.register(register_user_data)

    async def test_register_not_unique_email(
        self,
        register_user_data: RegisterRequest,
        auth_service: AuthService,
    ) -> None:
        await auth_service.register(register_user_data)

        register_user_data.username = "unique_username"
        with pytest.raises(UserEmailAlreadyExistsError):
            await auth_service.register(register_user_data)

    async def test_authenticate_user_valid(
        self,
        register_user_data: RegisterRequest,
        auth_service: AuthService,
    ) -> None:
        await auth_service.register(register_user_data)

        auth_user_data = LoginRequest(
            username=register_user_data.username,
            password=register_user_data.password,
        )
        token = await auth_service.authenticate_user(auth_user_data)
        assert token.access_token is not None
        assert token.refresh_token is not None
        assert token.token_type == BEARER_TOKEN_TYPE

    async def test_authenticate_username_not_exists(
        self,
        auth_service: AuthService,
    ) -> None:
        auth_user_data = LoginRequest(
            username="wrong_username",
            password="password",
        )
        with pytest.raises(UserUsernameNotFoundError):
            await auth_service.authenticate_user(auth_user_data)

    async def test_authenticate_not_valid_password(
        self,
        register_user_data: RegisterRequest,
        auth_service: AuthService,
    ) -> None:
        await auth_service.register(register_user_data)

        auth_user_data = LoginRequest(
            username=register_user_data.username,
            password="wrong_prefix_" + register_user_data.password,
        )
        with pytest.raises(InvalidPasswordError):
            await auth_service.authenticate_user(auth_user_data)

    async def test_refresh_access_token_valid(
        self,
        register_user_data: RegisterRequest,
        auth_service: AuthService,
    ) -> None:
        registration_token = await auth_service.register(register_user_data)
        payload = decode_jwt(registration_token.access_token)
        user_id = int(payload[FIELD_SUB])
        token = await auth_service.refresh_access_token(user_id)
        assert token.access_token is not None
        assert token.refresh_token is None
        assert token.token_type == BEARER_TOKEN_TYPE

    async def test_refresh_access_token_user_not_exist(
        self,
        auth_service: AuthService,
    ) -> None:
        with pytest.raises(UserIdNotFoundError):
            await auth_service.refresh_access_token(-1)
