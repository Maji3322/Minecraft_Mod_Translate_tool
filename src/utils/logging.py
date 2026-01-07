"""
Logging configuration for the application.
"""

import logging
import logging.handlers
import os
import sys
from typing import Optional


def setup_logger(name: str, log_file: Optional[str] = None, level: int = logging.DEBUG) -> logging.Logger:
    """
    Set up a logger with file and console handlers.
    
    Args:
        name: The name of the logger
        log_file: The path to the log file (optional)
        level: The logging level
        
    Returns:
        The configured logger
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.handlers:
        return logger
    
    # Create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Create file handler if log_file is provided
    if log_file:
        # Ensure logs directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        # Create rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_file,
            maxBytes=1024 * 1024,  # 1MB
            backupCount=3,
            encoding="utf-8"
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def setup_root_logger(log_dir: str = "logs") -> logging.Logger:
    """
    Set up the root logger for the application.
    
    Args:
        log_dir: The directory to store log files
        
    Returns:
        The configured root logger
    """
    # Ensure logs directory exists
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    # Set up root logger
    logger = setup_logger("mcmt", os.path.join(log_dir, "mcmt.log"))
    logger.info("===== APPLICATION STARTED =====")
    
    return logger
