import logging
import sys
from pathlib import Path
from agent.config import LOG_LEVEL, LOG_DIR


def setup_logger(name, log_file=None):
    """
    Setup a logger with console and optional file handlers.
    
    Args:
        name: Logger name
        log_file: Optional log file path
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL))
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, LOG_LEVEL))
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        log_path = LOG_DIR / log_file
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(getattr(logging, LOG_LEVEL))
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


# Create module logger
logger = setup_logger(__name__)
