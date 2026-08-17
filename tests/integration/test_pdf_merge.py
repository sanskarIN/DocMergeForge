from pathlib import Path

import pytest

from docmergeforge.core.exceptions import MergeCancelled, ValidationError
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


@pytest.mark.integration
def test_pdf_merge_requires_and_accepts_in_memory_password(tmp_path: Path) -> None:
    pypdf = pytest.importorskip("pypdf")
    source = tmp_path / "Part 1.pdf"
    writer = pypdf.PdfWriter()
    writer.add_blank_page(width=612, height=792)
    writer.encrypt("local-secret")
    with source.open("wb") as handle:
        writer.write(handle)

    document = InputDocument(
        source,
        DocumentKind.PDF,
        PartIdentity(1, "Part 1"),
        source.stat().st_size,
        sha256_file(source),
        1,
        encrypted=True,
    )
    missing_output = tmp_path / "missing-password.pdf"
    with pytest.raises(ValidationError, match="requires a local password"):
        PdfMergeEngine().merge([document], missing_output, PdfSettings())
    assert not missing_output.exists()

    output = tmp_path / "decrypted-master.pdf"
    PdfMergeEngine().merge(
        [document],
        output,
        PdfSettings(),
        password_provider=lambda _path: "local-secret",
    )
    reader = pypdf.PdfReader(str(output))
    assert not reader.is_encrypted
    assert len(reader.pages) == 1


@pytest.mark.integration
def test_pdf_merge_cancellation_does_not_publish_or_leave_part_files(tmp_path: Path) -> None:
    pypdf = pytest.importorskip("pypdf")
    docs: list[InputDocument] = []
    for part in range(1, 3):
        path = tmp_path / f"Part {part}.pdf"
        writer = pypdf.PdfWriter()
        writer.add_blank_page(width=612, height=792)
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

    output = tmp_path / "cancelled.pdf"
    cancel_requested = False

    def request_cancel(index: int, _total: int, _path: Path) -> None:
        nonlocal cancel_requested
        if index == 1:
            cancel_requested = True

    with pytest.raises(MergeCancelled, match="cancelled safely"):
        PdfMergeEngine().merge(
            docs,
            output,
            PdfSettings(),
            progress=request_cancel,
            cancelled=lambda: cancel_requested,
        )

    assert not output.exists()
    assert not list(tmp_path.glob("*.part"))
