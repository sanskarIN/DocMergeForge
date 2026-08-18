from __future__ import annotations

import logging
import re
from logging.handlers import RotatingFileHandler
from pathlib import Path

_LOGGER_NAME = "docmergeforge"
_SECRET_PATTERN = re.compile(
    r"(?ix)"
    r"(?P<key>[\"']?(?:password|passwd|secret|token|authorization|api[_-]?key|"
    r"access[_-]?token|refresh[_-]?token|client[_-]?secret)[\"']?\s*[:=]\s*)"
    r"(?P<quote>[\"']?)"
    r"(?P<value>[^\s,;}\]\"']+)"
    r"(?P=quote)?"
)
_BEARER_PATTERN = re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]+")
_AUTH_HEADER_PATTERN = re.compile(
    r"(?i)\bAuthorization\s*:\s*(?:Basic|Bearer)\s+[^\s,;]+"
)
_API_KEY_HEADER_PATTERN = re.compile(r"(?i)\b(?:X-)?Api-Key\s*:\s*[^\s,;]+")


def _redact_assignment(match: re.Match[str]) -> str:
    quote = match.group("quote")
    return f"{match.group('key')}{quote}[REDACTED]{quote}"


def redact_sensitive_text(value: str) -> str:
    value = _AUTH_HEADER_PATTERN.sub("Authorization: [REDACTED]", value)
    value = _API_KEY_HEADER_PATTERN.sub("Api-Key: [REDACTED]", value)
    value = _SECRET_PATTERN.sub(_redact_assignment, value)
    return _BEARER_PATTERN.sub("Bearer [REDACTED]", value)


class PrivacyFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = redact_sensitive_text(str(record.msg))
        if record.args:
            if isinstance(record.args, dict):
                record.args = {
                    key: redact_sensitive_text(str(value)) for key, value in record.args.items()
                }
            else:
                record.args = tuple(redact_sensitive_text(str(value)) for value in record.args)
        return True


def _configure_handler(handler: logging.Handler) -> logging.Handler:
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    handler.addFilter(PrivacyFilter())
    return handler


def configure_logging(path: Path, level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger(_LOGGER_NAME)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.propagate = False

    for handler in list(logger.handlers):
        handler.close()
        logger.removeHandler(handler)

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        handler: logging.Handler = RotatingFileHandler(
            path,
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
            encoding="utf-8",
        )
    except OSError:
        handler = logging.StreamHandler()

    logger.addHandler(_configure_handler(handler))
    return logger


def get_logger() -> logging.Logger:
    return logging.getLogger(_LOGGER_NAME)
