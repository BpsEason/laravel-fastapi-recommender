import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Laravel x FastAPI Recommender Service"
    PROJECT_DESCRIPTION: str = "Provides product recommendations based on user interactions and purchases."
    PROJECT_VERSION: str = "1.0.0"

    DATABASE_URL: str = os.getenv("DATABASE_URL", "mysql+pymysql://root:root_password@mysql:3306/laravel_db")
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB: int = int(os.getenv("REDIS_DB", 0))

    API_V1_STR: str = "/api/v1"

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env") # Load .env.docker in Docker
    # Note: In a dockerized environment, environment variables are usually passed directly,
    # or the .env.docker file is mounted. For local dev, a .env file might be used.

settings = Settings()
