import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from core.logging import configure_logging, get_logger
from fastapi import FastAPI
from infrastructure.kafka.consumer import consume, get_consumer
from infrastructure.kafka.producer import get_producer

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:  # noqa: ARG001
    """
    Действия до старта приложения.
    """
    configure_logging()
    consumer = await get_consumer()
    producer = await get_producer()
    await producer.start()
    asyncio.create_task(  # noqa: RUF006
        consume(consumer, producer),
    )
    logger.info("Application started")
    yield
    await consumer.stop()
    logger.info("Application has completed")
    """
    Действия при завершении работы приложения.
    """
