from pathlib import Path

import pytest

docx = pytest.importorskip("docx")
pytest.importorskip("docxcompose")

from docmergeforge.core.models import DocumentKind, DocxSettings, InputDocument, PartIdentity
from docmergeforge.docx.engine import DocxMergeEngine
from docmergeforge.utilities.hashing import sha256_file


@pytest.mark.integration
def test_docx_merge_reopens_and_preserves_sources(tmp_path: Path) -> None:
    docs = []
    hashes = {}
    for part in range(1, 4):
        path = tmp_path / f"Part {part}.docx"
        document = docx.Document()
        document.add_heading(f"Part {part}", level=1)
        document.add_paragraph(f"Unique marker {part}")
        document.save(path)
        digest = sha256_file(path)
        hashes[path] = digest
        docs.append(InputDocument(path, DocumentKind.DOCX, PartIdentity(part, f"Part {part}"), path.stat().st_size, digest))

    output = tmp_path / "master.docx"
    DocxMergeEngine().merge(docs, output, DocxSettings())
    reopened = docx.Document(str(output))
    text = "\\n".join(p.text for p in reopened.paragraphs)
    assert "Unique marker 1" in text and "Unique marker 3" in text
    assert all(sha256_file(path) == digest for path, digest in hashes.items())
