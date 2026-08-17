import hashlib
import json
from pathlib import Path

import pytest

import docmergeforge.utilities.output_transaction as output_transaction
from docmergeforge.core.exceptions import MergeCancelled, TransactionRecoveryError
from docmergeforge.utilities.output_transaction import (
    JOURNAL_FILENAME,
    OutputTransaction,
    recover_interrupted_output_transactions,
)


def _journal_entry(
    staging_name: str,
    final_relative: str,
    staged_data: bytes,
    *,
    had_existing: bool,
    backup_name: str | None,
) -> dict[str, object]:
    return {
        "staging_name": staging_name,
        "final_relative": final_relative,
        "overwrite": True,
        "had_existing": had_existing,
        "backup_name": backup_name,
        "staged_size": len(staged_data),
        "staged_sha256": hashlib.sha256(staged_data).hexdigest(),
    }


def _write_journal(
    transaction_folder: Path,
    phase: str,
    entries: list[dict[str, object]],
) -> None:
    (transaction_folder / JOURNAL_FILENAME).write_text(
        json.dumps({"version": 1, "phase": phase, "entries": entries}),
        encoding="utf-8",
    )


def test_output_transaction_promotes_multiple_files_together(tmp_path: Path) -> None:
    first = tmp_path / "master.pdf"
    second = tmp_path / "master.docx"

    with OutputTransaction(tmp_path) as transaction:
        first_entry = transaction.stage(first, overwrite=False)
        second_entry = transaction.stage(second, overwrite=False)
        first_entry.staging_path.write_bytes(b"pdf-result")
        second_entry.staging_path.write_bytes(b"docx-result")
        transaction.promote()

    assert first.read_bytes() == b"pdf-result"
    assert second.read_bytes() == b"docx-result"
    assert not list(tmp_path.glob(".docmergeforge-staging-*"))


def test_output_transaction_cancellation_keeps_published_files_untouched(tmp_path: Path) -> None:
    published = tmp_path / "master.pdf"
    published.write_bytes(b"existing-result")

    with pytest.raises(MergeCancelled), OutputTransaction(tmp_path) as transaction:
        entry = transaction.stage(published, overwrite=True)
        entry.staging_path.write_bytes(b"unfinished-result")
        raise MergeCancelled("cancelled")

    assert published.read_bytes() == b"existing-result"
    assert not list(tmp_path.glob(".docmergeforge-staging-*"))


def test_output_transaction_rolls_back_if_batch_promotion_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    first = tmp_path / "master.pdf"
    second = tmp_path / "master.docx"
    first.write_bytes(b"old-pdf")
    second.write_bytes(b"old-docx")
    original_replace = output_transaction.os.replace

    def fail_second_staged_replace(source: str | Path, destination: str | Path) -> None:
        if Path(source).name.startswith("001-"):
            raise OSError("simulated promotion failure")
        original_replace(source, destination)

    monkeypatch.setattr(output_transaction.os, "replace", fail_second_staged_replace)

    with OutputTransaction(tmp_path) as transaction:
        first_entry = transaction.stage(first, overwrite=True)
        second_entry = transaction.stage(second, overwrite=True)
        first_entry.staging_path.write_bytes(b"new-pdf")
        second_entry.staging_path.write_bytes(b"new-docx")
        with pytest.raises(OSError, match="simulated promotion failure"):
            transaction.promote()

    assert first.read_bytes() == b"old-pdf"
    assert second.read_bytes() == b"old-docx"
    assert not list(tmp_path.glob(".docmergeforge-staging-*"))


def test_output_transaction_detects_version_reservation_race(tmp_path: Path) -> None:
    requested = tmp_path / "master.pdf"

    with OutputTransaction(tmp_path) as transaction:
        entry = transaction.stage(requested, overwrite=False)
        entry.staging_path.write_bytes(b"result")
        entry.final_path.write_bytes(b"other-process")
        with pytest.raises(FileExistsError, match="became occupied"):
            transaction.promote()

    assert requested.read_bytes() == b"other-process"


def test_output_transaction_rejects_target_outside_destination(tmp_path: Path) -> None:
    output = tmp_path / "output"
    outside = tmp_path / "outside.pdf"

    with OutputTransaction(output) as transaction:
        with pytest.raises(ValueError, match="must stay inside"):
            transaction.stage(outside, overwrite=True)


