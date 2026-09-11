import asyncio
from asyncio import CancelledError, Task
from collections.abc import Callable
from typing import Any

from aiokafka import AIOKafkaConsumer, ConsumerRecord
from core.config.application import settings
from core.constants import KAFKA_CONNECTION_ERROR
from core.logging import get_logger
from schemas.event import AddRenderProjectEvent
from services.project import ProjectService

from infrastructure.database.core import session_factory
from infrastructure.database.unit_of_work import UnitOfWork
from infrastructure.minio.client import MinioClient
from infrastructure.minio.session import get_minio_session

logger = get_logger(__name__)


class KafkaConsumer:
    def __init__(
        self,
        *topics: str,
        **kwargs: Any,
    ) -> None:
        self._consumer: AIOKafkaConsumer | None = None
        self._task: Task[Any] | None = None
        self.topics = topics
        self.kwargs = kwargs

    async def _start(self) -> None:
        self._consumer = AIOKafkaConsumer(*self.topics, **self.kwargs)
        await self._consumer.start()
        logger.info("Kafka consumer started")

    async def _run(self, process_message_function: Callable[..., Any]) -> None:
        delay = 1
        while True:
            try:
                await self._start()
                assert self._consumer is not None
                async for message in self._consumer:
                    await process_message_function(message)
                    await self._consumer.commit()
                    delay = 1
            except KAFKA_CONNECTION_ERROR:
                logger.exception("Kafka consumer connection error")
                await asyncio.sleep(delay)
                delay *= 2
            except Exception:
                logger.exception(
                    "Failed to process message by kafka consumer",
                )
            finally:
                if self._consumer is not None:
                    await self._consumer.stop()
                    self._consumer = None

    async def run(self, process_message_function: Callable[..., Any]) -> None:
        self._task = asyncio.create_task(self._run(process_message_function))

    async def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except CancelledError:
                logger.exception("Kafka consumer task cancelled")
            except Exception:
                logger.exception("Cancellation of the Kafka consumer task failed")
            self._task = None

        if self._consumer is not None:
            await self._consumer.stop()
            self._consumer = None


async def process_message(message: ConsumerRecord) -> None:
    json_data = message.value
    add_render_project_event = AddRenderProjectEvent.model_validate(
        json_data,
    )
    logger.info("Received message, %s", add_render_project_event)
    project_id = add_render_project_event.project_id
    minio_session = get_minio_session()
    async with (
        session_factory() as session,
        UnitOfWork(session) as unit_of_work,
        ProjectService(unit_of_work) as project_service,
        minio_session.create_client(
            "s3",
            **settings.minio.config,
        ) as client,
        MinioClient(client) as s3_client,
    ):
        await project_service.update_project_status(project_id)
        await project_service.add_render_to_project(
            add_render_project_event,
            s3_client,
        )
