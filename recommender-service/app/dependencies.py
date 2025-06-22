from redis import Redis
from sqlalchemy.orm import Session
import logging

from .core.config import settings
from .models.db import SessionLocal

logger = logging.getLogger(__name__)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

_redis_client: Redis = None

def get_redis_client() -> Redis:
    global _redis_client
    if _redis_client is None:
        try:
            _redis_client = Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True
            )
            _redis_client.ping()
            logger.info("Successfully connected to Redis via dependency.")
        except Exception as e:
            logger.error(f"Could not connect to Redis via dependency: {e}")
            _redis_client = None
    return _redis_client
