from typing import Generator
from sqlmodel import SQLModel, create_engine, Session, inspect
from app.config import get_settings
from app.utils.logger import setup_logging


settings = get_settings()
logger = setup_logging(log_level_str=settings.LOG_LEVEL if hasattr(settings, "LOG_LEVEL") else "INFO")

logger.info("DATABASE_URL: %s", settings.DATABASE_URL)

engine = create_engine(
    settings.DATABASE_URL,
    echo=True if settings.ENVIRONMENT == "development" else False
)


def get_session() -> Generator[Session, Session, None]:
    with Session(engine) as session:
        yield session
