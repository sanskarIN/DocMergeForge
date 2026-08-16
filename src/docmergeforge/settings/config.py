from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


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

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> AppSettings:
        if not path.exists():
            return cls()
        return cls(**json.loads(path.read_text(encoding="utf-8")))
