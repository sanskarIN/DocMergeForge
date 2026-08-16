from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from docmergeforge.core.models import CompanionReference
from docmergeforge.utilities.hashing import sha256_file


@dataclass(slots=True, frozen=True)
class CompanionCopyResult:
    source: Path
    destination: Path
    sha256: str
    copied: bool


def copy_companion_packages(
    companions: list[CompanionReference],
    destination_root: Path,
) -> list[CompanionCopyResult]:
    """Copy companion package files without extracting or modifying them."""
    destination_root.mkdir(parents=True, exist_ok=True)
    results: list[CompanionCopyResult] = []

    for companion in sorted(
        companions,
        key=lambda item: (item.part is None, item.part or 0, item.path.name.casefold()),
    ):
        if not companion.path.is_file():
            raise ValueError(f"Companion copy currently supports package files only: {companion.path}")
        before = sha256_file(companion.path)
        if before != companion.sha256:
            raise ValueError(f"Companion package changed since discovery: {companion.path}")

        folder_name = f"Part_{companion.part:03d}" if companion.part is not None else "Unnumbered"
        destination_dir = destination_root / folder_name
        destination_dir.mkdir(parents=True, exist_ok=True)
        destination = destination_dir / companion.path.name

        copied = True
        if destination.exists():
            if sha256_file(destination) != before:
                raise FileExistsError(
                    f"Refusing to overwrite different companion package: {destination}"
                )
            copied = False
        else:
            shutil.copy2(companion.path, destination)

        after_source = sha256_file(companion.path)
        after_destination = sha256_file(destination)
        if after_source != before or after_destination != before:
            destination.unlink(missing_ok=True)
            raise RuntimeError(f"Companion integrity verification failed: {companion.path}")

        results.append(
            CompanionCopyResult(
                source=companion.path,
                destination=destination,
                sha256=before,
                copied=copied,
            )
        )

    return results
