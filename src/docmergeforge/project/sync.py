from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from docmergeforge.core.models import DocumentKind, InputDocument, MergeProject
from docmergeforge.discovery.part_detection import natural_key
from docmergeforge.project.discovery import discover_project_sources
from docmergeforge.project.store import save_project
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

    @property
    def changed(self) -> bool:
        return tuple(map(_path_key, self.current)) != tuple(map(_path_key, self.proposed))

    def to_dict(self) -> dict[str, object]:
        return {
            "changed": self.changed,
            "current_count": len(self.current),
            "proposed_count": len(self.proposed),
            "current": [str(path) for path in self.current],
            "proposed": [str(path) for path in self.proposed],
            "added": [str(path) for path in self.added],
            "removed": [str(path) for path in self.removed],
            "reordered": self.reordered,
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

    current = tuple(project.selected_files)
    proposed = tuple(item.path for item in _eligible_documents(project, discovered))
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

    return ProjectSyncPlan(
        current=current,
        proposed=proposed,
        added=added,
        removed=removed,
        reordered=common_current != common_proposed,
    )


def apply_project_sync(
    project: MergeProject,
    project_path: Path,
    plan: ProjectSyncPlan,
) -> Path | None:
    """Apply an approved plan with a durable backup and atomic project replacement."""
    if not plan.changed:
        return None
    if project_path.is_symlink():
        raise ValueError("Refusing to synchronize a project file through a symbolic link.")
    if not project_path.is_file():
        raise ValueError(f"Project file does not exist: {project_path}")
    if tuple(map(_path_key, project.selected_files)) != tuple(map(_path_key, plan.current)):
        raise ValueError("Project selection changed after the synchronization plan was created.")

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
