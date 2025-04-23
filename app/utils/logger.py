import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from app.config import get_settings

settings = get_settings()


def setup_logging(log_level_str="INFO"):
    log_level = getattr(logging, log_level_str.upper(), logging.INFO)

    # Create logs directory if it doesn't exist
    log_dir = os.environ.get("LOG_DIR", "logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Configure logger
    logger = logging.getLogger("library_api")

    # Clear any existing handlers to prevent duplicates on reloads
    if logger.handlers:
        logger.handlers = []

    logger.setLevel(log_level)
    logger.propagate = False  # Prevent duplicate logs

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)

    # File handler
    log_file_path = os.path.join(log_dir, "app.log")
    file_handler = RotatingFileHandler(
        log_file_path,
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setLevel(log_level)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(file_formatter)

    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
