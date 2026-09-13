from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from core.config.application import settings
from core.logging import configure_logging, get_logger
from fastapi import FastAPI
from infrastructure.kafka.consumer import (
    KafkaConsumer,
    add_project_render,
)
from infrastructure.kafka.producer import KafkaProducer
from infrastructure.kafka.utils import deserialize_message, serialize_message

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:  # noqa: ARG001
    configure_logging()
    producer = KafkaProducer(
        bootstrap_servers=settings.kafka.bootstrap_servers,
        value_serializer=serialize_message,
    )
    await producer.start()
    consumer = KafkaConsumer(
        settings.kafka.topic.generate_render,
        bootstrap_servers=settings.kafka.bootstrap_servers,
        group_id=settings.kafka.group_id,
        value_deserializer=deserialize_message,
        auto_offset_reset="earliest",
        enable_auto_commit=False,
    )
    await consumer.run(
        process_message_function=add_project_render,
        producer=producer,
    )
    logger.info("Application started")
    yield
    await consumer.stop()
    logger.info("Application has completed")
