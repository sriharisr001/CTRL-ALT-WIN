"""Database configuration and Beanie startup."""
from contextlib import asynccontextmanager
from beanie import init_beanie
from pymongo import AsyncMongoClient
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    mongodb_url: str
    gemini_api_key: str = ""
    jwt_secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
client: AsyncMongoClient | None = None


async def connect_database() -> None:
    """Initialize models; keep API usable if a remote database is temporarily down."""
    global client
    from models import User, RiskReport
    # Beanie 2.x uses PyMongo's native async client; Motor is incompatible.
    client = AsyncMongoClient(settings.mongodb_url, serverSelectionTimeoutMS=7000)
    await client.admin.command("ping")
    await init_beanie(database=client.get_default_database(), document_models=[User, RiskReport])


async def close_database() -> None:
    if client:
        client.close()
