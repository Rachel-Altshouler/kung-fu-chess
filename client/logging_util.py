from __future__ import annotations

import logging
from pathlib import Path


def setup_client_logger(log_dir: str | Path | None = None) -> logging.Logger:
    if log_dir is None:
        log_dir = Path(__file__).resolve().parent / "logs"
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("kungfu_client")
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log_path / "client.log", encoding="utf-8")
    handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    )
    logger.addHandler(handler)
    return logger
