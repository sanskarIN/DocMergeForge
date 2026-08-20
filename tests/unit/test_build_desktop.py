from pathlib import Path

import pytest

from docmergeforge.packaging.desktop import build_args, validate_build_root


def test_build_args_create_windowed_onedir_app(tmp_path: Path) -> None:
    root = tmp_path
    branding = root / "assets" / "branding"
    branding.mkdir(parents=True)
    args = build_args(root)
    assert str(root / "src" / "docmergeforge" / "ui" / "packaged_entry.py") in args
    assert "DocMergeForge" in args
    assert "--windowed" in args
    assert "--onedir" in args
    assert "--onefile" not in args
    assert "--add-data" in args


def test_build_args_can_create_one_file_app(tmp_path: Path) -> None:
    args = build_args(tmp_path, one_file=True)
    assert "--onefile" in args
    assert "--onedir" not in args


def test_validate_build_root_accepts_required_layout(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\n", encoding="utf-8")
    ui = tmp_path / "src" / "docmergeforge" / "ui"
    ui.mkdir(parents=True)
    for filename in (
        "main.py",
        "desktop_entry.py",
        "project_sync_dialog.py",
        "packaged_entry.py",
    ):
        (ui / filename).write_text("def main():\n    return 0\n", encoding="utf-8")

    assert validate_build_root(tmp_path) == tmp_path.resolve()


def test_validate_build_root_reports_missing_files(tmp_path: Path) -> None:
    with pytest.raises(ValueError) as exc_info:
        validate_build_root(tmp_path)

    message = str(exc_info.value)
    assert "pyproject.toml" in message
    assert "src" in message
    assert "main.py" in message
    assert "desktop_entry.py" in message
    assert "project_sync_dialog.py" in message
    assert "packaged_entry.py" in message
