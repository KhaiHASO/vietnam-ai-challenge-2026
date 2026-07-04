import logging
from dataclasses import dataclass

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import settings

logger = logging.getLogger("backend.mongo")


@dataclass
class MongoState:
    client: AsyncIOMotorClient | None = None
    database: AsyncIOMotorDatabase | None = None
    connected: bool = False
    last_error: str | None = None


mongo_state = MongoState()


async def connect_to_mongo() -> None:
    mongo_state.client = AsyncIOMotorClient(
        settings.mongodb_uri,
        serverSelectionTimeoutMS=2000,
        uuidRepresentation="standard",
    )
    mongo_state.database = mongo_state.client[settings.database_name]

    try:
        await mongo_state.client.admin.command("ping")
    except Exception as exc:
        mongo_state.connected = False
        mongo_state.last_error = exc.__class__.__name__
        logger.warning("MongoDB ping failed: %s", exc.__class__.__name__)
        return

    mongo_state.connected = True
    mongo_state.last_error = None
    logger.info("MongoDB connected to database '%s'", settings.database_name)


async def close_mongo_connection() -> None:
    if mongo_state.client is not None:
        mongo_state.client.close()

    mongo_state.client = None
    mongo_state.database = None
    mongo_state.connected = False


def get_database() -> AsyncIOMotorDatabase:
    if mongo_state.database is None:
        raise RuntimeError("MongoDB is not initialized")
    return mongo_state.database


def mongo_status() -> dict[str, object]:
    return {
        "name": settings.database_name,
        "connected": mongo_state.connected,
        "last_error": mongo_state.last_error,
    }
