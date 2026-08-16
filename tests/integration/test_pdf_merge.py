from pathlib import Path

import pytest

pypdf = pytest.importorskip("pypdf")

from docmergeforge.core.models import DocumentKind, InputDocument, PartIdentity, PdfSettings
from docmergeforge.pdf.engine import PdfMergeEngine
from docmergeforge.utilities.hashing import sha256_file


@pytest.mark.integration
def test_pdf_merge_preserves_page_count_and_sources(tmp_path: Path) -> None:
    docs = []
    source_hashes = {}
    for part in range(1, 4):
        path = tmp_path / f"Part {part}.pdf"
        writer = pypdf.PdfWriter()
        writer.add_blank_page(width=612, height=792)
        with path.open("wb") as handle:
            writer.write(handle)
        digest = sha256_file(path)
        source_hashes[path] = digest
        docs.append(InputDocument(path, DocumentKind.PDF, PartIdentity(part, f"Part {part}"), path.stat().st_size, digest, 1))

    output = tmp_path / "master.pdf"
    PdfMergeEngine().merge(docs, output, PdfSettings(title="Test"))
    reader = pypdf.PdfReader(str(output))
    assert len(reader.pages) == 3
    assert all(sha256_file(path) == digest for path, digest in source_hashes.items())
