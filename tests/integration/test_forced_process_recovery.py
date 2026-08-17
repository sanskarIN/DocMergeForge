from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from docmergeforge.utilities.output_lock import OutputDirectoryLock
from docmergeforge.utilities.output_transaction import (
    pending_output_transactions,
    recover_interrupted_output_transactions,
)


@pytest.mark.integration
def test_forced_process_exit_during_promotion_restores_previous_bundle(tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    pdf = output_dir / "Book.pdf"
    report = output_dir / "Merge_Report.md"
    pdf.write_bytes(b"previous-pdf-publication")
    report.write_text("previous-report-publication", encoding="utf-8")

    helper = Path(__file__).resolve().parents[1] / "helpers" / "crash_during_promotion.py"
    completed = subprocess.run(
        [sys.executable, str(helper), str(output_dir)],
        check=False,
        timeout=30,
    )

    assert completed.returncode == 97
    pending = pending_output_transactions(output_dir)
    assert len(pending) == 1
    assert (pending[0] / "transaction.json").is_file()

    results = recover_interrupted_output_transactions(output_dir)

    assert len(results) == 1
    assert results[0].status == "rolled-back"
    assert pdf.read_bytes() == b"previous-pdf-publication"
    assert report.read_text(encoding="utf-8") == "previous-report-publication"
    assert pending_output_transactions(output_dir) == []

    with OutputDirectoryLock(output_dir) as lock:
        assert lock.acquired
