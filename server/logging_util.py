from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path


def setup_logger(name: str, log_dir: str | Path) -> logging.Logger:
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler(log_path / f"{name}.log", encoding="utf-8")
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    )
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    )
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger


def log_event(logger: logging.Logger, event: str, **details):
    parts = [event]
    for key, value in details.items():
        parts.append(f"{key}={value}")
    logger.info(" | ".join(parts))
