from typing import Optional, Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo import ASCENDING, IndexModel
from app.core.config import settings
from app.core.logging import logger


class MongoDBManager:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None
    is_connected: bool = False


mongodb_manager = MongoDBManager()


def is_mongodb_available() -> bool:
    """Return True if MongoDB is enabled and client/db are actively connected."""
    return bool(settings.MONGODB_ENABLED and mongodb_manager.is_connected and mongodb_manager.db is not None)


async def init_mongodb_indexes(db: AsyncIOMotorDatabase) -> None:
    """Ensure essential indexes on MongoDB collections."""
    try:
        content_col = db["lesson_contents"]
        indexes = [
            IndexModel([("lesson_id", ASCENDING)], unique=True, name="uniq_lesson_id"),
            IndexModel([("course_id", ASCENDING)], name="idx_course_id"),
            IndexModel([("is_published", ASCENDING)], name="idx_is_published"),
            IndexModel([("content_type", ASCENDING)], name="idx_content_type"),
        ]
        await content_col.create_indexes(indexes)
        logger.info("MongoDB lesson_contents indexes initialized.")
    except Exception as e:
        logger.debug(f"MongoDB index creation skipped/deferred: {e}")


async def connect_mongodb() -> None:
    """Initialize MongoDB connection client and indexes if enabled."""
    if not settings.MONGODB_ENABLED:
        logger.info("MongoDB is disabled (MONGODB_ENABLED=False). Using PostgreSQL fallback for content.")
        if mongodb_manager.client is not None:
            try:
                mongodb_manager.client.close()
            except Exception:
                pass
        mongodb_manager.client = None
        mongodb_manager.db = None
        mongodb_manager.is_connected = False
        return

    client = None
    try:
        timeout = getattr(settings, "MONGODB_TIMEOUT_MS", 1000)
        client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            serverSelectionTimeoutMS=timeout,
            connectTimeoutMS=timeout,
            socketTimeoutMS=timeout,
        )
        # Attempt an immediate ping to verify server is reachable
        await client.admin.command("ping")
        mongodb_manager.client = client
        mongodb_manager.db = client[settings.MONGODB_DB_NAME]
        mongodb_manager.is_connected = True
        logger.info(f"MongoDB client initialized for database: {settings.MONGODB_DB_NAME}")
        await init_mongodb_indexes(mongodb_manager.db)
    except Exception as e:
        # If connection fails or server is unreachable, close client immediately to stop background topology threads
        if client is not None:
            try:
                client.close()
            except Exception:
                pass
        mongodb_manager.client = None
        mongodb_manager.db = None
        mongodb_manager.is_connected = False
        logger.info(f"MongoDB not available ({e}). Using PostgreSQL fallback for content storage.")


async def close_mongodb() -> None:
    """Close MongoDB connection client."""
    if mongodb_manager.client is not None:
        try:
            mongodb_manager.client.close()
        except Exception:
            pass
        mongodb_manager.client = None
        mongodb_manager.db = None
        mongodb_manager.is_connected = False
        logger.info("MongoDB connection closed.")


def get_mongodb() -> Optional[AsyncIOMotorDatabase]:
    """Dependency / helper to get MongoDB database instance if connected."""
    if is_mongodb_available():
        return mongodb_manager.db
    return None


def get_content_collection() -> Optional[AsyncIOMotorCollection]:
    """Helper to get lesson_contents collection if MongoDB is available."""
    if is_mongodb_available():
        return mongodb_manager.db["lesson_contents"]
    return None


async def check_mongodb_health() -> bool:
    """Verify MongoDB connectivity for health checks without retrying if unavailable."""
    if not is_mongodb_available():
        return False
    try:
        if mongodb_manager.client is None:
            return False
        await mongodb_manager.client.admin.command("ping")
        return True
    except Exception:
        return False
