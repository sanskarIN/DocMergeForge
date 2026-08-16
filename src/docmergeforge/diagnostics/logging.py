from __future__ import annotations

import logging
import re
from logging.handlers import RotatingFileHandler
from pathlib import Path

_LOGGER_NAME = "docmergeforge"
_SECRET_PATTERN = re.compile(
    r"(?i)\b(password|passwd|secret|token|authorization)\b\s*[:=]\s*([^\s,;]+)"
)
_BEARER_PATTERN = re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]+")


def redact_sensitive_text(value: str) -> str:
    value = _SECRET_PATTERN.sub(lambda match: f"{match.group(1)}=[REDACTED]", value)
    return _BEARER_PATTERN.sub("Bearer [REDACTED]", value)


class PrivacyFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = redact_sensitive_text(str(record.msg))
        if record.args:
            if isinstance(record.args, dict):
                record.args = {
                    key: redact_sensitive_text(str(value))
                    for key, value in record.args.items()
                }
            else:
                record.args = tuple(redact_sensitive_text(str(value)) for value in record.args)
        return True


def configure_logging(path: Path, level: str = "INFO") -> logging.Logger:
    path.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(_LOGGER_NAME)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.propagate = False

    for handler in list(logger.handlers):
        handler.close()
        logger.removeHandler(handler)

    handler = RotatingFileHandler(
        path,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    )
    handler.addFilter(PrivacyFilter())
    logger.addHandler(handler)
    return logger


def get_logger() -> logging.Logger:
    return logging.getLogger(_LOGGER_NAME)
