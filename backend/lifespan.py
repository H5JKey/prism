from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from core.config.application import settings
from core.logging import get_logger
from fastapi import FastAPI
from infrastructure.kafka.consumer import (
    KafkaConsumer,
    consume_render_generated,
)
from infrastructure.kafka.producer import KafkaProducer
from infrastructure.kafka.utils import deserialize_message, serialize_message

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:  # noqa: ARG001
    producer = KafkaProducer(
        bootstrap_servers=settings.kafka.bootstrap_servers,
        value_serializer=serialize_message,
    )
    await producer.start()
    consumer = KafkaConsumer(
        settings.kafka.topic.render_generated,
        bootstrap_servers=settings.kafka.bootstrap_servers,
        group_id=settings.kafka.group_id,
        value_deserializer=deserialize_message,
        auto_offset_reset="earliest",
        enable_auto_commit=False,
    )
    await consumer.run(
        callback=consume_render_generated,
        producer=producer,
    )
    logger.info("Application started")
    yield
    await consumer.stop()
    logger.info("Application has completed")
