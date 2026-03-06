import asyncio
import json
from typing import Optional

from aiokafka import AIOKafkaProducer

from .config import get_settings

_producer: Optional[AIOKafkaProducer] = None
_lock = asyncio.Lock()


async def get_producer() -> AIOKafkaProducer:
    global _producer
    if _producer is not None:
        return _producer

    async with _lock:
        if _producer is None:
            settings = get_settings()
            loop = asyncio.get_running_loop()
            _producer = AIOKafkaProducer(
                loop=loop,
                bootstrap_servers=settings.kafka_bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            )
            await _producer.start()

    return _producer


async def publish_claim_event(claim_id: str, state: str, payload: Optional[dict] = None) -> None:
    """
    Publish a simple claim lifecycle event to Kafka.
    """
    settings = get_settings()
    event = {
        "claim_id": claim_id,
        "state": state,
        "payload": payload or {},
    }
    producer = await get_producer()
    await producer.send_and_wait(settings.claim_lifecycle_topic, event)

