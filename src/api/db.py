from datetime import datetime

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.common.config import get_settings


class Base(DeclarativeBase):
    pass


class Claim(Base):
    __tablename__ = "claims"

    id = Column(String, primary_key=True, index=True)
    status = Column(String, nullable=False)
    raw_payload = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


settings = get_settings()
engine = create_async_engine(settings.database_url, echo=False, future=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def insert_claim(session: AsyncSession, claim_id: str, status: str, raw_payload: str) -> None:
    claim = Claim(id=claim_id, status=status, raw_payload=raw_payload)
    session.add(claim)
    await session.commit()


async def get_db_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

