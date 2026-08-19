from pathlib import Path

import pytest

from docmergeforge.core.models import MergeProject
from docmergeforge.core.part_range import MAX_EXPECTED_PART_COUNT
from docmergeforge.project.store import (
    load_project,
    load_project_snapshot,
    project_file_revision,
    save_project,
    save_project_if_revision,
)


def test_save_project_rejects_invalid_expected_range_before_writing(tmp_path: Path) -> None:
    project = MergeProject("Demo", [tmp_path / "source"], tmp_path / "output")
    project.settings.expected_end = MAX_EXPECTED_PART_COUNT + 1
    destination = tmp_path / "project.json"

    with pytest.raises(ValueError, match="cannot contain more than"):
        save_project(project, destination)

    assert not destination.exists()


def test_project_snapshot_revision_matches_persisted_bytes(tmp_path: Path) -> None:
    project = MergeProject("Demo", [tmp_path / "source"], tmp_path / "output")
    destination = tmp_path / "project.json"
    save_project(project, destination)

    restored, revision = load_project_snapshot(destination)

    assert restored == project
    assert revision == project_file_revision(destination)


def test_revision_guard_saves_when_project_file_is_unchanged(tmp_path: Path) -> None:
    project = MergeProject("Demo", [tmp_path / "source"], tmp_path / "output")
    destination = tmp_path / "project.json"
    save_project(project, destination)
    _, revision = load_project_snapshot(destination)
    project.name = "Updated"

    save_project_if_revision(project, destination, revision)

    assert load_project(destination).name == "Updated"


def test_revision_guard_rejects_stale_write_without_overwriting(tmp_path: Path) -> None:
    project = MergeProject("Demo", [tmp_path / "source"], tmp_path / "output")
    destination = tmp_path / "project.json"
    save_project(project, destination)
    _, revision = load_project_snapshot(destination)
    external_text = destination.read_text(encoding="utf-8").replace('"Demo"', '"External"', 1)
    destination.write_text(external_text, encoding="utf-8")
    project.name = "Local edit"

    with pytest.raises(ValueError, match="changed on disk"):
        save_project_if_revision(project, destination, revision)

    assert destination.read_text(encoding="utf-8") == external_text
    assert load_project(destination).name == "External"


def test_save_project_rejects_symlink_destination(tmp_path: Path) -> None:
    project = MergeProject("Demo", [tmp_path / "source"], tmp_path / "output")
    target = tmp_path / "project.json"
    save_project(project, target)
    original = target.read_text(encoding="utf-8")
    link = tmp_path / "project-link.json"
    try:
        link.symlink_to(target)
    except OSError:
        pytest.skip("symbolic links are not available on this test host")

    project.name = "Should not save"
    with pytest.raises(ValueError, match="symbolic link"):
        save_project(project, link)

    assert target.read_text(encoding="utf-8") == original
