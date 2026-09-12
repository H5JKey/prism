import asyncio

from core.config.application import settings
from core.logging import configure_logging, get_logger
from infrastructure.kafka.producer import KafkaProducer
from infrastructure.kafka.utils import serialize_message

from outbox_worker.helpers import run_worker

logger = get_logger(__name__)


async def main() -> None:
    configure_logging()
    producer = KafkaProducer(
        bootstrap_servers=settings.kafka.bootstrap_servers,
        value_serializer=serialize_message,
    )
    await producer.start()
    logger.info("Kafka producer for outbox worker started")
    try:
        await run_worker(producer)
    finally:
        await producer.stop()


if __name__ == "__main__":
    asyncio.run(main())
