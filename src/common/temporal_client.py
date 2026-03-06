from typing import Optional

from temporalio import client as temporal_client

from .config import get_settings

_client: Optional[temporal_client.Client] = None


async def get_client() -> temporal_client.Client:
    global _client
    if _client is None:
        settings = get_settings()
        _client = await temporal_client.Client.connect(
            target_host=settings.temporal_host,
            namespace=settings.temporal_namespace,
        )
    return _client


async def start_claim_workflow(claim_id: str) -> str:
    """
    Start the ProcessClaimWorkflow for the given claim_id.
    Returns the workflow ID.
    """
    from src.worker.workflows import ProcessClaimWorkflow  # avoid circular at import time

    client = await get_client()
    handle = await client.start_workflow(
        ProcessClaimWorkflow.run,
        claim_id,
        id=f"process-claim-{claim_id}",
        task_queue="claims-task-queue",
    )
    return handle.id

