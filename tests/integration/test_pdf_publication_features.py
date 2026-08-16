from pathlib import Path

import pytest

from docmergeforge.core.models import DocumentKind, InputDocument, PartIdentity, PdfSettings
from docmergeforge.pdf.engine import PdfMergeEngine
from docmergeforge.utilities.hashing import sha256_file


@pytest.mark.integration
def test_pdf_front_matter_toc_and_page_overlay(tmp_path: Path) -> None:
    pypdf = pytest.importorskip("pypdf")
    pytest.importorskip("reportlab")
    inputs: list[InputDocument] = []
    for part in (1, 2):
        path = tmp_path / f"Part {part}.pdf"
        writer = pypdf.PdfWriter()
        writer.add_blank_page(width=612, height=792)
        with path.open("wb") as handle:
            writer.write(handle)
        inputs.append(
            InputDocument(
                path=path,
                kind=DocumentKind.PDF,
                part=PartIdentity(part, f"Part {part}", f"Title {part}"),
                size=path.stat().st_size,
                sha256=sha256_file(path),
                page_count=1,
            )
        )

    output = tmp_path / "master.pdf"
    settings = PdfSettings(
        title="Test Master",
        author="Ram Sandesh",
        edition="August 2026",
        include_title_page=True,
        visible_toc=True,
        page_numbers=True,
        footer_text="DocMergeForge",
        watermark_text="DRAFT",
    )
    PdfMergeEngine().merge(inputs, output, settings)

    reader = pypdf.PdfReader(str(output))
    assert len(reader.pages) == 4
    assert "Test Master" in (reader.pages[0].extract_text() or "")
    assert "Table of Contents" in (reader.pages[1].extract_text() or "")
    assert "DRAFT" in (reader.pages[2].extract_text() or "")
    assert reader.metadata.title == "Test Master"
