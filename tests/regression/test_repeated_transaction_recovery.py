from pathlib import Path

import pytest

from docmergeforge.core.exceptions import MergeCancelled
from docmergeforge.utilities.output_transaction import OutputTransaction


@pytest.mark.regression
def test_repeated_cancellation_preserves_last_published_bundle(tmp_path: Path) -> None:
    pdf = tmp_path / "master.pdf"
    docx = tmp_path / "master.docx"
    pdf.write_bytes(b"published-pdf")
    docx.write_bytes(b"published-docx")

    for cycle in range(25):
        with pytest.raises(MergeCancelled), OutputTransaction(tmp_path) as transaction:
            pdf_entry = transaction.stage(pdf, overwrite=True)
            docx_entry = transaction.stage(docx, overwrite=True)
            pdf_entry.staging_path.write_bytes(f"cancelled-pdf-{cycle}".encode())
            docx_entry.staging_path.write_bytes(f"cancelled-docx-{cycle}".encode())
            raise MergeCancelled(f"cancel cycle {cycle}")

        assert pdf.read_bytes() == b"published-pdf"
        assert docx.read_bytes() == b"published-docx"
        assert not list(tmp_path.glob(".docmergeforge-staging-*"))

    with OutputTransaction(tmp_path) as transaction:
        pdf_entry = transaction.stage(pdf, overwrite=True)
        docx_entry = transaction.stage(docx, overwrite=True)
        pdf_entry.staging_path.write_bytes(b"recovered-pdf")
        docx_entry.staging_path.write_bytes(b"recovered-docx")
        transaction.promote()

    assert pdf.read_bytes() == b"recovered-pdf"
    assert docx.read_bytes() == b"recovered-docx"
    assert not list(tmp_path.glob(".docmergeforge-staging-*"))
