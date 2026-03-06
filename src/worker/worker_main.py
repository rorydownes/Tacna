import asyncio

from temporalio.worker import Worker

from src.common.config import get_settings
from src.common.temporal_client import get_client
from src.worker.activities import code_claim, submit_to_clearinghouse, validate_claim
from src.worker.workflows import ProcessClaimWorkflow


async def main() -> None:
    settings = get_settings()
    client = await get_client()

    worker = Worker(
        client,
        task_queue="claims-task-queue",
        workflows=[ProcessClaimWorkflow],
        activities=[validate_claim, code_claim, submit_to_clearinghouse],
    )

    print(
        f"Starting Temporal worker on task queue 'claims-task-queue' "
        f"(namespace={settings.temporal_namespace})"
    )
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())

