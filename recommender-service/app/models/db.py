from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)

try:
    engine = create_engine(settings.DATABASE_URL)
    # 測試資料庫連接
    with engine.connect() as connection:
        connection.execute("SELECT 1")
    logger.info("Database engine created and connected successfully.")
except Exception as e:
    logger.critical(f"Failed to create database engine or connect: {e}")
    # 在實際應用中，這裡可能需要更優雅的處理，例如應用程式啟動失敗

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Helper to create tables for testing/initial setup
def init_db_tables():
    """僅用於測試或初始設定，生產環境通常由 Laravel Migration 管理"""
    logger.info("Attempting to create database tables via SQLAlchemy Base.metadata.create_all.")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully (if they didn't exist).")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
