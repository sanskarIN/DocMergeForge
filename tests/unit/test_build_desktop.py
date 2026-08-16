from pathlib import Path

from scripts.build_desktop import build_args


def test_build_args_create_windowed_onedir_app(tmp_path: Path) -> None:
    root = tmp_path
    branding = root / "assets" / "branding"
    branding.mkdir(parents=True)
    args = build_args(root)
    assert str(root / "src" / "docmergeforge" / "ui" / "main.py") in args
    assert "DocMergeForge" in args
    assert "--windowed" in args
    assert "--onedir" in args
    assert "--onefile" not in args
    assert "--add-data" in args


def test_build_args_can_create_one_file_app(tmp_path: Path) -> None:
    args = build_args(tmp_path, one_file=True)
    assert "--onefile" in args
    assert "--onedir" not in args
