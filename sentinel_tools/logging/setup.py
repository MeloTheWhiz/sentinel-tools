from __future__ import annotations

import logging
from pathlib import Path


def configure_logging() -> logging.Logger:
    log_directory = Path.home() / ".local/share/sentinel-tools/logs"
    log_directory.mkdir(parents=True, exist_ok=True)

    log_file = log_directory / "sentinel-tools.log"
    logger = logging.getLogger("sentinel-tools")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
