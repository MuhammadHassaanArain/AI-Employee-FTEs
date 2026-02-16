"""
Logging infrastructure for AI Employee

Provides beautiful, colorized terminal logging with rich library
and file-based logging with timestamps.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
from rich.logging import RichHandler
from rich.traceback import install as install_rich_traceback
from rich.console import Console

# Install rich traceback handler for beautiful error displays
install_rich_traceback(show_locals=True, width=120, word_wrap=True)

# Define custom SUCCESS level (between INFO and WARNING)
SUCCESS_LEVEL = 25
logging.addLevelName(SUCCESS_LEVEL, "SUCCESS")

# Console for rich output
console = Console()

# Error deduplication cache to reduce spam
_error_cache = {}
_error_cache_max_age = 60  # seconds


class SuccessLogger(logging.Logger):
    """Custom logger with success() method"""

    def success(self, message, *args, **kwargs):
        """Log success message in green"""
        if self.isEnabledFor(SUCCESS_LEVEL):
            self._log(SUCCESS_LEVEL, message, args, **kwargs)


# Set custom logger class
logging.setLoggerClass(SuccessLogger)


class DedupFilter(logging.Filter):
    """Filter to deduplicate repeated error messages"""

    def filter(self, record):
        # Only deduplicate ERROR and WARNING levels
        if record.levelno not in (logging.ERROR, logging.WARNING):
            return True

        # Create cache key from message and module
        cache_key = f"{record.name}:{record.levelname}:{record.getMessage()}"
        current_time = datetime.now().timestamp()

        # Check if we've seen this error recently
        if cache_key in _error_cache:
            last_time = _error_cache[cache_key]
            if current_time - last_time < _error_cache_max_age:
                # Suppress duplicate within time window
                return False

        # Update cache and allow message
        _error_cache[cache_key] = current_time
        return True


def setup_logger(
    name: str,
    log_file: Optional[Path] = None,
    level: str = "INFO",
) -> logging.Logger:
    """
    Setup logger with rich console handler and optional file handler

    Args:
        name: Logger name
        log_file: Path to log file (optional)
        level: Logging level (DEBUG, INFO, WARNING, ERROR)

    Returns:
        Configured logger instance with success() method
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    logger.handlers.clear()

    # Rich console handler with beautiful formatting
    console_handler = RichHandler(
        console=console,
        show_time=True,
        show_level=True,
        show_path=True,
        markup=True,
        rich_tracebacks=True,
        tracebacks_show_locals=True,
        log_time_format="[%H:%M:%S]",
        level=getattr(logging, level.upper()),
    )

    # Custom format for rich handler (simplified, rich adds its own formatting)
    console_handler.setFormatter(
        logging.Formatter(
            "%(message)s",
            datefmt="[%X]",
        )
    )

    # Add deduplication filter to console
    console_handler.addFilter(DedupFilter())

    logger.addHandler(console_handler)

    # File handler (plain text, no colors) - if log file specified
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(getattr(logging, level.upper()))

        # Plain formatter for file (with full timestamp)
        file_formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)-8s %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    # Suppress noisy third-party loggers
    logging.getLogger("anthropic").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    return logger


def get_logger(name: str) -> SuccessLogger:
    """
    Get logger by name with success() method

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance with success() method
    """
    return logging.getLogger(name)


# Convenience function for quick success logging
def log_success(message: str):
    """Quick success log without getting logger"""
    logger = get_logger("ai_employee")
    logger.success(message)
