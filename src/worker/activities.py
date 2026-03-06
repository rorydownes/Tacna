from temporalio import activity

from src.common.kafka_client import publish_claim_event


@activity.defn
async def validate_claim(claim_id: str) -> str:
    await publish_claim_event(claim_id, "VALIDATED")
    return "validated"


@activity.defn
async def code_claim(claim_id: str) -> str:
    await publish_claim_event(claim_id, "CODED")
    return "coded"


@activity.defn
async def submit_to_clearinghouse(claim_id: str) -> str:
    await publish_claim_event(claim_id, "SUBMITTED_TO_CLEARINGHOUSE")
    return "submitted"

