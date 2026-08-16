from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


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
        data = json.loads(self.path.read_text(encoding="utf-8"))
        return [
            RecentProject(
                name=item["name"],
                project_file=Path(item["project_file"]),
                source_folder=Path(item["source_folder"]),
                output_folder=Path(item["output_folder"]),
            )
            for item in data
            if isinstance(item, dict)
        ]

    def add(self, project: RecentProject) -> None:
        items = [item for item in self.load() if item.project_file != project.project_file]
        items.insert(0, project)
        items = items[: self.limit]
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = [
            {
                "name": item.name,
                "project_file": str(item.project_file),
                "source_folder": str(item.source_folder),
                "output_folder": str(item.output_folder),
            }
            for item in items
        ]
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def remove_missing(self) -> list[RecentProject]:
        items = [item for item in self.load() if item.project_file.exists()]
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = [
            {
                "name": item.name,
                "project_file": str(item.project_file),
                "source_folder": str(item.source_folder),
                "output_folder": str(item.output_folder),
            }
            for item in items
        ]
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return items
