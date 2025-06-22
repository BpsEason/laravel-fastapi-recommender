from fastapi import FastAPI, HTTPException, status
import logging
from .api.v1.routes import router as v1_router
from .core.config import settings
from .dependencies import get_db, get_redis_client

# 配置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__) # 為 main.py 實例化一個 logger

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION
)

app.include_router(v1_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    logger.info("Root endpoint accessed.") # 添加日誌
    return {"message": "Welcome to FastAPI Recommender Service!"}

@app.get("/health")
async def health_check():
    """
    健康檢查端點，檢查資料庫和 Redis 連接狀態。
    """
    logger.info("Health check requested.") # 添加日誌
    try:
        with get_db() as db:
            db.execute("SELECT 1")

        redis_client_instance = get_redis_client()
        if redis_client_instance:
            redis_client_instance.ping()
        else:
            raise Exception("Redis client not initialized or connection failed.")

        logger.info("Health check successful: Database and Redis connected.")
        return {"status": "ok", "database": "connected", "redis": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Service unhealthy: {e}"
        )
