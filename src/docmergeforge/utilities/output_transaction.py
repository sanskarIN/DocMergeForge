from __future__ import annotations

import json
import os
import shutil
import tempfile
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType
from typing import Any, Self

from docmergeforge.core.exceptions import TransactionRecoveryError
from docmergeforge.utilities.atomic import versioned_path
from docmergeforge.utilities.hashing import sha256_file

STAGING_PREFIX = ".docmergeforge-staging-"
JOURNAL_FILENAME = "transaction.json"
JOURNAL_VERSION = 1
JOURNAL_PHASES = {"promoting", "committed", "rolled-back"}


@dataclass(slots=True, frozen=True)
class StagedOutput:
    staging_path: Path
    final_path: Path
    overwrite: bool


@dataclass(slots=True, frozen=True)
class RecoveryResult:
    transaction_folder: Path
    status: str
    restored_paths: tuple[Path, ...] = ()
    removed_paths: tuple[Path, ...] = ()


def _is_within(path: Path, folder: Path) -> bool:
    try:
        path.resolve().relative_to(folder.resolve())
    except ValueError:
        return False
    return True


def _safe_child(folder: Path, name: str) -> Path:
    candidate = Path(name)
    if candidate.is_absolute() or candidate.name != name:
        raise TransactionRecoveryError(f"Unsafe transaction journal child path: {name!r}")
    return folder / candidate


def _safe_final(output_folder: Path, relative_name: str) -> Path:
    candidate = output_folder / relative_name
    if not _is_within(candidate, output_folder):
        raise TransactionRecoveryError(
            f"Transaction journal references a path outside the output folder: {relative_name!r}"
        )
    return candidate


def _matches_staged_fingerprint(path: Path, size: int, digest: str) -> bool:
    try:
        return path.is_file() and path.stat().st_size == size and sha256_file(path) == digest
    except OSError:
        return False


def pending_output_transactions(output_folder: Path) -> list[Path]:
    if not output_folder.is_dir():
        return []
    return sorted(
        path
        for path in output_folder.glob(f"{STAGING_PREFIX}*")
        if path.is_dir() and (path / JOURNAL_FILENAME).is_file()
    )


