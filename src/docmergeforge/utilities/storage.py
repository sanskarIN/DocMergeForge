from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from docmergeforge.core.exceptions import InsufficientStorageError


@dataclass(slots=True, frozen=True)
class StorageEstimate:
    source_bytes: int
    projected_output_bytes: int
    temporary_bytes: int
    safe_required_bytes: int
    free_bytes: int

    @property
    def sufficient(self) -> bool:
        return self.free_bytes >= self.safe_required_bytes


def estimate_storage(paths: list[Path], output_folder: Path) -> StorageEstimate:
    source = sum(path.stat().st_size for path in paths if path.exists())
    projected = max(source, 1)
    temporary = int(projected * 1.25)
    safe = projected + temporary + 128 * 1024 * 1024
    free = shutil.disk_usage(output_folder if output_folder.exists() else output_folder.parent).free
    return StorageEstimate(source, projected, temporary, safe, free)


def require_storage(paths: list[Path], output_folder: Path) -> StorageEstimate:
    estimate = estimate_storage(paths, output_folder)
    if not estimate.sufficient:
        raise InsufficientStorageError(
            f"Not enough free disk space. Need about {estimate.safe_required_bytes} bytes; "
            f"{estimate.free_bytes} bytes available."
        )
    return estimate
