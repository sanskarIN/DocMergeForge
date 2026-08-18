from pathlib import Path


def _script_text() -> str:
    repository_root = Path(__file__).resolve().parents[2]
    return (repository_root / "scripts" / "report_word_acceptance_environment.ps1").read_text(
        encoding="utf-8"
    )


def test_word_acceptance_environment_recorder_captures_required_fields() -> None:
    script = _script_text()

    for field in (
        "windows_caption",
        "windows_version",
        "windows_build",
        "os_architecture",
        "powershell_version",
        "word_version",
        "word_build",
        "word_path",
        "office_platform",
        "office_version_to_report",
    ):
        assert field in script


def test_word_acceptance_environment_recorder_is_noninteractive_and_cleans_com() -> None:
    script = _script_text()

    assert "$word.Visible = $false" in script
    assert "$word.DisplayAlerts = 0" in script
    assert "$word.AutomationSecurity = 3" in script
    assert "try { $word.Quit() } catch { }" in script
    assert "FinalReleaseComObject($word)" in script
    assert "WaitForPendingFinalizers" in script
