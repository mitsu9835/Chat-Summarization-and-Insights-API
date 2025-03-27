"""
Logging configuration for the application.
"""
import logging
from config.settings import settings


def setup_logging():
    """Configure application-wide logging."""
    logger = logging.getLogger("chat_api")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Create handler
    handler = logging.StreamHandler()
    handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(handler)
    
    return logger


logger = setup_logging() 