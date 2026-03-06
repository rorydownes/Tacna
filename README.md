## Temporal RCM PoC

This repository is a proof of concept for a scalable medical claims processing pipeline using:

- **FastAPI** for the HTTP API
- **Temporal** (Python SDK) for workflow orchestration
- **Kafka** for claim lifecycle events
- **PostgreSQL** for persistence


### One-time local development setup

From the repo root, run the setup script to install prerequisites via Homebrew (Docker Desktop, Python 3.12, a virtualenv, and project deps). Safe to run multiple times:

```bash
./setup_env.sh
```

### Quick start

1. Copy the example environment file (or use the setup script above, which does this for you):

   ```bash
   cp .env.example .env
   ```

2. Build and start the stack:

   ```bash
   docker-compose up --build
   ```

3. Once running:

- FastAPI should be available at `http://localhost:8000`
- Temporal Web UI should be available at `http://localhost:8233`
- PostgreSQL and Kafka run inside the Docker network

4. Submit a sample claim:

   ```bash
   python scripts/submit_test_claim.py
   ```

   You should see a `202` response with a `claim_id`. In the Docker logs you should see:

   - The API persisting the claim to PostgreSQL
   - The Temporal worker running the `ProcessClaimWorkflow`
   - Kafka events being published for each workflow activity step

### High-level flow

1. `POST /claims` to the FastAPI service with a CMS-1500-style payload.
2. The API validates the payload and persists a claim record in PostgreSQL.
3. The API starts a Temporal `ProcessClaimWorkflow` for the `claim_id`.
4. The Temporal worker runs stub activities and publishes claim lifecycle events to Kafka.

Subsequent iterations will flesh out real validation, coding, and clearinghouse logic.

