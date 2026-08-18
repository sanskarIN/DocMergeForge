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
