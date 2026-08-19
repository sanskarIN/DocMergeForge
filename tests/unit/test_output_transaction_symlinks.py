import hashlib
import json
from pathlib import Path

import pytest

from docmergeforge.core.exceptions import TransactionRecoveryError
from docmergeforge.utilities.output_transaction import (
    JOURNAL_FILENAME,
    recover_interrupted_output_transactions,
)


def _entry(*, backup_name: str | None = None, had_existing: bool = False) -> dict[str, object]:
    data = b"replacement"
    return {
        "staging_name": "000-master.pdf",
        "final_relative": "master.pdf",
        "overwrite": True,
        "had_existing": had_existing,
        "backup_name": backup_name,
        "staged_size": len(data),
        "staged_sha256": hashlib.sha256(data).hexdigest(),
    }


def _write_journal(folder: Path, entries: list[dict[str, object]]) -> None:
    (folder / JOURNAL_FILENAME).write_text(
        json.dumps({"version": 1, "phase": "promoting", "entries": entries}),
        encoding="utf-8",
    )


def test_recovery_refuses_symlinked_journal(tmp_path: Path) -> None:
    transaction = tmp_path / ".docmergeforge-staging-journal-link"
    transaction.mkdir()
    outside = tmp_path / "outside-journal.json"
    outside.write_text("{}", encoding="utf-8")
    try:
        (transaction / JOURNAL_FILENAME).symlink_to(outside)
    except OSError as exc:
        pytest.skip(f"File symlinks are unavailable: {exc}")

    with pytest.raises(TransactionRecoveryError, match="symlinked transaction recovery journal"):
        recover_interrupted_output_transactions(tmp_path)

    assert outside.read_text(encoding="utf-8") == "{}"
    assert transaction.exists()


def test_recovery_refuses_symlinked_backup_child(tmp_path: Path) -> None:
    transaction = tmp_path / ".docmergeforge-staging-backup-link"
    transaction.mkdir()
    staged = transaction / "000-master.pdf"
    staged.write_bytes(b"replacement")
    victim = tmp_path / "victim.pdf"
    victim.write_bytes(b"private-old-output")
    backup = transaction / "backup-000-master.pdf"
    try:
        backup.symlink_to(victim)
    except OSError as exc:
        pytest.skip(f"File symlinks are unavailable: {exc}")
    _write_journal(
        transaction,
        [_entry(backup_name=backup.name, had_existing=True)],
    )

    with pytest.raises(TransactionRecoveryError, match="must not be a symlink"):
        recover_interrupted_output_transactions(tmp_path)

    assert victim.read_bytes() == b"private-old-output"
    assert transaction.exists()
