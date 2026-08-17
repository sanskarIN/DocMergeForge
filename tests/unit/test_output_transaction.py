from pathlib import Path

import pytest

import docmergeforge.utilities.output_transaction as output_transaction
from docmergeforge.core.exceptions import MergeCancelled
from docmergeforge.utilities.output_transaction import OutputTransaction


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
