from typing import List, Optional

from pydantic import BaseModel


class Provider(BaseModel):
    npi: str
    tax_id: str
    organization_name: str


class Insurance(BaseModel):
    payer_id: str
    member_id: str
    group_number: str


class Patient(BaseModel):
    patient_id: str
    dob: str
    insurance: Insurance


class Diagnosis(BaseModel):
    code: str
    type: str
    description: Optional[str] = None


class ServiceLine(BaseModel):
    id: str
    date_of_service: str
    cpt_code: str
    modifier: Optional[str] = None
    charge_amount: float
    diagnosis_pointers: List[str]


class ClaimMetadata(BaseModel):
    source_system: str
    timestamp: str


class ClaimPayload(BaseModel):
    claim_id: str
    provider: Provider
    patient: Patient
    diagnoses: List[Diagnosis]
    service_lines: List[ServiceLine]
    status: str
    metadata: ClaimMetadata

