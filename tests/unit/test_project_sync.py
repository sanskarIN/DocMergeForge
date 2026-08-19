from pathlib import Path

import pytest

from docmergeforge.core.models import (
    DocumentKind,
    InputDocument,
    MergeProject,
    MergeSettings,
    PartIdentity,
)
from docmergeforge.project.discovery import discover_project_sources
from docmergeforge.project.store import load_project, save_project
from docmergeforge.project.sync import apply_project_sync, plan_project_sync


def _document(path: Path, kind: DocumentKind, part: int | None) -> InputDocument:
    return InputDocument(
        path=path,
        kind=kind,
        part=PartIdentity(part, f"Part {part}" if part is not None else path.stem),
        size=1,
        sha256=path.name,
    )


def _project(tmp_path: Path) -> MergeProject:
    return MergeProject(
        name="Book",
        source_folders=[tmp_path / "Book"],
        output_folder=tmp_path / "Master",
        settings=MergeSettings(expected_start=1, expected_end=10),
    )


def test_project_source_discovery_excludes_nested_output(tmp_path: Path) -> None:
    source = tmp_path / "Book"
    output = source / "Master"
    source.mkdir()
    output.mkdir()
    source_file = source / "notes.txt"
    old_output = output / "old-report.txt"
    source_file.write_text("source", encoding="utf-8")
    old_output.write_text("output", encoding="utf-8")
    project = MergeProject(
        name="Book",
        source_folders=[source],
        output_folder=output,
    )

    discovered = discover_project_sources(project)

    assert [item.path for item in discovered] == [source_file]


def test_sync_plan_selects_only_numbered_mergeable_files_in_range(tmp_path: Path) -> None:
    project = _project(tmp_path)
    root = project.source_folders[0]
    discovered = [
        _document(root / "Part 10.pdf", DocumentKind.PDF, 10),
        _document(root / "Part 2.pdf", DocumentKind.PDF, 2),
        _document(root / "Preface.pdf", DocumentKind.PDF, None),
        _document(root / "Part 11.pdf", DocumentKind.PDF, 11),
        _document(root / "Part 1.zip", DocumentKind.COMPANION, 1),
    ]

    plan = plan_project_sync(project, discovered)

    assert list(plan.proposed) == [root / "Part 2.pdf", root / "Part 10.pdf"]
    assert plan.added == plan.proposed
    assert plan.removed == ()
    assert plan.changed is True


def test_sync_plan_reports_added_removed_and_reordered_paths(tmp_path: Path) -> None:
    project = _project(tmp_path)
    root = project.source_folders[0]
    part_1 = root / "Part 1.pdf"
    part_2 = root / "Part 2.pdf"
    part_3 = root / "Part 3.pdf"
    old = root / "Old Part 4.pdf"
    project.selected_files = [part_2, old, part_1]
    discovered = [
        _document(part_3, DocumentKind.PDF, 3),
        _document(part_2, DocumentKind.PDF, 2),
        _document(part_1, DocumentKind.PDF, 1),
    ]

    plan = plan_project_sync(project, discovered)

    assert list(plan.proposed) == [part_1, part_2, part_3]
    assert plan.added == (part_3,)
    assert plan.removed == (old,)
    assert plan.reordered is True


def test_apply_sync_creates_backup_and_replaces_project_atomically(tmp_path: Path) -> None:
    project = _project(tmp_path)
    root = project.source_folders[0]
    old = root / "Part 2.pdf"
    new = root / "Part 1.pdf"
    project.selected_files = [old]
    project_path = tmp_path / "Book.json"
    save_project(project, project_path)
    plan = plan_project_sync(project, [_document(new, DocumentKind.PDF, 1)])

    backup = apply_project_sync(project, project_path, plan)

    assert backup == tmp_path / "Book.json.bak"
    assert backup.is_file()
    assert load_project(backup).selected_files == [old]
    assert load_project(project_path).selected_files == [new]
    assert project.selected_files == [new]


def test_apply_sync_noop_does_not_require_or_write_project_file(tmp_path: Path) -> None:
    project = _project(tmp_path)
    plan = plan_project_sync(project, [])

    backup = apply_project_sync(project, tmp_path / "missing.json", plan)

    assert backup is None
    assert not (tmp_path / "missing.json").exists()


def test_apply_sync_rejects_symlinked_project_file(tmp_path: Path) -> None:
    project = _project(tmp_path)
    project_path = tmp_path / "Book.json"
    save_project(project, project_path)
    link = tmp_path / "Book-link.json"
    try:
        link.symlink_to(project_path)
    except OSError:
        pytest.skip("symbolic links are not available on this test host")
    new = project.source_folders[0] / "Part 1.pdf"
    plan = plan_project_sync(project, [_document(new, DocumentKind.PDF, 1)])

    with pytest.raises(ValueError, match="symbolic link"):
        apply_project_sync(project, link, plan)
