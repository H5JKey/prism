from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any


class AbstractKafkaConsumer(ABC):
    """
    Интерфейс для работы с кафка консюмером.
    """

    @abstractmethod
    async def run(self, process_message_function: Callable[..., Any]) -> None:
        """
        Метод для запуска кафка консюмера.
        """

    @abstractmethod
    async def stop(self) -> None:
        """
        Метод для остановки кафка консюмера.
        """


class AbstractKafkaProducer(ABC):
    """
    Интерфейс для работы с кафка продюсером.
    """

    @abstractmethod
    async def start(self) -> None:
        """
        Метод для запуска кафка продюсера.
        """

    @abstractmethod
    async def stop(self) -> None:
        """
        Метод для остановки кафка продюсера.
        """

    @abstractmethod
    async def send(
        self,
        topic: str,
        value: Any | None = None,
        key: Any | None = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
    ) -> None:
        """
        Метод для отправки сообщения кафка продюсером.
        """
