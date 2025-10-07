"""Logging configuration for PhotoZipper.

This module provides centralized logging setup with:
- Console handler (INFO level)
- File handler (DEBUG level)
- Consistent formatting across handlers
"""

import logging
from pathlib import Path
from typing import Optional


def setup_logging(
    output_dir: Path,
    log_level: str = "INFO"
) -> logging.Logger:
    """Set up logging with console and file handlers.
    
    Creates a logger with two handlers:
    1. Console handler - INFO level, outputs to stdout
    2. File handler - DEBUG level, writes to photozipper.log in output_dir
    
    Args:
        output_dir: Directory where log file will be created
        log_level: Log level for console output (DEBUG, INFO, WARNING, ERROR)
        
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger('photozipper')
    
    # Clear any existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Set logger level to DEBUG to capture everything
    logger.setLevel(logging.DEBUG)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    # Create formatters
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler (INFO level)
    console_handler = logging.StreamHandler()
    console_level = getattr(logging, log_level.upper(), logging.INFO)
    console_handler.setLevel(console_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (DEBUG level)
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        log_file = output_dir / 'photozipper.log'
        file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except (OSError, PermissionError) as e:
        # If file handler fails, log to console only
        logger.warning(f"Could not create log file: {e}")
    
    return logger
