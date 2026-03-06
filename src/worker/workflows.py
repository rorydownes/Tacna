from datetime import timedelta

from temporalio import workflow

from src.worker import activities


@workflow.defn
class ProcessClaimWorkflow:
    @workflow.run
    async def run(self, claim_id: str) -> None:
        await workflow.execute_activity(
            activities.validate_claim,
            claim_id,
            schedule_to_close_timeout=timedelta(seconds=10),
        )
        await workflow.execute_activity(
            activities.code_claim,
            claim_id,
            schedule_to_close_timeout=timedelta(seconds=10),
        )
        await workflow.execute_activity(
            activities.submit_to_clearinghouse,
            claim_id,
            schedule_to_close_timeout=timedelta(seconds=10),
        )

