import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from core.exceptions.base import KafkaSendError
from core.interfaces.kafka import AbstractKafkaProducer
from core.logging import get_logger
from infrastructure.database.core import session_factory
from infrastructure.database.unit_of_work import UnitOfWork

from outbox_worker.worker import OutboxWorker

logger = get_logger(__name__)


@asynccontextmanager
async def get_outbox_worker(
    producer: AbstractKafkaProducer,
) -> AsyncGenerator[OutboxWorker]:
    async with session_factory() as session, UnitOfWork(session) as unit_of_work:
        outbox_worker = OutboxWorker(
            unit_of_work,
            producer,
        )
        yield outbox_worker


async def run_worker(producer: AbstractKafkaProducer) -> None:
    logger.info("Outbox worker started")
    delay = 5
    while True:
        try:
            async with get_outbox_worker(producer) as outbox_worker:
                await outbox_worker.process_messages()
            await asyncio.sleep(delay)
            delay = 5
        except KafkaSendError:
            error_detail = "Process message failed"
            logger.exception(error_detail)
            delay *= 2
        finally:
            await asyncio.sleep(delay)