def test_interrupted_promotion_restores_previous_bundle(tmp_path: Path) -> None:
    transaction_folder = tmp_path / ".docmergeforge-staging-crash"
    transaction_folder.mkdir()
    pdf = tmp_path / "master.pdf"
    docx = tmp_path / "master.docx"
    new_pdf = b"new-pdf"
    new_docx = b"new-docx"

    pdf.write_bytes(new_pdf)
    (transaction_folder / "001-master.docx").write_bytes(new_docx)
    (transaction_folder / "backup-000-master.pdf").write_bytes(b"old-pdf")
    (transaction_folder / "backup-001-master.docx").write_bytes(b"old-docx")
    _write_journal(
        transaction_folder,
        "promoting",
        [
            _journal_entry(
                "000-master.pdf",
                "master.pdf",
                new_pdf,
                had_existing=True,
                backup_name="backup-000-master.pdf",
            ),
            _journal_entry(
                "001-master.docx",
                "master.docx",
                new_docx,
                had_existing=True,
                backup_name="backup-001-master.docx",
            ),
        ],
    )

    results = recover_interrupted_output_transactions(tmp_path)

    assert len(results) == 1
    assert results[0].status == "rolled-back"
    assert pdf.read_bytes() == b"old-pdf"
    assert docx.read_bytes() == b"old-docx"
    assert not transaction_folder.exists()


def test_interrupted_new_output_is_removed(tmp_path: Path) -> None:
    transaction_folder = tmp_path / ".docmergeforge-staging-new-output"
    transaction_folder.mkdir()
    final = tmp_path / "new-report.json"
    staged = b"new-report"
    final.write_bytes(staged)
    _write_journal(
        transaction_folder,
        "promoting",
        [
            _journal_entry(
                "000-new-report.json",
                "new-report.json",
                staged,
                had_existing=False,
                backup_name=None,
            )
        ],
    )

    results = recover_interrupted_output_transactions(tmp_path)

    assert results[0].removed_paths == (final,)
    assert not final.exists()
    assert not transaction_folder.exists()


def test_committed_journal_cleanup_keeps_published_output(tmp_path: Path) -> None:
    transaction_folder = tmp_path / ".docmergeforge-staging-committed"
    transaction_folder.mkdir()
    final = tmp_path / "master.pdf"
    staged = b"committed-pdf"
    final.write_bytes(staged)
    (transaction_folder / "backup-000-master.pdf").write_bytes(b"old-pdf")
    _write_journal(
        transaction_folder,
        "committed",
        [
            _journal_entry(
                "000-master.pdf",
                "master.pdf",
                staged,
                had_existing=True,
                backup_name="backup-000-master.pdf",
            )
        ],
    )

    results = recover_interrupted_output_transactions(tmp_path)

    assert results[0].status == "cleaned-committed"
    assert final.read_bytes() == staged
    assert not transaction_folder.exists()


def test_recovery_refuses_to_overwrite_changed_file(tmp_path: Path) -> None:
    transaction_folder = tmp_path / ".docmergeforge-staging-conflict"
    transaction_folder.mkdir()
    final = tmp_path / "master.pdf"
    staged = b"transaction-pdf"
    final.write_bytes(b"changed-after-crash")
    (transaction_folder / "backup-000-master.pdf").write_bytes(b"old-pdf")
    _write_journal(
        transaction_folder,
        "promoting",
        [
            _journal_entry(
                "000-master.pdf",
                "master.pdf",
                staged,
                had_existing=True,
                backup_name="backup-000-master.pdf",
            )
        ],
    )

    with pytest.raises(TransactionRecoveryError, match="no longer matches"):
        recover_interrupted_output_transactions(tmp_path)

    assert final.read_bytes() == b"changed-after-crash"
    assert transaction_folder.exists()


def test_pending_journal_blocks_new_transaction(tmp_path: Path) -> None:
    transaction_folder = tmp_path / ".docmergeforge-staging-pending"
    transaction_folder.mkdir()
    (transaction_folder / JOURNAL_FILENAME).write_text("{}", encoding="utf-8")

    with pytest.raises(TransactionRecoveryError, match="Recover it before starting"):
        with OutputTransaction(tmp_path):
            pass
