from pathlib import Path


def _script_text() -> str:
    repository_root = Path(__file__).resolve().parents[2]
    script_path = repository_root / "scripts" / "check_word_process_state.ps1"
    return script_path.read_text(encoding="utf-8")


def test_word_process_state_guard_checks_winword_and_writes_evidence() -> None:
    script = _script_text()

    assert 'ValidateSet("before", "after")' in script
    assert "Get-Process -Name WINWORD" in script
    assert "winword_process_count" in script
    assert "clean = ($processes.Count -eq 0)" in script
    assert "ConvertTo-Json" in script


def test_word_process_state_guard_waits_after_and_fails_on_leftover_process() -> None:
    script = _script_text()

    assert 'if ($Phase -eq "after")' in script
    assert "Start-Sleep -Seconds 2" in script
    assert "if ($processes.Count -gt 0)" in script
    assert "WINWORD process state is not clean" in script
