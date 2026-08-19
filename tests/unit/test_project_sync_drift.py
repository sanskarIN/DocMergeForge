import json
from pathlib import Path

import pytest

from docmergeforge.core.models import MergeProject, MergeSettings
from docmergeforge.project.drift import evaluate_project_sync_drift
from docmergeforge.project.store import save_project
from docmergeforge.project.sync import plan_project_sync
from scripts import check_project_sync


def _project(tmp_path: Path, end: int = 2) -> tuple[MergeProject, Path]:
    source = tmp_path / "Book"
    source.mkdir()
    project = MergeProject(
        name="Book",
        source_folders=[source],
        output_folder=tmp_path / "Master",
        settings=MergeSettings(expected_start=1, expected_end=end),
    )
    return project, source


def _write_parts(source: Path, *parts: int) -> list[Path]:
    paths: list[Path] = []
    for part in parts:
        path = source / f"Part {part}.docx"
        path.write_text(f"part {part}", encoding="utf-8")
        paths.append(path)
    return paths


def test_drift_result_is_in_sync_when_saved_selection_matches_sources(tmp_path: Path) -> None:
    project, source = _project(tmp_path)
    part_1, part_2 = _write_parts(source, 1, 2)
    project.selected_files = [part_1, part_2]

    result = evaluate_project_sync_drift(project)

    assert result.in_sync is True
    assert result.exit_code == 0
    assert result.plan.changed is False
    assert result.plan.safe_to_apply is True
    assert result.to_dict()["in_sync"] is True


def test_drift_result_fails_when_saved_selection_is_stale(tmp_path: Path) -> None:
    project, source = _project(tmp_path)
    _write_parts(source, 1, 2)

    result = evaluate_project_sync_drift(project)

    assert result.in_sync is False
    assert result.exit_code == 2
    assert result.plan.changed is True


def test_drift_result_fails_for_duplicate_ambiguity_even_without_selection_diff(
    tmp_path: Path,
) -> None:
    project, source = _project(tmp_path, end=1)
    (source / "Part 1.docx").write_text("one", encoding="utf-8")
    (source / "Part 1 copy.docx").write_text("duplicate", encoding="utf-8")
    project.selected_files = list(plan_project_sync(project).proposed)

    result = evaluate_project_sync_drift(project)

    assert result.plan.changed is False
    assert result.plan.safe_to_apply is False
    assert result.plan.duplicate_docx_parts == (1,)
    assert result.in_sync is False
    assert result.exit_code == 2


def test_drift_result_does_not_treat_missing_parts_as_selection_drift(tmp_path: Path) -> None:
    project, source = _project(tmp_path, end=3)
    part_1, part_2 = _write_parts(source, 1, 2)
    project.selected_files = [part_1, part_2]

    result = evaluate_project_sync_drift(project)

    assert result.plan.changed is False
    assert result.plan.safe_to_apply is True
    assert result.plan.missing_docx_parts == (3,)
    assert result.plan.numbering_complete_for_available_kinds is False
    assert result.in_sync is True
    assert result.exit_code == 0


def test_check_project_sync_script_emits_json_and_exit_code(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    project, source = _project(tmp_path)
    part_1, part_2 = _write_parts(source, 1, 2)
    project.selected_files = [part_1, part_2]
    project_path = tmp_path / "Book.json"
    save_project(project, project_path)

    exit_code = check_project_sync.main(["--project", str(project_path)])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["project"] == str(project_path)
    assert payload["in_sync"] is True
    assert payload["changed"] is False
    assert payload["safe_to_apply"] is True
