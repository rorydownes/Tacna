from pydantic import BaseModel

from src.common.models import ClaimPayload


class ClaimRequest(ClaimPayload):
    pass


class ClaimResponse(BaseModel):
    claim_id: str
    status: str

