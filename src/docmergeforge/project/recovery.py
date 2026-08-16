from __future__ import annotations

from pathlib import Path

from docmergeforge.core.models import MergeProject
from docmergeforge.project.store import load_project, save_project


class RecoveryStore:
    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir

    def checkpoint(self, project: MergeProject, name: str) -> Path:
        self.base_dir.mkdir(parents=True, exist_ok=True)
        project.last_successful_checkpoint = name
        path = self.base_dir / "recovery-project.json"
        save_project(project, path)
        return path

    def recover(self) -> MergeProject | None:
        path = self.base_dir / "recovery-project.json"
        return load_project(path) if path.exists() else None

    def clear(self) -> None:
        (self.base_dir / "recovery-project.json").unlink(missing_ok=True)
