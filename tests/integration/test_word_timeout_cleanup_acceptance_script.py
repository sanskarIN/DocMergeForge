import json
from pathlib import Path

import pytest

from docmergeforge.core.exceptions import ValidationError
from docmergeforge.docx.fidelity import FidelityCapability
from docmergeforge.docx.native import NativeCommandResult
from docmergeforge.docx.word_process import WordProcessCleanupResult
from scripts import check_word_timeout_cleanup_acceptance as script


def _capability() -> FidelityCapability:
    return FidelityCapability(
        mode="word",
        available=True,
        production_ready=False,
        detail="test Word host",
        automation_ready=True,
        executable="fake-powershell",
    )


def test_word_timeout_cleanup_acceptance_records_timeout_and_cleanup(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_dir = tmp_path / "evidence"
    captured_script = ""

    monkeypatch.setattr(
        script,
        "require_fidelity_automation",
        lambda mode: _capability(),
    )

    def fake_run(
        command: list[str], *, timeout_seconds: int
    ) -> NativeCommandResult:
        nonlocal captured_script
        identity = Path(command[command.index("-ProcessIdentityFile") + 1])
        identity.write_text(
            json.dumps(
                {
                    "process_id": 4242,
                    "process_name": "WINWORD",
                    "start_time_utc_ticks": 638910000000000000,
                }
            ),
            encoding="utf-8",
        )
        captured_script = Path(command[command.index("-File") + 1]).read_text(
            encoding="utf-8"
        )
        raise ValidationError(
            f"Native DOCX fidelity command timed out after {timeout_seconds} seconds."
        )

    monkeypatch.setattr(script, "run_native_command", fake_run)
    monkeypatch.setattr(
        script,
        "cleanup_word_process_identity",
        lambda identity, powershell: WordProcessCleanupResult(
            identity_present=True,
            process_found=True,
            terminated=True,
        ),
    )

    exit_code = script.main(
        [
            "--output-dir",
            str(output_dir),
            "--timeout",
            "5",
            "--hold-seconds",
            "30",
        ]
    )
    payload = json.loads(
        (output_dir / "word-timeout-cleanup-evidence.json").read_text(
            encoding="utf-8"
        )
    )

    assert exit_code == 0
    assert payload["accepted"] is True
    assert payload["timeout_observed"] is True
    assert payload["identity_recorded"] is True
    assert payload["process_found_during_cleanup"] is True
    assert payload["forced_termination"] is True
    assert "GetWindowThreadProcessId" in captured_script
    assert "Start-Sleep -Seconds $HoldSeconds" in captured_script


def test_word_timeout_cleanup_acceptance_rejects_non_timeout_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        script,
        "require_fidelity_automation",
        lambda mode: _capability(),
    )
    monkeypatch.setattr(
        script,
        "run_native_command",
        lambda command, **kwargs: (_ for _ in ()).throw(
            ValidationError("Word COM automation failed before timeout.")
        ),
    )

    with pytest.raises(ValidationError, match="before timeout"):
        script.main(["--output-dir", str(tmp_path / "evidence")])


def test_word_timeout_cleanup_acceptance_requires_identity_after_timeout(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        script,
        "require_fidelity_automation",
        lambda mode: _capability(),
    )

    def fake_timeout(command: list[str], **kwargs: object) -> NativeCommandResult:
        raise ValidationError("Native DOCX fidelity command timed out after 20 seconds.")

    monkeypatch.setattr(script, "run_native_command", fake_timeout)

    with pytest.raises(ValidationError, match="before Word process identity was recorded"):
        script.main(["--output-dir", str(tmp_path / "evidence")])


def test_word_timeout_cleanup_acceptance_rejects_missing_cleanup_identity(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_dir = tmp_path / "evidence"
    monkeypatch.setattr(
        script,
        "require_fidelity_automation",
        lambda mode: _capability(),
    )

    def fake_timeout(command: list[str], **kwargs: object) -> NativeCommandResult:
        identity = Path(command[command.index("-ProcessIdentityFile") + 1])
        identity.write_text(
            json.dumps(
                {
                    "process_id": 4242,
                    "process_name": "WINWORD",
                    "start_time_utc_ticks": 638910000000000000,
                }
            ),
            encoding="utf-8",
        )
        raise ValidationError("Native DOCX fidelity command timed out after 20 seconds.")

    monkeypatch.setattr(script, "run_native_command", fake_timeout)
    monkeypatch.setattr(
        script,
        "cleanup_word_process_identity",
        lambda identity, powershell: WordProcessCleanupResult(
            identity_present=False,
            process_found=False,
            terminated=False,
        ),
    )

    with pytest.raises(ValidationError, match="lost its process identity"):
        script.main(["--output-dir", str(output_dir)])


def test_word_timeout_cleanup_acceptance_refuses_evidence_overwrite(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_dir = tmp_path / "evidence"
    output_dir.mkdir()
    (output_dir / "word-timeout-cleanup-evidence.json").write_text(
        "{}",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        script,
        "require_fidelity_automation",
        lambda mode: _capability(),
    )

    with pytest.raises(SystemExit, match="Refusing to overwrite existing"):
        script.main(["--output-dir", str(output_dir)])


def test_word_timeout_cleanup_acceptance_rejects_invalid_duration() -> None:
    with pytest.raises(SystemExit, match="greater than --timeout"):
        script.main(["--timeout", "20", "--hold-seconds", "20"])
