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


def create_db_and_tables():
    try:
        # Explicitly import models to ensure they're registered with SQLModel

        # Test database connection
        with engine.connect() as conn:
            logger.info("Database connection successful")

        # Log registered models
        logger.info("Registered models: %s", SQLModel.metadata.tables.keys())

        # Create tables
        logger.info("Creating database tables...")
        SQLModel.metadata.create_all(engine)
        logger.info("Database tables created successfully")

        # Verify tables
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        logger.info("Existing tables: %s", existing_tables)

        # Check for expected tables
        expected_tables = ["book", "author", "book_author_link"]
        for table in expected_tables:
            if table not in existing_tables:
                logger.error(f"Table '{table}' was not created")
            else:
                logger.info(f"Table '{table}' exists")

    except Exception as e:
        logger.error("Error creating tables: %s", str(e))
        raise


def get_session() -> Generator[Session, Session, None]:
    with Session(engine) as session:
        yield session
