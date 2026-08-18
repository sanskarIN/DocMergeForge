import json
from pathlib import Path

import pytest

from docmergeforge.core.models import MergeProject
from docmergeforge.project.store import load_project, save_project


def test_project_round_trip(tmp_path: Path) -> None:
    project = MergeProject("Demo", [tmp_path / "src"], tmp_path / "out")
    project.selected_files = [tmp_path / "src" / "Part 2.pdf", tmp_path / "src" / "Part 1.pdf"]
    project.settings.profile_name = "Custom"
    project.settings.filename_template = "{series}_{part_count}_{profile}"
    path = tmp_path / "docmergeforge-project.json"

    save_project(project, path)
    restored = load_project(path)

    assert restored.name == "Demo"
    assert restored.source_folders == [tmp_path / "src"]
    assert restored.output_folder == tmp_path / "out"
    assert restored.selected_files == project.selected_files
    assert restored.settings.profile_name == "Custom"
    assert restored.settings.filename_template == "{series}_{part_count}_{profile}"
    assert not list(tmp_path.glob(f".{path.name}.*.tmp"))


def _write_project(tmp_path: Path, payload: object) -> Path:
    path = tmp_path / "project.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _valid_payload() -> dict[str, object]:
    return {
        "name": "Demo",
        "source_folders": ["source"],
        "output_folder": "output",
        "settings": {"expected_start": 1, "expected_end": 120},
    }


def test_project_load_rejects_non_object_root(tmp_path: Path) -> None:
    path = _write_project(tmp_path, ["not", "an", "object"])

    with pytest.raises(ValueError, match="root.*JSON object"):
        load_project(path)


def test_project_load_rejects_empty_source_folders(tmp_path: Path) -> None:
    payload = _valid_payload()
    payload["source_folders"] = []
    path = _write_project(tmp_path, payload)

    with pytest.raises(ValueError, match="source_folders.*at least one"):
        load_project(path)


def test_project_load_rejects_inverted_part_range(tmp_path: Path) -> None:
    payload = _valid_payload()
    payload["settings"] = {"expected_start": 10, "expected_end": 2}
    path = _write_project(tmp_path, payload)

    with pytest.raises(ValueError, match="positive and non-decreasing"):
        load_project(path)


def test_project_load_rejects_string_overwrite_flag(tmp_path: Path) -> None:
    payload = _valid_payload()
    payload["settings"] = {
        "expected_start": 1,
        "expected_end": 1,
        "overwrite": "false",
    }
    path = _write_project(tmp_path, payload)

    with pytest.raises(ValueError, match="settings.overwrite.*boolean"):
        load_project(path)


def test_project_load_rejects_invalid_pdf_boolean(tmp_path: Path) -> None:
    payload = _valid_payload()
    payload["settings"] = {
        "expected_start": 1,
        "expected_end": 1,
        "pdf": {"page_numbers": "yes"},
    }
    path = _write_project(tmp_path, payload)

    with pytest.raises(ValueError, match="settings.pdf.page_numbers.*boolean"):
        load_project(path)


def test_project_load_rejects_unknown_docx_fidelity_mode(tmp_path: Path) -> None:
    payload = _valid_payload()
    payload["settings"] = {
        "expected_start": 1,
        "expected_end": 1,
        "docx": {"fidelity_mode": "unsafe-native"},
    }
    path = _write_project(tmp_path, payload)

    with pytest.raises(ValueError, match="settings.docx.fidelity_mode.*must be one of"):
        load_project(path)
