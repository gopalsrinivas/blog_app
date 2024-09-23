import os
import logging
from logging.config import dictConfig

# Set your desired log directory path
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../logger")

# Ensure the logger directory exists
os.makedirs(log_dir, exist_ok=True)

# Define the log file path inside the logger directory
log_file_path = os.path.join(log_dir, "logger_app.log")

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "{levelname} {asctime} {name} {message}",
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M:%S",  # Adding date and time format
        },
        "error_formatter": {  # Separate formatter for error logs
            "format": "{levelname} {asctime} {name} {message}",
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M:%S",  # Adding date and time for error logs
        },
    },
    "handlers": {
        "file": {
            "level": "DEBUG",  # Change to DEBUG for detailed logs
            "class": "logging.FileHandler",
            "filename": log_file_path,
            "formatter": "default",
        },
        "error_file": {
            "level": "ERROR",  # Dedicated handler for error logs
            "class": "logging.FileHandler",
            "filename": os.path.join(log_dir, "error_app.log"),
            "formatter": "error_formatter",  # Using error_formatter
        },
    },
    "root": {
        "handlers": ["file", "error_file"],
        "level": "DEBUG",  # Change to DEBUG for detailed logs
    },
}

# Apply the logging configuration
dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)
