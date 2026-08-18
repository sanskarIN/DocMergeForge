import logging
from pathlib import Path

import pytest

from docmergeforge.diagnostics import logging as diagnostics_logging
from docmergeforge.diagnostics.logging import configure_logging, redact_sensitive_text


def test_redacts_common_secret_assignments() -> None:
    value = "password=hunter2 token:abc123 authorization=BasicXYZ safe=value"
    redacted = redact_sensitive_text(value)
    assert "hunter2" not in redacted
    assert "abc123" not in redacted
    assert "BasicXYZ" not in redacted
    assert "safe=value" in redacted


def test_redacts_bearer_credentials() -> None:
    redacted = redact_sensitive_text("Authorization header Bearer abc.def-123")
    assert "abc.def-123" not in redacted
    assert "Bearer [REDACTED]" in redacted


def test_redacts_json_style_and_common_secret_names() -> None:
    value = (
        '{"password": "hunter2", "api_key": "api123", '
        '"client_secret": "client456", "access_token": "access789"}'
    )
    redacted = redact_sensitive_text(value)

    for secret in ("hunter2", "api123", "client456", "access789"):
        assert secret not in redacted
    assert redacted.count("[REDACTED]") == 4


def test_redacts_basic_authorization_and_api_key_headers() -> None:
    value = "Authorization: Basic dXNlcjpwYXNz X-Api-Key: key-123"
    redacted = redact_sensitive_text(value)

    assert "dXNlcjpwYXNz" not in redacted
    assert "key-123" not in redacted
    assert "Authorization: [REDACTED]" in redacted
    assert "Api-Key: [REDACTED]" in redacted


def test_configure_logging_falls_back_to_private_stream_on_file_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def failing_handler(*args: object, **kwargs: object) -> logging.Handler:
        del args, kwargs
        raise OSError("simulated log-file failure")

    monkeypatch.setattr(diagnostics_logging, "RotatingFileHandler", failing_handler)

    logger = configure_logging(tmp_path / "app.log")
    assert len(logger.handlers) == 1
    handler = logger.handlers[0]
    assert isinstance(handler, logging.StreamHandler)
    assert not isinstance(handler, logging.FileHandler)

    record = logging.LogRecord(
        "docmergeforge",
        logging.ERROR,
        __file__,
        1,
        "api_key=secret-value",
        (),
        None,
    )
    assert handler.filter(record)
    assert "secret-value" not in str(record.msg)
    assert "[REDACTED]" in str(record.msg)

    handler.close()
    logger.removeHandler(handler)
