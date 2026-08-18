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
        try:
            raw: object = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            return cls()
        if not isinstance(raw, dict):
            return cls()

        defaults = cls()
        values: dict[str, Any] = {}
        for field in fields(cls):
            if field.name not in raw:
                continue
            value = raw[field.name]
            default = getattr(defaults, field.name)
            if isinstance(default, bool):
                if isinstance(value, bool):
                    values[field.name] = value
            elif isinstance(default, int):
                if isinstance(value, int) and not isinstance(value, bool):
                    values[field.name] = value
            elif isinstance(default, str) and isinstance(value, str):
                values[field.name] = value

        loaded = cls(**values)
        loaded.worker_count = max(1, min(64, loaded.worker_count))
        loaded.text_scale_percent = max(80, min(200, loaded.text_scale_percent))

        allowed_strings = {
            "theme": {"system", "light", "dark"},
            "logging_level": {"DEBUG", "INFO", "WARNING", "ERROR"},
            "pdf_optimization": {"preserve", "balanced", "archive"},
            "docx_fidelity_mode": {"portable", "libreoffice", "word"},
            "merge_profile": {
                "Exact Preservation",
                "Master eBook",
                "Print Draft",
                "Archive",
                "Custom",
            },
        }
        for name, allowed in allowed_strings.items():
            if getattr(loaded, name) not in allowed:
                setattr(loaded, name, getattr(defaults, name))
        return loaded
