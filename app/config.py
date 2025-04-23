# app.config.py
import os
import logging
from pydantic_settings import BaseSettings
from functools import lru_cache

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


logger.info(f"DATABASE_URL environment variable: {os.getenv('DATABASE_URL')}")


class Settings(BaseSettings):
    DATABASE_URL: str
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "info"

    MAX_BORROWS_PER_USER: int = 5
    BORROW_DURATION_DAYS: int = 14
    OVERDUE_FINE_RATE: float = 0.5

    LOG_DIR: str = "logs"

    class Config:
        env_file = ".env"
        extra = "ignore"

@lru_cache()
def get_settings() -> BaseSettings:
    try:
        settings = Settings()
        logger.info(f"Loaded settings: DATABASE_URL={settings.DATABASE_URL}, ENVIRONMENT={settings.ENVIRONMENT}")
        return settings
    except Exception as e:
        logger.error(f"Error loading settings: {e}")
        raise
