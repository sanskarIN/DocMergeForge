from __future__ import annotations

import os
import shutil
import tempfile
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path

from docmergeforge.core.exceptions import InsufficientStorageError, OutputAccessError


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


def _existing_anchor(path: Path) -> Path:
    candidate = path
    while not candidate.exists() and candidate != candidate.parent:
        candidate = candidate.parent
    return candidate


def require_output_writable(output_folder: Path) -> None:
    """Verify that the destination can host transaction staging before merge work starts."""

    probe_path: Path | None = None
    try:
        output_folder.mkdir(parents=True, exist_ok=True)
        descriptor, raw_path = tempfile.mkstemp(
            prefix=".docmergeforge-write-probe-",
            dir=output_folder,
        )
        probe_path = Path(raw_path)
        os.close(descriptor)
    except OSError as exc:
        raise OutputAccessError(
            f"Output folder is not writable: {output_folder}: {exc}"
        ) from exc
    finally:
        if probe_path is not None:
            with suppress(OSError):
                probe_path.unlink(missing_ok=True)


def estimate_storage(paths: list[Path], output_folder: Path) -> StorageEstimate:
    source = sum(path.stat().st_size for path in paths if path.exists())
    projected = max(source, 1)
    temporary = int(projected * 1.25)
    safe = projected + temporary + 128 * 1024 * 1024
    free = shutil.disk_usage(_existing_anchor(output_folder)).free
    return StorageEstimate(source, projected, temporary, safe, free)


def require_storage(paths: list[Path], output_folder: Path) -> StorageEstimate:
    require_output_writable(output_folder)
    estimate = estimate_storage(paths, output_folder)
    if not estimate.sufficient:
        raise InsufficientStorageError(
            f"Not enough free disk space. Need about {estimate.safe_required_bytes} bytes; "
            f"{estimate.free_bytes} bytes available."
        )
    return estimate
