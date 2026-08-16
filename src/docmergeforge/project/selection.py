from __future__ import annotations

from pathlib import Path

from docmergeforge.core.models import DocumentKind, InputDocument

_MERGEABLE_KINDS = {DocumentKind.PDF, DocumentKind.DOCX}


def _path_key(path: Path) -> str:
    """Return a stable comparison key without requiring the path to still exist."""
    try:
        return str(path.resolve(strict=False)).casefold()
    except OSError:
        return str(path.absolute()).casefold()


def apply_project_selection(
    discovered: list[InputDocument],
    selected_files: list[Path],
) -> list[InputDocument]:
    """Apply persisted document selection/order while retaining non-mergeable metadata.

    When ``selected_files`` is empty, discovery results are returned unchanged. When it
    is populated, only the selected PDF/DOCX files are returned as mergeable inputs and
    they are emitted in exactly the persisted order. Companion and unsupported files
    remain available to indexing/reporting, but can never become merge inputs here.
    """
    if not selected_files:
        return list(discovered)

    by_path = {_path_key(item.path): item for item in discovered}
    selected_documents: list[InputDocument] = []
    missing: list[Path] = []
    seen: set[str] = set()

    for path in selected_files:
        key = _path_key(path)
        if key in seen:
            raise ValueError(f"Selected file appears more than once: {path}")
        seen.add(key)
        item = by_path.get(key)
        if item is None:
            missing.append(path)
            continue
        if item.kind in _MERGEABLE_KINDS:
            selected_documents.append(item)

    if missing:
        missing_text = ", ".join(str(path) for path in missing)
        raise ValueError(f"Selected project files were not found during discovery: {missing_text}")

    metadata = [item for item in discovered if item.kind not in _MERGEABLE_KINDS]
    return selected_documents + metadata
