import asyncio
from datetime import datetime

import httpx


async def main() -> None:
    claim = {
        "claim_id": "clm_123456789",
        "provider": {
            "npi": "1234567890",
            "tax_id": "99-9999999",
            "organization_name": "Talkiatry",
        },
        "patient": {
            "patient_id": "pat_98765",
            "dob": "1980-05-15",
            "insurance": {
                "payer_id": "AETNA_001",
                "member_id": "W123456789",
                "group_number": "GRP999",
            },
        },
        "diagnoses": [
            {
                "code": "F32.9",
                "type": "ICD-10",
                "description": "Major depressive disorder",
            }
        ],
        "service_lines": [
            {
                "id": "svc_001",
                "date_of_service": "2026-03-04",
                "cpt_code": "99213",
                "modifier": "25",
                "charge_amount": 150.00,
                "diagnosis_pointers": ["F32.9"],
            }
        ],
        "status": "SUBMITTED",
        "metadata": {
            "source_system": "ElationEHR",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        },
    }

    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        resp = await client.post("/claims", json=claim)
        print(f"Status: {resp.status_code}")
        print(f"Body: {resp.json()}")


if __name__ == "__main__":
    asyncio.run(main())

