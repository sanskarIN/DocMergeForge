from pathlib import Path

import pytest

from docmergeforge.core.exceptions import ValidationError
from docmergeforge.core.models import (
    DocumentKind,
    InputDocument,
    PartIdentity,
    PdfSettings,
)
from docmergeforge.pdf.engine import PdfMergeEngine
from docmergeforge.utilities.hashing import sha256_file


@pytest.mark.integration
def test_pdf_merge_preserves_page_count_and_sources(tmp_path: Path) -> None:
    pypdf = pytest.importorskip("pypdf")
    docs: list[InputDocument] = []
    source_hashes: dict[Path, str] = {}
    for part in range(1, 4):
        path = tmp_path / f"Part {part}.pdf"
        writer = pypdf.PdfWriter()
        writer.add_blank_page(width=612, height=792)
        with path.open("wb") as handle:
            writer.write(handle)
        digest = sha256_file(path)
        source_hashes[path] = digest
        docs.append(
            InputDocument(
                path,
                DocumentKind.PDF,
                PartIdentity(part, f"Part {part}"),
                path.stat().st_size,
                digest,
                1,
            )
        )

    output = tmp_path / "master.pdf"
    PdfMergeEngine().merge(docs, output, PdfSettings(title="Test"))
    reader = pypdf.PdfReader(str(output))
    assert len(reader.pages) == 3
    assert all(sha256_file(path) == digest for path, digest in source_hashes.items())


@pytest.mark.integration
def test_pdf_merge_does_not_promote_output_if_source_changes(tmp_path: Path) -> None:
    pypdf = pytest.importorskip("pypdf")
    source = tmp_path / "Part 1.pdf"
    writer = pypdf.PdfWriter()
    writer.add_blank_page(width=612, height=792)
    with source.open("wb") as handle:
        writer.write(handle)
    document = InputDocument(
        source,
        DocumentKind.PDF,
        PartIdentity(1, "Part 1"),
        source.stat().st_size,
        sha256_file(source),
        1,
    )
    output = tmp_path / "master.pdf"

    def mutate_source(_index: int, _total: int, path: Path) -> None:
        path.write_bytes(path.read_bytes() + b"\nchanged")

    with pytest.raises(ValidationError, match="Source integrity violation"):
        PdfMergeEngine().merge(
            [document],
            output,
            PdfSettings(),
            progress=mutate_source,
        )

    assert not output.exists()


@pytest.mark.integration
def test_pdf_merge_can_preserve_confirmed_manual_order(tmp_path: Path) -> None:
    pypdf = pytest.importorskip("pypdf")
    docs: list[InputDocument] = []
    for part, width in ((1, 300), (2, 500)):
        path = tmp_path / f"Part {part}.pdf"
        writer = pypdf.PdfWriter()
        writer.add_blank_page(width=width, height=700)
        with path.open("wb") as handle:
            writer.write(handle)
        docs.append(
            InputDocument(
                path,
                DocumentKind.PDF,
                PartIdentity(part, f"Part {part}"),
                path.stat().st_size,
                sha256_file(path),
                1,
            )
        )

    output = tmp_path / "manual-order.pdf"
    PdfMergeEngine().merge(
        [docs[1], docs[0]],
        output,
        PdfSettings(add_part_bookmarks=False),
        preserve_order=True,
    )

    reader = pypdf.PdfReader(str(output))
    assert float(reader.pages[0].mediabox.width) == 500
    assert float(reader.pages[1].mediabox.width) == 300
