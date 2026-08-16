from docmergeforge.diagnostics.logging import redact_sensitive_text


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
