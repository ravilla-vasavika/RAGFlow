"""Centralized logging configuration for RAG application."""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logger(name: str = "ragflow", level: str = "INFO") -> logging.Logger:
    """
    Configure and return a logger with console and file handlers.
    
    Args:
        name: Logger name
        level: Logging level (INFO, WARNING, ERROR, DEBUG)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Format for all handlers
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
    console_handler.setFormatter(formatter)
    
    # File handler with rotation
    log_file = log_dir / "app.log"
    file_handler = RotatingFileHandler(
        filename=log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5
    )
    file_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
    file_handler.setFormatter(formatter)
    
    # Add handlers to logger if not already present
    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
    
    return logger
