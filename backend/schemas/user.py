from datetime import datetime
from typing import ClassVar, Self

from core.security.password_utils import hash_password
from pydantic import BaseModel, ConfigDict

from schemas.auth import RegisterRequest
from schemas.constraints.user import (
    EmailConstraint,
    EncryptedPasswordConstraint,
    NameConstraint,
    SurnameConstraint,
    UsernameConstraint,
)


class UserBase(BaseModel):
    """
    Базовая схема для пользователя.
    """

    surname: SurnameConstraint
    name: NameConstraint
    username: UsernameConstraint

    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    """
    Схема для создания пользователя.
    """

    email: EmailConstraint
    encrypted_password: EncryptedPasswordConstraint

    @classmethod
    def get_from_register_request(cls, register_user_data: RegisterRequest) -> Self:
        password = register_user_data.password
        encrypted_password = hash_password(password)
        register_user_data_dict = register_user_data.model_dump(
            exclude={"password"},
        )
        create_user_data = cls(
            encrypted_password=encrypted_password,
            **register_user_data_dict,
        )
        return create_user_data


class UserUpdate(UserBase):
    """
    Схема для обновления данных о пользователе.
    """

    email: EmailConstraint


class UserResponse(UserBase):
    """
    Схема для вывода информации о пользователе,
    которая будет видна другим пользователям.
    """

    id: int
    registration_date: datetime


class UserFullResponse(UserResponse):
    """
    Схема для вывода информации о пользователе.
    """

    email: EmailConstraint
