from fastapi import FastAPI

from src.api import db
from src.api.heartbeat import build_heartbeat
from src.api.routes import claims

app = FastAPI(title="Temporal RCM PoC")


@app.on_event("startup")
async def on_startup() -> None:
    await db.init_db()


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/heartbeat")
async def heartbeat() -> dict:
    return await build_heartbeat()


app.include_router(claims.router)

