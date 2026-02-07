import logging
import logging.handlers
import os
import sys
import json
from datetime import datetime
from typing import Any, Dict

from .config import settings

class JsonFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    def format(self, record: logging.LogRecord) -> str:
        log_entry: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName,
            "line": record.lineno,
        }
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)

def setup_logging():
    """
    Centralized logging setup.
    Configures console and rotating file handlers based on settings.
    """
    # Ensure logs directory exists
    log_dir = os.path.dirname(settings.log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    
    # Common formatters
    if settings.log_format.lower() == "json":
        formatter = JsonFormatter()
    else:
        log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        date_format = "%Y-%m-%d %H:%M:%S"
        formatter = logging.Formatter(log_format, date_format)

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear existing handlers to avoid duplicates during re-initialization
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File Handler (Timed Rotating)
    try:
        file_handler = logging.handlers.TimedRotatingFileHandler(
            settings.log_file,
            when=settings.log_rotation,
            interval=1,
            backupCount=settings.log_backup_count,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    except Exception as e:
        # Fallback if file logging fails (e.g. permission issues)
        root_logger.error(f"Failed to initialize file logging: {e}")

    # Set some common library loggers to WARNING to reduce noise
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    
    logging.info("Logging initialized (Level: %s, Format: %s, File: %s)", 
                 settings.log_level, settings.log_format, settings.log_file)
