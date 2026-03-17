"""Logging configuration for the application."""

import logging
import logging.handlers
import os
from typing import Optional


def setup_logger(
    name: str, log_file: Optional[str] = None, level: int = logging.DEBUG
) -> logging.Logger:
    """Set up a logger with file and console handlers.

    Args:
        name: The name of the logger.
        log_file: The path to the log file (optional).
        level: The logging level.

    Returns:
        The configured logger.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    debug_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] %(message)s"
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_file,
            maxBytes=1024 * 1024 * 5,  # 5MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(level)
        # Use debug formatter for file to include function/line info
        file_handler.setFormatter(debug_formatter)
        logger.addHandler(file_handler)

    return logger


def setup_root_logger(log_dir: str = "logs") -> logging.Logger:
    """Set up the root logger for the application.

    Args:
        log_dir: The directory to store log files.

    Returns:
        The configured root logger.
    """
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Configure the root logger so that all child loggers (src.*, etc.) propagate here.
    logger = setup_logger("", os.path.join(log_dir, "mcmt.log"))

    # Suppress verbose debug output from third-party libraries.
    for lib in ("httpx", "httpcore", "openai", "hpack", "h2", "flet", "flet_core", "flet_web", "flet_runtime"):
        logging.getLogger(lib).setLevel(logging.WARNING)

    logger.info("===== APPLICATION STARTED =====")

    return logger