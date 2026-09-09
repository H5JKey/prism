from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from core.config.application import settings
from pydantic import ValidationError
from schemas.event import DLQFormatMessage

from infrastructure.kafka.producer import process_message
from infrastructure.kafka.utils import (
    deserialize_message,
    send_message,
    serialize_message,
)

_consumer = None


async def get_consumer() -> AIOKafkaConsumer:
    global _consumer  # noqa: PLW0603
    if _consumer is None:
        _consumer = AIOKafkaConsumer(
            settings.kafka.topic.generate_render,
            bootstrap_servers=settings.kafka.bootstrap_servers,
            group_id="backend",
            value_deserializer=deserialize_message,
        )
    return _consumer


async def consume(consumer: AIOKafkaConsumer, producer: AIOKafkaProducer) -> None:
    await consumer.start()
    async for message in consumer:
        try:
            await process_message(message)
            await consumer.commit()
        except ValidationError as error:
            dlq_format_message = DLQFormatMessage(
                message=message.value,
                error=str(error),
            )
            dlq_message = serialize_message(dlq_format_message)
            await send_message(
                producer=producer,
                topic=settings.kafka.topic.dead_letter_queue,
                value=dlq_message,
            )
