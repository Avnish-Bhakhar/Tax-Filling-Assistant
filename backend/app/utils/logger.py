"""
Structured Logging Module
Provides centralized, structured logging with privacy-aware filtering.
"""

import logging
import sys
import re
from datetime import datetime
from pathlib import Path


class PrivacyFilter(logging.Filter):
    """Filter sensitive information from log records."""

    SENSITIVE_PATTERNS = [
        (r'\b[A-Z]{5}[0-9]{4}[A-Z]\b', '[PAN_REDACTED]'),  # PAN Number
        (r'\b\d{12}\b', '[AADHAAR_REDACTED]'),  # Aadhaar
        (r'\b\d{10,12}\b', '[PHONE_REDACTED]'),  # Phone
        (r'[\w\.-]+@[\w\.-]+\.\w+', '[EMAIL_REDACTED]'),  # Email
    ]

    def filter(self, record):
        if hasattr(record, 'msg') and isinstance(record.msg, str):
            for pattern, replacement in self.SENSITIVE_PATTERNS:
                record.msg = re.sub(pattern, replacement, record.msg)
        return True


class TaxAppLogger:
    """Custom logger for the Tax Filing Assistant."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.logger = logging.getLogger("TaxAssistant")
        self.logger.setLevel(logging.DEBUG)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_format)

        # File handler
        log_dir = Path(__file__).resolve().parent.parent.parent / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(
            log_dir / f"taxbot_{datetime.now().strftime('%Y%m%d')}.log"
        )
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(module)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)

        # Add privacy filter
        privacy_filter = PrivacyFilter()
        console_handler.addFilter(privacy_filter)
        file_handler.addFilter(privacy_filter)

        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    def get_logger(self, module_name=None):
        if module_name:
            return logging.getLogger(f"TaxAssistant.{module_name}")
        return self.logger


def get_logger(module_name=None):
    """Convenience function to get a logger instance."""
    return TaxAppLogger().get_logger(module_name)
