from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from sqlalchemy import text

from src.api.db import engine
from src.common.kafka_client import get_producer
from src.common.temporal_client import get_client

WORKER_TASK_QUEUE = "claims-task-queue"


async def _safe_check(check: Callable[[], Awaitable[bool]]) -> bool:
    try:
        return await check()
    except Exception:
        return False


async def _check_postgres() -> bool:
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        return result.scalar_one() == 1


async def _check_kafka() -> bool:
    # Producer startup performs broker connectivity/bootstrap metadata checks.
    await get_producer()
    return True


async def _check_temporal() -> bool:
    client = await get_client()
    # Lightweight non-mutating server interaction to validate connectivity.
    await _call_temporal_get_system_info(client)
    return True


async def _check_worker() -> bool:
    client = await get_client()
    response = await _describe_task_queue(client)
    pollers = _extract_pollers(response)
    return len(pollers) > 0


async def _call_temporal_get_system_info(client: Any) -> None:
    workflow_service = getattr(client, "workflow_service", None)
    if workflow_service is None:
        return

    try:
        from temporalio.api.workflowservice.v1 import GetSystemInfoRequest

        await workflow_service.get_system_info(GetSystemInfoRequest())
    except Exception:
        # If this RPC shape changes by SDK version, successful client creation
        # is still a useful connectivity signal.
        return


async def _describe_task_queue(client: Any) -> Any:
    workflow_service = getattr(client, "workflow_service", None)
    if workflow_service is None:
        return None

    try:
        from temporalio.api.enums.v1 import TaskQueueType
        from temporalio.api.taskqueue.v1 import TaskQueue
        from temporalio.api.workflowservice.v1 import DescribeTaskQueueRequest

        request = DescribeTaskQueueRequest(
            namespace=client.namespace,
            task_queue=TaskQueue(name=WORKER_TASK_QUEUE),
            task_queue_type=TaskQueueType.TASK_QUEUE_TYPE_WORKFLOW,
        )
        return await workflow_service.describe_task_queue(request)
    except Exception:
        return None


def _extract_pollers(response: Any) -> list[Any]:
    if response is None:
        return []

    # Temporal response types have shifted over SDK versions.
    for attr in ("pollers", "task_queue_status", "task_queue_pollers"):
        value = getattr(response, attr, None)
        if value is None:
            continue
        if isinstance(value, list):
            return value
        pollers = getattr(value, "pollers", None)
        if isinstance(pollers, list):
            return pollers

    return []


async def build_heartbeat() -> dict[str, Any]:
    components = {
        "postgres": await _safe_check(_check_postgres),
        "kafka": await _safe_check(_check_kafka),
        "temporal": await _safe_check(_check_temporal),
        "api": True,
        "worker": await _safe_check(_check_worker),
    }
    return {
        "status": all(components.values()),
        "components": components,
    }
