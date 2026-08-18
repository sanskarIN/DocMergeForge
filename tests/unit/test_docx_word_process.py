import json
from pathlib import Path

import pytest

from docmergeforge.core.exceptions import ValidationError
from docmergeforge.docx import word_process
from docmergeforge.docx.native import NativeCommandResult


def _write_identity(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "process_id": 4242,
                "process_name": "WINWORD",
                "start_time_utc_ticks": 638910000000000000,
            }
        ),
        encoding="utf-8",
    )


def test_word_process_cleanup_is_noop_without_identity(tmp_path: Path) -> None:
    result = word_process.cleanup_word_process_identity(
        tmp_path / "missing.json",
        powershell="fake-powershell",
    )

    assert not result.identity_present
    assert not result.process_found
    assert not result.terminated


def test_word_process_cleanup_uses_pid_name_and_start_time_guard(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    identity = tmp_path / "word-process.json"
    _write_identity(identity)
    captured_script = ""

    def fake_run(command: list[str], **kwargs: object) -> NativeCommandResult:
        nonlocal captured_script
        script = Path(command[command.index("-File") + 1])
        captured_script = script.read_text(encoding="utf-8")
        payload = {
            "identity_match": True,
            "process_found": True,
            "terminated": True,
        }
        return NativeCommandResult(tuple(command), json.dumps(payload), "")

    monkeypatch.setattr(word_process, "run_native_command", fake_run)
    result = word_process.cleanup_word_process_identity(
        identity,
        powershell="fake-powershell",
    )

    assert result.identity_present
    assert result.process_found
    assert result.terminated
    assert "Get-Process -Id $wordProcessId" in captured_script
    assert "$actualName -ne 'WINWORD'" in captured_script
    assert "$actualStartTicks -ne $expectedStartTicks" in captured_script
    assert "Stop-Process -Id $wordProcessId -Force" in captured_script


def test_word_process_cleanup_accepts_already_exited_process(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    identity = tmp_path / "word-process.json"
    _write_identity(identity)

    def fake_run(command: list[str], **kwargs: object) -> NativeCommandResult:
        payload = {
            "identity_match": True,
            "process_found": False,
            "terminated": False,
        }
        return NativeCommandResult(tuple(command), json.dumps(payload), "")

    monkeypatch.setattr(word_process, "run_native_command", fake_run)
    result = word_process.cleanup_word_process_identity(
        identity,
        powershell="fake-powershell",
    )

    assert result.identity_present
    assert not result.process_found
    assert not result.terminated


def test_word_process_cleanup_rejects_unsafe_identity(tmp_path: Path) -> None:
    identity = tmp_path / "word-process.json"
    identity.write_text(
        json.dumps(
            {
                "process_id": 4242,
                "process_name": "notepad",
                "start_time_utc_ticks": 638910000000000000,
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValidationError, match="Unsafe Word process identity"):
        word_process.cleanup_word_process_identity(
            identity,
            powershell="fake-powershell",
        )


def test_word_process_cleanup_rejects_invalid_result(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    identity = tmp_path / "word-process.json"
    _write_identity(identity)

    monkeypatch.setattr(
        word_process,
        "run_native_command",
        lambda command, **kwargs: NativeCommandResult(tuple(command), "not-json", ""),
    )

    with pytest.raises(ValidationError, match="invalid evidence"):
        word_process.cleanup_word_process_identity(
            identity,
            powershell="fake-powershell",
        )


def test_word_process_cleanup_rejects_nonpositive_timeout(tmp_path: Path) -> None:
    identity = tmp_path / "word-process.json"
    _write_identity(identity)

    with pytest.raises(ValidationError, match="timeout must be at least one second"):
        word_process.cleanup_word_process_identity(
            identity,
            powershell="fake-powershell",
            timeout_seconds=0,
        )
