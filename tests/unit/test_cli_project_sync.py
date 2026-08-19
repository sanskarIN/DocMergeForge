import json
from pathlib import Path

import pytest

from docmergeforge.cli import main as cli
from docmergeforge.core.models import MergeProject, MergeSettings
from docmergeforge.project.store import load_project, save_project


def _write_project(tmp_path: Path) -> tuple[Path, Path]:
    source = tmp_path / "Book"
    source.mkdir()
    (source / "Part 2.docx").write_text("part two", encoding="utf-8")
    (source / "Part 1.docx").write_text("part one", encoding="utf-8")
    project = MergeProject(
        name="Book",
        source_folders=[source],
        output_folder=tmp_path / "Master",
        settings=MergeSettings(expected_start=1, expected_end=2),
    )
    project_path = tmp_path / "Book.json"
    save_project(project, project_path)
    return project_path, source


def test_cli_parser_supports_project_sync_apply() -> None:
    args = cli.build_parser().parse_args(
        ["project-sync", "--project", "Book.json", "--apply"]
    )

    assert args.command == "project-sync"
    assert args.project == Path("Book.json")
    assert args.apply is True


def test_cli_project_sync_previews_without_mutating_project(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    project_path, source = _write_project(tmp_path)

    exit_code = cli.main(["project-sync", "--project", str(project_path)])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["changed"] is True
    assert payload["applied"] is False
    assert payload["approval_required"] is True
    assert payload["backup"] is None
    assert payload["proposed"] == [
        str(source / "Part 1.docx"),
        str(source / "Part 2.docx"),
    ]
    assert load_project(project_path).selected_files == []
    assert not (tmp_path / "Book.json.bak").exists()


def test_cli_project_sync_apply_creates_backup_and_persists_order(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    project_path, source = _write_project(tmp_path)

    exit_code = cli.main(["project-sync", "--project", str(project_path), "--apply"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["changed"] is True
    assert payload["applied"] is True
    assert payload["approval_required"] is False
    assert payload["backup"] == str(tmp_path / "Book.json.bak")
    assert load_project(project_path).selected_files == [
        source / "Part 1.docx",
        source / "Part 2.docx",
    ]
    assert load_project(tmp_path / "Book.json.bak").selected_files == []


def test_cli_project_sync_apply_is_noop_when_selection_is_current(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    project_path, source = _write_project(tmp_path)
    project = load_project(project_path)
    project.selected_files = [source / "Part 1.docx", source / "Part 2.docx"]
    save_project(project, project_path)

    exit_code = cli.main(["project-sync", "--project", str(project_path), "--apply"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["changed"] is False
    assert payload["applied"] is False
    assert payload["backup"] is None
    assert not (tmp_path / "Book.json.bak").exists()
