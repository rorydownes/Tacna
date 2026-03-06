from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://claims_user:claims_password@postgres:5432/claims_db"
    temporal_host: str = "temporal:7233"
    temporal_namespace: str = "default"
    kafka_bootstrap_servers: str = "kafka:9092"
    claim_lifecycle_topic: str = "claim-lifecycle-events"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_prefix = ""
        case_sensitive = False


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

