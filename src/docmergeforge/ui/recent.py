from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from docmergeforge.utilities.atomic import atomic_write_text


@dataclass(slots=True, frozen=True)
class RecentProject:
    name: str
    project_file: Path
    source_folder: Path
    output_folder: Path


class RecentProjectsStore:
    def __init__(self, path: Path, limit: int = 12) -> None:
        self.path = path
        self.limit = limit

    def load(self) -> list[RecentProject]:
        if not self.path.exists():
            return []
        try:
            data: object = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            return []
        if not isinstance(data, list):
            return []

        projects: list[RecentProject] = []
        required = ("name", "project_file", "source_folder", "output_folder")
        for item in data:
            if not isinstance(item, dict):
                continue
            if not all(isinstance(item.get(key), str) for key in required):
                continue
            projects.append(
                RecentProject(
                    name=item["name"],
                    project_file=Path(item["project_file"]),
                    source_folder=Path(item["source_folder"]),
                    output_folder=Path(item["output_folder"]),
                )
            )
        return projects[: self.limit]

    @staticmethod
    def _serialize(items: list[RecentProject]) -> str:
        payload = [
            {
                "name": item.name,
                "project_file": str(item.project_file),
                "source_folder": str(item.source_folder),
                "output_folder": str(item.output_folder),
            }
            for item in items
        ]
        return json.dumps(payload, indent=2)

    def add(self, project: RecentProject) -> None:
        items = [item for item in self.load() if item.project_file != project.project_file]
        items.insert(0, project)
        atomic_write_text(self.path, self._serialize(items[: self.limit]))

    def remove_missing(self) -> list[RecentProject]:
        items = [item for item in self.load() if item.project_file.exists()]
        atomic_write_text(self.path, self._serialize(items))
        return items
