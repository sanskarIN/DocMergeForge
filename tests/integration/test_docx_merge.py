from pathlib import Path

import pytest

from docmergeforge.core.exceptions import MergeCancelled, ValidationError
from docmergeforge.core.models import (
    DocumentKind,
    DocxSettings,
    InputDocument,
    PartIdentity,
)
from docmergeforge.docx.engine import DocxMergeEngine
from docmergeforge.utilities.hashing import sha256_file


def _build_docx(docx: object, path: Path, part: int) -> InputDocument:
    document = docx.Document()  # type: ignore[attr-defined]
    document.add_heading(f"Part {part}", level=1)
    document.add_paragraph(f"Unique marker {part}")
    document.save(path)
    digest = sha256_file(path)
    return InputDocument(
        path,
        DocumentKind.DOCX,
        PartIdentity(part, f"Part {part}"),
        path.stat().st_size,
        digest,
    )


@pytest.mark.integration
def test_docx_merge_reopens_and_preserves_sources(tmp_path: Path) -> None:
    docx = pytest.importorskip("docx")
    pytest.importorskip("docxcompose")
    docs = [_build_docx(docx, tmp_path / f"Part {part}.docx", part) for part in range(1, 4)]
    hashes = {item.path: item.sha256 for item in docs}

    output = tmp_path / "master.docx"
    DocxMergeEngine().merge(docs, output, DocxSettings())
    reopened = docx.Document(str(output))
    text = "\n".join(p.text for p in reopened.paragraphs)
    assert "Unique marker 1" in text and "Unique marker 3" in text
    assert all(sha256_file(path) == digest for path, digest in hashes.items())


@pytest.mark.integration
def test_docx_merge_does_not_promote_output_if_source_changes(tmp_path: Path) -> None:
    docx = pytest.importorskip("docx")
    pytest.importorskip("docxcompose")
    first = _build_docx(docx, tmp_path / "Part 1.docx", 1)
    second = _build_docx(docx, tmp_path / "Part 2.docx", 2)
    output = tmp_path / "master.docx"

    def mutate_first(_index: int, _total: int, _path: Path) -> None:
        first.path.write_bytes(first.path.read_bytes() + b"changed")

    with pytest.raises(ValidationError, match="Source integrity violation"):
        DocxMergeEngine().merge(
            [first, second],
            output,
            DocxSettings(),
            progress=mutate_first,
        )

    assert not output.exists()


@pytest.mark.integration
def test_docx_merge_cancellation_does_not_publish_or_leave_part_files(tmp_path: Path) -> None:
    docx = pytest.importorskip("docx")
    pytest.importorskip("docxcompose")
    docs = [_build_docx(docx, tmp_path / f"Part {part}.docx", part) for part in range(1, 3)]
    output = tmp_path / "cancelled.docx"
    cancel_requested = False

    def request_cancel(index: int, _total: int, _path: Path) -> None:
        nonlocal cancel_requested
        if index == 1:
            cancel_requested = True

    with pytest.raises(MergeCancelled, match="cancelled safely"):
        DocxMergeEngine().merge(
            docs,
            output,
            DocxSettings(),
            progress=request_cancel,
            cancelled=lambda: cancel_requested,
        )

    assert not output.exists()
    assert not list(tmp_path.glob("*.part"))
