from pathlib import Path

from docmergeforge.core.models import DocumentKind, InputDocument, PartIdentity
from docmergeforge.validation.service import duplicate_hashes, validate_part_set


def item(part: int, name: str, digest: str | None = None) -> InputDocument:
    return InputDocument(
        path=Path(name),
        kind=DocumentKind.PDF,
        part=PartIdentity(part, f"Part {part}"),
        size=10,
        sha256=digest or str(part),
        page_count=1,
    )


def test_missing_part_37() -> None:
    docs = [item(i, f"Part {i}.pdf") for i in range(1, 121) if i != 37]
    result = validate_part_set(docs, DocumentKind.PDF, 1, 120)
    assert result.missing_parts == [37]
    assert not result.ready


def test_duplicate_part_48() -> None:
    docs = [item(i, f"Part {i}.pdf") for i in range(1, 121)]
    docs.append(item(48, "Part 048 copy.pdf"))
    result = validate_part_set(docs, DocumentKind.PDF, 1, 120)
    assert 48 in result.duplicate_parts
    assert not result.ready


def test_duplicate_file_hashes() -> None:
    docs = [item(1, "Part 1.pdf", "same"), item(2, "Part 2.pdf", "same")]
    assert "same" in duplicate_hashes(docs)
