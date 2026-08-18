from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, cast

from docmergeforge.core.models import (
    DocxSettings,
    MergeProject,
    MergeSettings,
    MergeState,
    PdfSettings,
)
from docmergeforge.utilities.atomic import atomic_write_text


def save_project(project: MergeProject, path: Path) -> None:
    data = asdict(project)
    data["source_folders"] = [str(item) for item in project.source_folders]
    data["output_folder"] = str(project.output_folder)
    data["selected_files"] = [str(item) for item in project.selected_files]
    data["state"] = project.state.value
    atomic_write_text(
        path,
        json.dumps(data, indent=2, ensure_ascii=False),
    )


def _mapping(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"Project field '{label}' must be a JSON object.")
    return cast(dict[str, Any], value)


def _required_string(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Project field '{key}' must be a non-empty string.")
    return value


def _path_list(value: object, label: str, *, allow_empty: bool) -> list[Path]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"Project field '{label}' must be a JSON array of path strings.")
    if not allow_empty and not value:
        raise ValueError(f"Project field '{label}' must contain at least one path.")
    return [Path(item) for item in value]


def _positive_range(settings_data: dict[str, Any]) -> tuple[int, int]:
    start = settings_data.get("expected_start", 1)
    end = settings_data.get("expected_end", 120)
    if (
        not isinstance(start, int)
        or isinstance(start, bool)
        or not isinstance(end, int)
        or isinstance(end, bool)
        or start < 1
        or end < start
    ):
        raise ValueError("Project expected part range must be positive and non-decreasing.")
    return start, end


def load_project(path: Path) -> MergeProject:
    raw: object = json.loads(path.read_text(encoding="utf-8"))
    data = _mapping(raw, "root")
    name = _required_string(data, "name")
    source_folders = _path_list(data.get("source_folders"), "source_folders", allow_empty=False)
    output_folder = Path(_required_string(data, "output_folder"))
    selected_files = _path_list(data.get("selected_files", []), "selected_files", allow_empty=True)

    warnings_raw = data.get("warnings", [])
    if not isinstance(warnings_raw, list) or not all(
        isinstance(item, str) for item in warnings_raw
    ):
        raise ValueError("Project field 'warnings' must be a JSON array of strings.")
    warnings = cast(list[str], warnings_raw)

    settings_data = _mapping(data.get("settings", {}), "settings")
    pdf = PdfSettings(**_mapping(settings_data.get("pdf", {}), "settings.pdf"))
    docx = DocxSettings(**_mapping(settings_data.get("docx", {}), "settings.docx"))
    expected_start, expected_end = _positive_range(settings_data)
    settings = MergeSettings(
        expected_start=expected_start,
        expected_end=expected_end,
        checksum_generation=settings_data.get("checksum_generation", True),
        automatic_validation=settings_data.get("automatic_validation", True),
        overwrite=settings_data.get("overwrite", False),
        profile_name=settings_data.get("profile_name", "Exact Preservation"),
        filename_template=settings_data.get("filename_template", "{series}_Master"),
        pdf=pdf,
        docx=docx,
    )

    state_raw = data.get("state", "CREATED")
    if not isinstance(state_raw, str):
        raise ValueError("Project field 'state' must be a string.")
    checkpoint = data.get("last_successful_checkpoint")
    if checkpoint is not None and not isinstance(checkpoint, str):
        raise ValueError("Project field 'last_successful_checkpoint' must be a string or null.")

    return MergeProject(
        name=name,
        source_folders=source_folders,
        output_folder=output_folder,
        settings=settings,
        selected_files=selected_files,
        state=MergeState(state_raw),
        last_successful_checkpoint=checkpoint,
        warnings=warnings,
    )
