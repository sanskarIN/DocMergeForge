from __future__ import annotations

from pathlib import Path

from docmergeforge.core.models import InputDocument, MergeProject
from docmergeforge.discovery.scanner import scan


def _resolved(path: Path) -> Path:
    try:
        return path.resolve(strict=False)
    except OSError:
        return path.absolute()


def _is_within(path: Path, directory: Path) -> bool:
    try:
        _resolved(path).relative_to(_resolved(directory))
    except ValueError:
        return False
    return True


def discover_project_sources(project: MergeProject) -> list[InputDocument]:
    """Discover project sources without applying persisted selected-file filtering.

    A strictly nested output directory is excluded so previously published artifacts,
    reports, and transaction residue cannot be fed back into source discovery.
    """
    discovered = scan(project.source_folders, recursive=True)
    output = _resolved(project.output_folder)
    source_roots = [_resolved(root) for root in project.source_folders]
    output_is_strictly_nested = any(
        output != source_root and _is_within(output, source_root) for source_root in source_roots
    )
    if output_is_strictly_nested:
        return [item for item in discovered if not _is_within(item.path, output)]
    return discovered
