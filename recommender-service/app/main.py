from fastapi import FastAPI, HTTPException, status
import logging
from .api.v1.routes import router as v1_router
from .core.config import settings
from .dependencies import get_db, get_redis_client

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app.include_router(v1_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI Recommender Service!"}

@app.get("/health")
async def health_check():
    """
    健康檢查端點，檢查資料庫和 Redis 連接狀態。
    """
    try:
        with get_db() as db:
            db.execute("SELECT 1")
            
        redis_client_instance = get_redis_client()
        if redis_client_instance:
            redis_client_instance.ping()
        else:
            raise Exception("Redis client not initialized.")
            
        return {"status": "ok", "database": "connected", "redis": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Service unhealthy: {e}"
        )
