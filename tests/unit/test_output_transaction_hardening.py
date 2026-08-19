import hashlib
import json
import os
from pathlib import Path

import pytest

import docmergeforge.utilities.output_transaction as output_transaction
from docmergeforge.core.exceptions import TransactionRecoveryError
from docmergeforge.utilities.output_transaction import (
    JOURNAL_FILENAME,
    OutputTransaction,
    pending_output_transactions,
    recover_interrupted_output_transactions,
)


def _entry(
    *,
    staging_name: str = "000-master.pdf",
    final_relative: str = "master.pdf",
    overwrite: object = True,
    had_existing: object = False,
    backup_name: object = None,
    staged_data: bytes = b"result",
    staged_size: object | None = None,
    staged_sha256: object | None = None,
) -> dict[str, object]:
    return {
        "staging_name": staging_name,
        "final_relative": final_relative,
        "overwrite": overwrite,
        "had_existing": had_existing,
        "backup_name": backup_name,
        "staged_size": len(staged_data) if staged_size is None else staged_size,
        "staged_sha256": (
            hashlib.sha256(staged_data).hexdigest()
            if staged_sha256 is None
            else staged_sha256
        ),
    }


def _journal(folder: Path, *, phase: object = "promoting", entries: object) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    (folder / JOURNAL_FILENAME).write_text(
        json.dumps({"version": 1, "phase": phase, "entries": entries}),
        encoding="utf-8",
    )


def test_transaction_rejects_duplicate_staged_target(tmp_path: Path) -> None:
    requested = tmp_path / "master.pdf"

    with OutputTransaction(tmp_path) as transaction:
        transaction.stage(requested, overwrite=False)
        with pytest.raises(ValueError, match="already staged"):
            transaction.stage(requested, overwrite=False)


def test_transaction_preserves_case_distinct_targets_on_posix(tmp_path: Path) -> None:
    if os.path.normcase("A") == os.path.normcase("a"):
        pytest.skip("Case-distinct output targets are not supported on this platform.")

    with OutputTransaction(tmp_path) as transaction:
        first = transaction.stage(tmp_path / "Master.pdf", overwrite=False)
        second = transaction.stage(tmp_path / "master.pdf", overwrite=False)

    assert first.final_path != second.final_path


def test_transaction_fsync_failure_does_not_publish(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "master.pdf"
    target.write_bytes(b"published")

    def failing_fsync(path: Path) -> None:
        del path
        raise OSError("simulated staged-output fsync failure")

    monkeypatch.setattr(output_transaction, "fsync_completed_file", failing_fsync)

    with OutputTransaction(tmp_path) as transaction:
        entry = transaction.stage(target, overwrite=True)
        entry.staging_path.write_bytes(b"replacement")
        with pytest.raises(OSError, match="simulated staged-output fsync failure"):
            transaction.promote()

    assert target.read_bytes() == b"published"
    assert not list(tmp_path.glob(".docmergeforge-staging-*"))


def test_recovery_rejects_parent_directory_child_reference(tmp_path: Path) -> None:
    folder = tmp_path / ".docmergeforge-staging-corrupt"
    _journal(folder, entries=[_entry(staging_name="..")])

    with pytest.raises(TransactionRecoveryError, match="Unsafe transaction journal child path"):
        recover_interrupted_output_transactions(tmp_path)

    assert folder.exists()


def test_recovery_rejects_string_boolean_in_journal(tmp_path: Path) -> None:
    folder = tmp_path / ".docmergeforge-staging-types"
    _journal(folder, entries=[_entry(had_existing="false")])

    with pytest.raises(TransactionRecoveryError, match="had_existing.*boolean"):
        recover_interrupted_output_transactions(tmp_path)

    assert folder.exists()


def test_recovery_rejects_non_string_phase_without_type_error(tmp_path: Path) -> None:
    folder = tmp_path / ".docmergeforge-staging-phase"
    _journal(folder, phase=["promoting"], entries=[_entry()])

    with pytest.raises(TransactionRecoveryError, match="Invalid transaction recovery phase"):
        recover_interrupted_output_transactions(tmp_path)

    assert folder.exists()


def test_recovery_rejects_non_hex_fingerprint(tmp_path: Path) -> None:
    folder = tmp_path / ".docmergeforge-staging-digest"
    _journal(folder, entries=[_entry(staged_sha256="z" * 64)])

    with pytest.raises(TransactionRecoveryError, match="fingerprint is invalid"):
        recover_interrupted_output_transactions(tmp_path)

    assert folder.exists()


def test_recovery_rejects_output_folder_as_final_target(tmp_path: Path) -> None:
    folder = tmp_path / ".docmergeforge-staging-final"
    _journal(folder, entries=[_entry(final_relative=".")])

    with pytest.raises(TransactionRecoveryError, match="outside the output folder"):
        recover_interrupted_output_transactions(tmp_path)

    assert folder.exists()


def test_recovery_rejects_duplicate_final_targets_before_mutation(tmp_path: Path) -> None:
    folder = tmp_path / ".docmergeforge-staging-duplicates"
    _journal(
        folder,
        entries=[
            _entry(staging_name="000-master.pdf"),
            _entry(staging_name="001-master.pdf"),
        ],
    )

    with pytest.raises(TransactionRecoveryError, match="same output more than once"):
        recover_interrupted_output_transactions(tmp_path)

    assert folder.exists()
    assert not (tmp_path / "master.pdf").exists()


def test_pending_transactions_do_not_follow_symlinked_staging_directory(tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / JOURNAL_FILENAME).write_text("{}", encoding="utf-8")
    link = tmp_path / ".docmergeforge-staging-link"
    try:
        link.symlink_to(outside, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"Directory symlinks are unavailable: {exc}")

    assert pending_output_transactions(tmp_path) == []
