from __future__ import annotations

import hashlib
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
_MAX_BASENAME_UTF8_BYTES = 180


def _bounded_basename(value: str) -> str:
    encoded = value.encode("utf-8")
    if len(encoded) <= _MAX_BASENAME_UTF8_BYTES:
        return value

    digest = hashlib.sha256(encoded).hexdigest()[:12]
    suffix = f"_{digest}"
    budget = _MAX_BASENAME_UTF8_BYTES - len(suffix.encode("utf-8"))
    prefix_chars: list[str] = []
    used = 0
    for character in value:
        size = len(character.encode("utf-8"))
        if used + size > budget:
            break
        prefix_chars.append(character)
        used += size
    prefix = "".join(prefix_chars).rstrip(" ._") or "DocMergeForge"
    return f"{prefix}{suffix}"


def safe_basename(value: str) -> str:
    cleaned = _INVALID_FILENAME.sub("_", value)
    cleaned = _WHITESPACE.sub("_", cleaned)
    cleaned = re.sub(r"_+", "_", cleaned).strip(" ._")
    if not cleaned:
        cleaned = "DocMergeForge_Master"
    if cleaned.upper() in _RESERVED:
        cleaned = f"_{cleaned}"
    return _bounded_basename(cleaned)


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
