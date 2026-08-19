from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from docmergeforge.core.models import DocumentKind, InputDocument, MergeProject
from docmergeforge.discovery.part_detection import natural_key
from docmergeforge.project.discovery import discover_project_sources
from docmergeforge.project.store import load_project, save_project
from docmergeforge.utilities.atomic import atomic_write_text, versioned_path

_MERGEABLE_KINDS = {DocumentKind.PDF, DocumentKind.DOCX}


def _path_key(path: Path) -> str:
    try:
        resolved = path.resolve(strict=False)
    except OSError:
        resolved = path.absolute()
    return os.path.normcase(str(resolved))


@dataclass(slots=True, frozen=True)
class ProjectSyncPlan:
    current: tuple[Path, ...]
    proposed: tuple[Path, ...]
    added: tuple[Path, ...]
    removed: tuple[Path, ...]
    reordered: bool
    duplicate_pdf_parts: tuple[int, ...]
    duplicate_docx_parts: tuple[int, ...]
    missing_pdf_parts: tuple[int, ...]
    missing_docx_parts: tuple[int, ...]

    @property
    def changed(self) -> bool:
        return tuple(map(_path_key, self.current)) != tuple(map(_path_key, self.proposed))

    @property
    def safe_to_apply(self) -> bool:
        return not self.duplicate_pdf_parts and not self.duplicate_docx_parts

    @property
    def numbering_complete_for_available_kinds(self) -> bool:
        return (
            bool(self.proposed)
            and self.safe_to_apply
            and not self.missing_pdf_parts
            and not self.missing_docx_parts
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "changed": self.changed,
            "safe_to_apply": self.safe_to_apply,
            "numbering_complete_for_available_kinds": self.numbering_complete_for_available_kinds,
            "current_count": len(self.current),
            "proposed_count": len(self.proposed),
            "current": [str(path) for path in self.current],
            "proposed": [str(path) for path in self.proposed],
            "added": [str(path) for path in self.added],
            "removed": [str(path) for path in self.removed],
            "reordered": self.reordered,
            "duplicate_parts": {
                "pdf": list(self.duplicate_pdf_parts),
                "docx": list(self.duplicate_docx_parts),
            },
            "missing_parts": {
                "pdf": list(self.missing_pdf_parts),
                "docx": list(self.missing_docx_parts),
            },
        }


def _eligible_documents(project: MergeProject, discovered: list[InputDocument]) -> list[InputDocument]:
    start = project.settings.expected_start
    end = project.settings.expected_end
    unique: list[InputDocument] = []
    seen: set[str] = set()

    for item in discovered:
        if (
            item.kind not in _MERGEABLE_KINDS
            or item.part.number is None
            or not start <= item.part.number <= end
        ):
            continue
        key = _path_key(item.path)
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)

    return sorted(
        unique,
        key=lambda item: (
            item.part.number if item.part.number is not None else end + 1,
            item.kind.value,
            natural_key(item.path.name),
            _path_key(item.path),
        ),
    )


def _duplicate_parts(
    documents: list[InputDocument],
    kind: DocumentKind,
) -> tuple[int, ...]:
    counts: dict[int, int] = {}
    for item in documents:
        if item.kind != kind or item.part.number is None:
            continue
        counts[item.part.number] = counts.get(item.part.number, 0) + 1
    return tuple(sorted(part for part, count in counts.items() if count > 1))


def _missing_parts(
    documents: list[InputDocument],
    kind: DocumentKind,
    start: int,
    end: int,
) -> tuple[int, ...]:
    found = {
        item.part.number
        for item in documents
        if item.kind == kind and item.part.number is not None
    }
    if not found:
        return ()
    return tuple(part for part in range(start, end + 1) if part not in found)


def plan_project_sync(
    project: MergeProject,
    discovered: list[InputDocument] | None = None,
) -> ProjectSyncPlan:
    """Build a non-mutating selected-file synchronization proposal.

    The proposal contains only numbered PDF/DOCX sources inside the configured expected
    range. Unnumbered front/back matter remains an explicit manual selection decision.
    """
    if discovered is None:
        discovered = discover_project_sources(project)

    eligible = _eligible_documents(project, discovered)
    current = tuple(project.selected_files)
    proposed = tuple(item.path for item in eligible)
    current_keys = tuple(_path_key(path) for path in current)
    proposed_keys = tuple(_path_key(path) for path in proposed)
    current_set = set(current_keys)
    proposed_set = set(proposed_keys)

    added = tuple(
        path
        for path, key in zip(proposed, proposed_keys, strict=True)
        if key not in current_set
    )
    removed = tuple(
        path for path, key in zip(current, current_keys, strict=True) if key not in proposed_set
    )
    common_current = tuple(key for key in current_keys if key in proposed_set)
    common_proposed = tuple(key for key in proposed_keys if key in current_set)
    start = project.settings.expected_start
    end = project.settings.expected_end

    return ProjectSyncPlan(
        current=current,
        proposed=proposed,
        added=added,
        removed=removed,
        reordered=common_current != common_proposed,
        duplicate_pdf_parts=_duplicate_parts(eligible, DocumentKind.PDF),
        duplicate_docx_parts=_duplicate_parts(eligible, DocumentKind.DOCX),
        missing_pdf_parts=_missing_parts(eligible, DocumentKind.PDF, start, end),
        missing_docx_parts=_missing_parts(eligible, DocumentKind.DOCX, start, end),
    )


def apply_project_sync(
    project: MergeProject,
    project_path: Path,
    plan: ProjectSyncPlan,
) -> Path | None:
    """Apply an approved plan with a durable backup and atomic project replacement."""
    if not plan.safe_to_apply:
        raise ValueError(
            "Refusing to apply an ambiguous synchronization plan with duplicate PDF/DOCX "
            "part numbers. Resolve duplicate source parts and preview again."
        )
    if not plan.changed:
        return None
    if project_path.is_symlink():
        raise ValueError("Refusing to synchronize a project file through a symbolic link.")
    if not project_path.is_file():
        raise ValueError(f"Project file does not exist: {project_path}")
    if tuple(map(_path_key, project.selected_files)) != tuple(map(_path_key, plan.current)):
        raise ValueError("Project selection changed after the synchronization plan was created.")

    persisted_project = load_project(project_path)
    if persisted_project != project:
        raise ValueError(
            "Project file changed on disk after it was loaded. Reload the project, review a new "
            "synchronization preview, and apply only that fresh plan."
        )

    backup_path = versioned_path(project_path.with_suffix(project_path.suffix + ".bak"))
    original_text = project_path.read_text(encoding="utf-8")
    atomic_write_text(backup_path, original_text)

    original_selection = list(project.selected_files)
    project.selected_files = list(plan.proposed)
    try:
        save_project(project, project_path)
    except Exception:
        project.selected_files = original_selection
        raise
    return backup_path
