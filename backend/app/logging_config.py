import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import sys

from .config import settings


def configure_logging() -> None:
    """Configure app logs to stdout and a rotated persistent file."""
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    log_dir = Path(settings.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "backend.log"

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )

    app_logger = logging.getLogger("super_bank")
    app_logger.setLevel(level)
    app_logger.handlers.clear()
    app_logger.propagate = False

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    app_logger.addHandler(stream_handler)
    app_logger.addHandler(file_handler)
    app_logger.info("logging.configured path=%s level=%s", log_path, settings.log_level.upper())
