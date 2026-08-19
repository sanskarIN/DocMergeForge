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
from docmergeforge.core.part_range import validate_expected_part_range
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
    if (
        not isinstance(value, list)
        or not all(isinstance(item, str) and item.strip() for item in value)
    ):
        raise ValueError(f"Project field '{label}' must be a JSON array of non-empty path strings.")
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
    ):
        raise ValueError("Project expected part range values must be integers.")
    try:
        return validate_expected_part_range(start, end)
    except ValueError as exc:
        raise ValueError(f"Project {exc}") from exc


def _bool_value(data: dict[str, Any], key: str, default: bool, label: str) -> bool:
    value = data.get(key, default)
    if not isinstance(value, bool):
        raise ValueError(f"Project field '{label}.{key}' must be a boolean.")
    return value


def _string_value(data: dict[str, Any], key: str, default: str, label: str) -> str:
    value = data.get(key, default)
    if not isinstance(value, str):
        raise ValueError(f"Project field '{label}.{key}' must be a string.")
    return value


def _optional_string(data: dict[str, Any], key: str, label: str) -> str | None:
    value = data.get(key)
    if value is not None and not isinstance(value, str):
        raise ValueError(f"Project field '{label}.{key}' must be a string or null.")
    return value


def _positive_int(data: dict[str, Any], key: str, default: int, label: str) -> int:
    value = data.get(key, default)
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise ValueError(f"Project field '{label}.{key}' must be a positive integer.")
    return value


def _choice(
    data: dict[str, Any],
    key: str,
    default: str,
    choices: set[str],
    label: str,
) -> str:
    value = _string_value(data, key, default, label)
    if value not in choices:
        allowed = ", ".join(sorted(choices))
        raise ValueError(f"Project field '{label}.{key}' must be one of: {allowed}.")
    return value


def _pdf_settings(data: dict[str, Any]) -> PdfSettings:
    label = "settings.pdf"
    return PdfSettings(
        add_part_bookmarks=_bool_value(data, "add_part_bookmarks", True, label),
        title=_optional_string(data, "title", label),
        author=_optional_string(data, "author", label),
        edition=_optional_string(data, "edition", label),
        include_title_page=_bool_value(data, "include_title_page", False, label),
        visible_toc=_bool_value(data, "visible_toc", False, label),
        page_numbers=_bool_value(data, "page_numbers", False, label),
        page_number_start=_positive_int(data, "page_number_start", 1, label),
        header_text=_optional_string(data, "header_text", label),
        footer_text=_optional_string(data, "footer_text", label),
        watermark_text=_optional_string(data, "watermark_text", label),
        optimization=_choice(
            data,
            "optimization",
            "preserve",
            {"preserve", "balanced", "archive"},
            label,
        ),
    )


def _docx_settings(data: dict[str, Any]) -> DocxSettings:
    label = "settings.docx"
    return DocxSettings(
        start_each_part_on_new_page=_bool_value(
            data, "start_each_part_on_new_page", True, label
        ),
        preserve_sections=_bool_value(data, "preserve_sections", True, label),
        fidelity_mode=_choice(
            data,
            "fidelity_mode",
            "portable",
            {"portable", "libreoffice", "word"},
            label,
        ),
        add_part_headings=_bool_value(data, "add_part_headings", True, label),
        create_toc_field=_bool_value(data, "create_toc_field", True, label),
        style_conflict_policy=_choice(
            data,
            "style_conflict_policy",
            "prefer_master",
            {"prefer_master", "error"},
            label,
        ),
        numbering_conflict_policy=_choice(
            data,
            "numbering_conflict_policy",
            "remap",
            {"remap", "error"},
            label,
        ),
        header_text=_optional_string(data, "header_text", label),
        footer_text=_optional_string(data, "footer_text", label),
        continuous_page_numbering=_bool_value(
            data, "continuous_page_numbering", True, label
        ),
    )


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
    pdf = _pdf_settings(_mapping(settings_data.get("pdf", {}), "settings.pdf"))
    docx = _docx_settings(_mapping(settings_data.get("docx", {}), "settings.docx"))
    expected_start, expected_end = _positive_range(settings_data)
    settings = MergeSettings(
        expected_start=expected_start,
        expected_end=expected_end,
        checksum_generation=_bool_value(
            settings_data, "checksum_generation", True, "settings"
        ),
        automatic_validation=_bool_value(
            settings_data, "automatic_validation", True, "settings"
        ),
        overwrite=_bool_value(settings_data, "overwrite", False, "settings"),
        profile_name=_string_value(
            settings_data, "profile_name", "Exact Preservation", "settings"
        ),
        filename_template=_string_value(
            settings_data, "filename_template", "{series}_Master", "settings"
        ),
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
