from aiokafka import AIOKafkaProducer
from core.config.application import settings
from core.logging import get_logger

from infrastructure.kafka.utils import serialize_message

logger = get_logger(__name__)

_producer = None


async def get_producer() -> AIOKafkaProducer:
    global _producer  # noqa: PLW0603
    if _producer is None:
        _producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka.bootstrap_servers,
            value_serializer=serialize_message,
        )
    return _producer
