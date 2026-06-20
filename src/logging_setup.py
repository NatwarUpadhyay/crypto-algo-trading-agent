"""
Logging configuration for the trading agent.

Dual handlers:
  - JSON to file (for advisory module, dashboards, automated parsing)
  - Human-readable to console (for development)
"""

import logging
import logging.handlers
from pathlib import Path

import structlog
from pythonjsonlogger import jsonlogger


def setup_logging(log_dir: Path, log_file: str, log_level: str) -> logging.Logger:
    """
    Initialize dual-handler logging: JSON file + console.

    Args:
        log_dir: Directory to write logs to
        log_file: Filename for log output
        log_level: Root logger level (INFO, DEBUG, etc.)

    Returns:
        Configured root logger instance
    """
    # Create log directory if it doesn't exist
    log_dir.mkdir(parents=True, exist_ok=True)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Remove any existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # ========================================================================
    # Handler 1: JSON to file (for parsing, advisory module, dashboards)
    # ========================================================================
    json_log_path = log_dir / log_file
    json_handler = logging.FileHandler(json_log_path)
    json_handler.setLevel(logging.INFO)

    json_formatter = jsonlogger.JsonFormatter(
        fmt="%(timestamp)s %(level)s %(name)s %(message)s"
    )
    json_handler.setFormatter(json_formatter)
    root_logger.addHandler(json_handler)

    # ========================================================================
    # Handler 2: Human-readable to console (for development)
    # ========================================================================
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    console_formatter = logging.Formatter(
        fmt="[%(asctime)s] %(levelname)-8s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # ========================================================================
    # Configure structlog (structured logging for events)
    # ========================================================================
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    return root_logger
