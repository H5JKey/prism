import asyncio
from typing import Any

from aiokafka import AIOKafkaProducer
from core.constants import KAFKA_CONNECTION_ERRORS
from core.exceptions.base import KafkaSendError
from core.interfaces.kafka import AbstractKafkaProducer
from core.logging import get_logger

logger = get_logger(__name__)


class KafkaProducer(AbstractKafkaProducer):
    def __init__(self, **kwargs: Any) -> None:
        self._producer: AIOKafkaProducer | None = None
        self.params = kwargs

    async def start(self) -> None:
        delay = 1
        while True:
            try:
                if self._producer is None:
                    self._producer = AIOKafkaProducer(**self.params)
                    await self._producer.start()
                return  # noqa: TRY300
            except KAFKA_CONNECTION_ERRORS:
                logger.exception("Kafka connection error")
                self._producer = None
                await asyncio.sleep(delay)
                delay = min(delay * 2, 2 * 60)

    async def stop(self) -> None:
        if self._producer is None:
            return

        try:
            await self._producer.stop()
            logger.info("Kafka producer stopped")
        except Exception:
            logger.exception("Stopping kafka producer failed")
        finally:
            self._producer = None

    async def send(
        self,
        topic: str,
        value: Any | None = None,
        key: Any | None = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
    ) -> None:
        if self._producer is None:
            detail = "Producer not started"
            raise RuntimeError(detail)

        delay = base_delay
        for attempt in range(1, max_retries + 1):
            try:
                await self._producer.send_and_wait(
                    topic=topic,
                    key=key,
                    value=value,
                )
                logger.info(
                    "Sent message, topic=%s, key=%s,value=%s",
                    topic,
                    key,
                    value,
                )
                return  # noqa: TRY300
            except KAFKA_CONNECTION_ERRORS:
                logger.exception(
                    "Kafka send failed. Retry %s/%s, topic='%s', key='%s', delay=%.2fs",
                    attempt,
                    max_retries,
                    topic,
                    key,
                    delay,
                )
                await asyncio.sleep(delay)
                delay *= 2

        logger.error(
            "Message sending failed, topic=%s, key=%s,value=%s",
            topic,
            key,
            value,
        )
        error_detail = "Message sending failed"
        raise KafkaSendError(error_detail)
