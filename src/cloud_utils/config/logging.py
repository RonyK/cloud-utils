"""
Cloud Utils Common Logging Module

Provides common logging configuration for all cloud utilities.
"""

import logging
import sys
from typing import Optional

from .settings import LOG_LEVEL, DEBUG


def setup_logging(
    level: Optional[str] = None,
    format_string: Optional[str] = None,
    log_file: Optional[str] = None
) -> None:
    """
    Setup logging configuration
    
    Args:
        level: Log level (default: from settings or INFO)
        format_string: Log format string
        log_file: Log file path (optional)
    """
    if level is None:
        level = LOG_LEVEL
    
    if format_string is None:
        if DEBUG:
            format_string = '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        else:
            format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    
    formatter = logging.Formatter(format_string)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Add file handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Adjust external library log levels
    logging.getLogger('boto3').setLevel(logging.WARNING)
    logging.getLogger('botocore').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('opensearchpy').setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get logger instance
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def set_log_level(name: str, level: str) -> None:
    """
    Set log level for specific logger
    
    Args:
        name: Logger name
        level: Log level
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))


# Default logging setup
setup_logging()
