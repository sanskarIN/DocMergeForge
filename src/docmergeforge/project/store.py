from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

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


def load_project(path: Path) -> MergeProject:
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    settings_data = data.get("settings", {})
    pdf = PdfSettings(**settings_data.get("pdf", {}))
    docx = DocxSettings(**settings_data.get("docx", {}))
    settings = MergeSettings(
        expected_start=settings_data.get("expected_start", 1),
        expected_end=settings_data.get("expected_end", 120),
        checksum_generation=settings_data.get("checksum_generation", True),
        automatic_validation=settings_data.get("automatic_validation", True),
        overwrite=settings_data.get("overwrite", False),
        profile_name=settings_data.get("profile_name", "Exact Preservation"),
        filename_template=settings_data.get("filename_template", "{series}_Master"),
        pdf=pdf,
        docx=docx,
    )
    return MergeProject(
        name=data["name"],
        source_folders=[Path(item) for item in data["source_folders"]],
        output_folder=Path(data["output_folder"]),
        settings=settings,
        selected_files=[Path(item) for item in data.get("selected_files", [])],
        state=MergeState(data.get("state", "CREATED")),
        last_successful_checkpoint=data.get("last_successful_checkpoint"),
        warnings=list(data.get("warnings", [])),
    )
