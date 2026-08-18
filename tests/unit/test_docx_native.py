from pathlib import Path
from subprocess import CompletedProcess, TimeoutExpired

import pytest
from docx import Document

from docmergeforge.core.exceptions import ValidationError
from docmergeforge.docx import native
from docmergeforge.utilities.hashing import sha256_file


def test_run_native_command_rejects_empty_command() -> None:
    with pytest.raises(ValidationError, match="cannot be empty"):
        native.run_native_command([])


def test_run_native_command_captures_success(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(*args: object, **kwargs: object) -> CompletedProcess[str]:
        return CompletedProcess(["office"], 0, stdout="ok", stderr="")

    monkeypatch.setattr(native.subprocess, "run", fake_run)
    result = native.run_native_command(["office", "--headless"])
    assert result.command == ("office", "--headless")
    assert result.stdout == "ok"


def test_run_native_command_fails_closed_on_nonzero(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(*args: object, **kwargs: object) -> CompletedProcess[str]:
        return CompletedProcess(["office"], 9, stdout="", stderr="failure")

    monkeypatch.setattr(native.subprocess, "run", fake_run)
    with pytest.raises(ValidationError, match="exit code 9"):
        native.run_native_command(["office"])


def test_run_native_command_fails_closed_on_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(*args: object, **kwargs: object) -> CompletedProcess[str]:
        raise TimeoutExpired(cmd=["office"], timeout=1)

    monkeypatch.setattr(native.subprocess, "run", fake_run)
    with pytest.raises(ValidationError, match="timed out"):
        native.run_native_command(["office"], timeout_seconds=1)


def test_validate_native_docx_output_and_source_hash(tmp_path: Path) -> None:
    source = tmp_path / "source.docx"
    Document().save(source)
    expected = sha256_file(source)

    native.validate_native_docx_output(source)
    native.verify_native_source_unchanged(source, expected)

    Document().save(source)
    with pytest.raises(ValidationError, match="Source integrity violation"):
        native.verify_native_source_unchanged(source, expected)