def _load_journal(transaction_folder: Path) -> dict[str, Any]:
    journal_path = transaction_folder / JOURNAL_FILENAME
    try:
        payload = json.loads(journal_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise TransactionRecoveryError(
            f"Could not read transaction recovery journal: {journal_path}: {exc}"
        ) from exc
    if not isinstance(payload, dict) or payload.get("version") != JOURNAL_VERSION:
        raise TransactionRecoveryError(f"Unsupported transaction recovery journal: {journal_path}")
    if payload.get("phase") not in JOURNAL_PHASES:
        raise TransactionRecoveryError(f"Invalid transaction recovery phase in: {journal_path}")
    entries = payload.get("entries")
    if not isinstance(entries, list) or not entries:
        raise TransactionRecoveryError(
            f"Transaction recovery journal has no output entries: {journal_path}"
        )
    return payload


def _recover_promoting_transaction(
    output_folder: Path,
    transaction_folder: Path,
    payload: dict[str, Any],
) -> RecoveryResult:
    actions: list[tuple[str, Path, Path | None]] = []

    for raw in payload["entries"]:
        if not isinstance(raw, dict):
            raise TransactionRecoveryError("Transaction journal entry is not an object.")
        try:
            staging_name = str(raw["staging_name"])
            final_relative = str(raw["final_relative"])
            had_existing = bool(raw["had_existing"])
            staged_size = int(raw["staged_size"])
            staged_sha256 = str(raw["staged_sha256"])
            backup_name = raw.get("backup_name")
        except (KeyError, TypeError, ValueError) as exc:
            raise TransactionRecoveryError("Transaction journal entry is incomplete.") from exc

        if staged_size < 0 or len(staged_sha256) != 64:
            raise TransactionRecoveryError("Transaction journal fingerprint is invalid.")

        staging = _safe_child(transaction_folder, staging_name)
        final = _safe_final(output_folder, final_relative)
        backup = (
            _safe_child(transaction_folder, str(backup_name)) if backup_name is not None else None
        )

        if backup is not None and backup.exists():
            if final.exists() and not _matches_staged_fingerprint(
                final,
                staged_size,
                staged_sha256,
            ):
                raise TransactionRecoveryError(
                    "Recovery stopped because a published path no longer matches the "
                    f"interrupted transaction: {final}"
                )
            actions.append(("restore", final, backup))
            continue

        if had_existing:
            if not staging.exists():
                raise TransactionRecoveryError(
                    "Recovery cannot restore a previous output because both its staging "
                    f"file and rollback backup are unavailable: {final}"
                )
            if not final.exists():
                raise TransactionRecoveryError(
                    f"Recovery expected the previous published output to still exist: {final}"
                )
            actions.append(("keep", final, None))
            continue

        if staging.exists():
            actions.append(("keep", final, None))
            continue

        if final.exists():
            if not _matches_staged_fingerprint(final, staged_size, staged_sha256):
                raise TransactionRecoveryError(
                    "Recovery stopped rather than deleting a file that does not match the "
                    f"interrupted transaction: {final}"
                )
            actions.append(("remove", final, None))
        else:
            actions.append(("keep", final, None))

    restored: list[Path] = []
    removed: list[Path] = []
    for action, final, backup in actions:
        if action == "restore":
            if backup is None:
                raise TransactionRecoveryError("Internal recovery action is missing a backup.")
            final.unlink(missing_ok=True)
            final.parent.mkdir(parents=True, exist_ok=True)
            os.replace(backup, final)
            restored.append(final)
        elif action == "remove":
            final.unlink(missing_ok=True)
            removed.append(final)

    shutil.rmtree(transaction_folder)
    return RecoveryResult(
        transaction_folder,
        "rolled-back",
        tuple(restored),
        tuple(removed),
    )


def recover_interrupted_output_transactions(output_folder: Path) -> list[RecoveryResult]:
    """Recover journaled output transactions after an interrupted process.

    A journal marked ``promoting`` is rolled back to the pre-publication state. Journals
    marked ``committed`` or ``rolled-back`` are already at a safe boundary, so only stale
    staging data is removed. Corrupt or conflicting journals are left untouched and fail
    closed.
    """

    results: list[RecoveryResult] = []
    for transaction_folder in pending_output_transactions(output_folder):
        payload = _load_journal(transaction_folder)
        if payload["phase"] in {"committed", "rolled-back"}:
            phase = str(payload["phase"])
            shutil.rmtree(transaction_folder)
            results.append(RecoveryResult(transaction_folder, f"cleaned-{phase}"))
            continue
        results.append(
            _recover_promoting_transaction(
                output_folder,
                transaction_folder,
                payload,
            )
        )
    return results


class OutputTransaction:
    """Stage one or more output files and publish them as a single batch."""

    def __init__(self, output_folder: Path) -> None:
        self.output_folder = output_folder
        self._staging_folder: Path | None = None
        self._entries: list[StagedOutput] = []
        self._committed = False

    def __enter__(self) -> Self:
        self.output_folder.mkdir(parents=True, exist_ok=True)
        pending = pending_output_transactions(self.output_folder)
        if pending:
            raise TransactionRecoveryError(
                "Interrupted publication transaction detected. Recover it before starting "
                f"another merge: {pending[0]}"
            )
        self._staging_folder = Path(tempfile.mkdtemp(prefix=STAGING_PREFIX, dir=self.output_folder))
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        del exc_type, exc, traceback
        if self._staging_folder is None:
            return

        folder = self._staging_folder
        self._staging_folder = None
        journal = folder / JOURNAL_FILENAME
        if journal.exists() and not self._committed:
            try:
                payload = _load_journal(folder)
            except TransactionRecoveryError:
                return
            if payload["phase"] == "promoting":
                return
        shutil.rmtree(folder, ignore_errors=True)

    def stage(self, requested_path: Path, *, overwrite: bool) -> StagedOutput:
        if self._staging_folder is None:
            raise RuntimeError("OutputTransaction must be entered before staging outputs.")
        if self._committed:
            raise RuntimeError("Cannot stage more outputs after transaction promotion.")

        final_path = requested_path if overwrite else versioned_path(requested_path)
        if not _is_within(final_path, self.output_folder):
            raise ValueError(
                f"Output transaction target must stay inside {self.output_folder}: {final_path}"
            )
        staging_path = self._staging_folder / f"{len(self._entries):03d}-{final_path.name}"
        entry = StagedOutput(staging_path, final_path, overwrite)
        self._entries.append(entry)
        return entry

    def _write_journal(self, phase: str, entries: list[dict[str, object]]) -> None:
        if self._staging_folder is None:
            raise RuntimeError("OutputTransaction must be entered before journaling.")
        payload = {
            "version": JOURNAL_VERSION,
            "phase": phase,
            "entries": entries,
        }
        journal = self._staging_folder / JOURNAL_FILENAME
        temporary = journal.with_suffix(".json.tmp")
        with temporary.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, journal)

    def promote(self) -> None:
        if self._staging_folder is None:
            raise RuntimeError("OutputTransaction must be entered before promotion.")
        if self._committed:
            raise RuntimeError("OutputTransaction has already been promoted.")
        if not self._entries:
            raise RuntimeError("OutputTransaction has no staged outputs to promote.")

        journal_entries: list[dict[str, object]] = []
        for index, entry in enumerate(self._entries):
            if not entry.staging_path.exists() or entry.staging_path.stat().st_size == 0:
                raise RuntimeError(f"Staged output is missing or empty: {entry.staging_path}")
            if not entry.overwrite and entry.final_path.exists():
                raise FileExistsError(
                    f"Reserved output path became occupied before promotion: {entry.final_path}"
                )
            had_existing = entry.final_path.exists()
            backup_name = (
                f"backup-{index:03d}-{entry.final_path.name}"
                if entry.overwrite and had_existing
                else None
            )
            final_relative = str(
                entry.final_path.resolve().relative_to(self.output_folder.resolve())
            )
            journal_entries.append(
                {
                    "staging_name": entry.staging_path.name,
                    "final_relative": final_relative,
                    "overwrite": entry.overwrite,
                    "had_existing": had_existing,
                    "backup_name": backup_name,
                    "staged_size": entry.staging_path.stat().st_size,
                    "staged_sha256": sha256_file(entry.staging_path),
                }
            )

        self._write_journal("promoting", journal_entries)
        backups: dict[Path, Path] = {}
        promoted: list[Path] = []
        try:
            for raw, entry in zip(journal_entries, self._entries, strict=True):
                entry.final_path.parent.mkdir(parents=True, exist_ok=True)
                journal_backup_name = raw["backup_name"]
                if isinstance(journal_backup_name, str):
                    backup = self._staging_folder / journal_backup_name
                    os.replace(entry.final_path, backup)
                    backups[entry.final_path] = backup

            for entry in self._entries:
                os.replace(entry.staging_path, entry.final_path)
                promoted.append(entry.final_path)

            self._write_journal("committed", journal_entries)
        except Exception:
            try:
                for path in reversed(promoted):
                    path.unlink(missing_ok=True)
                for final_path, backup in backups.items():
                    if backup.exists():
                        os.replace(backup, final_path)
                self._write_journal("rolled-back", journal_entries)
            except Exception as rollback_error:
                raise TransactionRecoveryError(
                    "Publication failed and automatic rollback was incomplete. Recovery "
                    f"evidence was preserved in {self._staging_folder}."
                ) from rollback_error
            raise

        for backup in backups.values():
            with suppress(OSError):
                backup.unlink(missing_ok=True)
        self._committed = True
