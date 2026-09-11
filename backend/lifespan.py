from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from core.config.application import settings
from core.logging import configure_logging, get_logger
from fastapi import FastAPI
from infrastructure.kafka.consumer import (
    KafkaConsumer,
    process_message,
)
from infrastructure.kafka.utils import deserialize_message

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:  # noqa: ARG001
    configure_logging()
    consumer = KafkaConsumer(
        settings.kafka.topic.generate_render,
        bootstrap_servers=settings.kafka.bootstrap_servers,
        group_id="backend",
        value_deserializer=deserialize_message,
    )
    await consumer.run(process_message_function=process_message)
    logger.info("Application started")
    yield
    await consumer.stop()
    logger.info("Application has completed")
