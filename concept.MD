# Candid Health Proof of Concept: Scalable Medical Claims Processing (Python)

## 1. Experiment Overview
**Goal:** Build a highly scalable, fault-tolerant medical claims processing pipeline mimicking Candid Health's Revenue Cycle Management (RCM) platform.
**Technologies:** * **Web Backend (BE):** Python with FastAPI (excellent for handling async/await natively).
* **Orchestration:** Temporal Python SDK (stateful workflow management, retries, saga pattern).
* **Event Streaming:** Apache Kafka with `confluent-kafka-python` or `aiokafka` (pub/sub for lifecycle events and downstream analytics).

## 2. Architecture Flow


1.  **Ingestion:** A medical provider submits a claim payload via a `POST` request to the FastAPI web server.
2.  **Synchronous Response:** FastAPI validates the schema using Pydantic, persists the initial state to a primary database, and returns a `202 Accepted` with a `claim_id` to the client.
3.  **Workflow Initiation:** The FastAPI endpoint uses the Temporal Client to asynchronously start the `ProcessClaimWorkflow`.
4.  **Workflow Execution (Temporal):** Temporal orchestrates a series of Python-based asynchronous Activities (validation, coding, clearinghouse submission).
5.  **Event Emitting (Kafka):** As the workflow progresses, Temporal Activities publish state changes to a Kafka topic (e.g., `claim-lifecycle-events`). Downstream systems consume these events without coupling to the core workflow.

## 3. Claim Data Model
Using Pydantic in Python will make validating this CMS-1500-style payload incredibly easy on the FastAPI side. 

```json
{
  "claim_id": "clm_123456789",
  "provider": {
    "npi": "1234567890",
    "tax_id": "99-9999999",
    "organization_name": "Talkiatry"
  },
  "patient": {
    "patient_id": "pat_98765",
    "dob": "1980-05-15",
    "insurance": {
      "payer_id": "AETNA_001",
      "member_id": "W123456789",
      "group_number": "GRP999"
    }
  },
  "diagnoses": [
    { "code": "F32.9", "type": "ICD-10", "description": "Major depressive disorder" }
  ],
  "service_lines": [
    {
      "id": "svc_001",
      "date_of_service": "2026-03-04",
      "cpt_code": "99213",
      "modifier": "25",
      "charge_amount": 150.00,
      "diagnosis_pointers": ["F32.9"]
    }
  ],
  "status": "SUBMITTED",
  "metadata": {
    "source_system": "ElationEHR",
    "timestamp": "2026-03-05T14:30:00Z"
  }
}