from __future__ import annotations

import re

from docmergeforge import __version__
from docmergeforge.core.models import MergeProject
from docmergeforge.utilities.filename_template import render_filename

_INVALID_FILENAME = re.compile(r'[<>:"/\\|?*\x00-\x1f]+')
_WHITESPACE = re.compile(r"\s+")
_RESERVED = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{index}" for index in range(1, 10)),
    *(f"LPT{index}" for index in range(1, 10)),
}


def safe_basename(value: str) -> str:
    cleaned = _INVALID_FILENAME.sub("_", value)
    cleaned = _WHITESPACE.sub("_", cleaned)
    cleaned = re.sub(r"_+", "_", cleaned).strip(" ._")
    if not cleaned:
        cleaned = "DocMergeForge_Master"
    if cleaned.upper() in _RESERVED:
        cleaned = f"_{cleaned}"
    return cleaned


def render_project_basename(project: MergeProject) -> str:
    template = project.settings.filename_template.strip() or "{series}_Master"
    part_count = max(0, project.settings.expected_end - project.settings.expected_start + 1)
    rendered = render_filename(
        template,
        series=project.name,
        author=project.settings.pdf.author or "",
        part_count=part_count,
        edition=project.settings.pdf.edition or "",
        profile=project.settings.profile_name,
        version=__version__,
    )
    return safe_basename(rendered)
