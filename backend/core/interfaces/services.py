from abc import ABC, abstractmethod
from typing import BinaryIO

from infrastructure.database.models import Project
from schemas.file import FileResponse


class AbstractFileUploader(ABC):
    """
    Интерфейс для сервиса загрузки файлов.
    """

    @abstractmethod
    async def upload(
        self,
        file_name: str,
        file: BinaryIO,
    ) -> FileResponse:
        """
        Метод для загрузки файла.
        """


class AbstractProjectAccessValidatorService(ABC):
    """
    Интерфейс для сервиса проверки прав доступа к проекту.
    """

    @abstractmethod
    async def validate_access_to_get_project(
        self,
        project_id: int,
        user_id: int,
    ) -> Project:
        """
        Метод для проверки прав доступа на просмотр проекта.
        """

    @abstractmethod
    async def validate_access_to_change_project(
        self,
        project_id: int,
        user_id: int,
    ) -> Project:
        """
        Метод для проверки прав доступа на изменение данных проекта.
        """
