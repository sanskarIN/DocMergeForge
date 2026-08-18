from __future__ import annotations

import json
from dataclasses import asdict, dataclass, fields
from pathlib import Path
from typing import Any

from docmergeforge.utilities.atomic import atomic_write_text


@dataclass(slots=True)
class AppSettings:
    theme: str = "system"
    default_output_folder: str = ""
    temporary_directory: str = ""
    worker_count: int = 2
    logging_level: str = "INFO"
    checksum_generation: bool = True
    automatic_validation: bool = True
    pdf_optimization: str = "preserve"
    docx_fidelity_mode: str = "portable"
    crash_recovery: bool = True
    merge_profile: str = "Exact Preservation"
    filename_template: str = "{series}_Complete_{part_count}_Part_Master_Edition"
    libreoffice_integration: bool = True
    word_high_fidelity: bool = False
    recent_project_history: bool = True
    reduced_motion: bool = False
    text_scale_percent: int = 100
    first_run_completed: bool = False

    def save(self, path: Path) -> None:
        atomic_write_text(path, json.dumps(asdict(self), indent=2))

    @classmethod
    def load(cls, path: Path) -> AppSettings:
        if not path.exists():
            return cls()
        raw: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        known = {field.name for field in fields(cls)}
        values = {key: value for key, value in raw.items() if key in known}
        return cls(**values)
