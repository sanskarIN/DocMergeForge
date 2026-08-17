import os
import sys
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import docmergeforge.ui.main as ui_main  # noqa: E402
import docmergeforge.ui.paths as ui_paths  # noqa: E402
from docmergeforge.ui.packaged_entry import main  # noqa: E402


@pytest.mark.integration
def test_packaged_entry_smoke_initializes_desktop_without_dialogs(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = tmp_path / "settings.json"
    log = tmp_path / "docmergeforge.log"
    recent = tmp_path / "recent-projects.json"
    recovery = tmp_path / "recovery"

    monkeypatch.setattr(ui_paths, "settings_path", lambda: settings)
    monkeypatch.setattr(ui_paths, "log_path", lambda: log)
    monkeypatch.setattr(ui_main, "settings_path", lambda: settings)
    monkeypatch.setattr(ui_main, "log_path", lambda: log)
    monkeypatch.setattr(ui_main, "recent_projects_path", lambda: recent)
    monkeypatch.setattr(ui_main, "recovery_dir", lambda: recovery)
    monkeypatch.setattr(sys, "argv", ["DocMergeForge", "--packaged-smoke"])

    assert main() == 0
    assert log.is_file()
