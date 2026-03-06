import json
import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api import db
from src.api.schemas import ClaimRequest, ClaimResponse
from src.common.temporal_client import start_claim_workflow

router = APIRouter(prefix="/claims", tags=["claims"])


@router.post(
    "",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=ClaimResponse,
)
async def create_claim(
    request: ClaimRequest,
    session: AsyncSession = Depends(db.get_db_session),
) -> ClaimResponse:
    claim_id = request.claim_id or f"clm_{uuid.uuid4().hex}"

    await db.insert_claim(
        session=session,
        claim_id=claim_id,
        status="SUBMITTED",
        raw_payload=request.model_dump_json(),
    )

    await start_claim_workflow(claim_id)

    return ClaimResponse(claim_id=claim_id, status="ACCEPTED")

