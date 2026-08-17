from __future__ import annotations

import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType
from typing import Self

from docmergeforge.utilities.atomic import versioned_path


@dataclass(slots=True, frozen=True)
class StagedOutput:
    staging_path: Path
    final_path: Path
    overwrite: bool


class OutputTransaction:
    """Stage one or more output files and publish them as a single batch."""

    def __init__(self, output_folder: Path) -> None:
        self.output_folder = output_folder
        self._staging_folder: Path | None = None
        self._entries: list[StagedOutput] = []
        self._committed = False

    def __enter__(self) -> Self:
        self.output_folder.mkdir(parents=True, exist_ok=True)
        self._staging_folder = Path(
            tempfile.mkdtemp(prefix=".docmergeforge-staging-", dir=self.output_folder)
        )
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        del exc_type, exc, traceback
        if self._staging_folder is not None:
            shutil.rmtree(self._staging_folder, ignore_errors=True)
            self._staging_folder = None

    def stage(self, requested_path: Path, *, overwrite: bool) -> StagedOutput:
        if self._staging_folder is None:
            raise RuntimeError("OutputTransaction must be entered before staging outputs.")
        if self._committed:
            raise RuntimeError("Cannot stage more outputs after transaction promotion.")

        final_path = requested_path if overwrite else versioned_path(requested_path)
        staging_path = self._staging_folder / f"{len(self._entries):03d}-{final_path.name}"
        entry = StagedOutput(staging_path, final_path, overwrite)
        self._entries.append(entry)
        return entry

    def promote(self) -> None:
        if self._staging_folder is None:
            raise RuntimeError("OutputTransaction must be entered before promotion.")
        if self._committed:
            raise RuntimeError("OutputTransaction has already been promoted.")

        for entry in self._entries:
            if not entry.staging_path.exists() or entry.staging_path.stat().st_size == 0:
                raise RuntimeError(f"Staged output is missing or empty: {entry.staging_path}")
            if not entry.overwrite and entry.final_path.exists():
                raise FileExistsError(
                    f"Reserved output path became occupied before promotion: {entry.final_path}"
                )

        backups: dict[Path, Path] = {}
        promoted: list[Path] = []
        try:
            for index, entry in enumerate(self._entries):
                entry.final_path.parent.mkdir(parents=True, exist_ok=True)
                if entry.overwrite and entry.final_path.exists():
                    backup = self._staging_folder / f"backup-{index:03d}-{entry.final_path.name}"
                    os.replace(entry.final_path, backup)
                    backups[entry.final_path] = backup

            for entry in self._entries:
                os.replace(entry.staging_path, entry.final_path)
                promoted.append(entry.final_path)
        except Exception:
            for path in reversed(promoted):
                path.unlink(missing_ok=True)
            for final_path, backup in backups.items():
                if backup.exists():
                    os.replace(backup, final_path)
            raise

        for backup in backups.values():
            backup.unlink(missing_ok=True)
        self._committed = True
