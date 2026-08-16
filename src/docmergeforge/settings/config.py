from __future__ import annotations

import json
from dataclasses import asdict, dataclass, fields
from pathlib import Path
from typing import Any


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
    first_run_completed: bool = False

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = path.with_suffix(path.suffix + ".tmp")
        temp.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")
        temp.replace(path)

    @classmethod
    def load(cls, path: Path) -> AppSettings:
        if not path.exists():
            return cls()
        raw: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        known = {field.name for field in fields(cls)}
        values = {key: value for key, value in raw.items() if key in known}
        return cls(**values)
