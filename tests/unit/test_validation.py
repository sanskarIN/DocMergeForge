from pathlib import Path

from docmergeforge.core.models import DocumentKind, InputDocument, PartIdentity
from docmergeforge.validation.service import duplicate_hashes, validate_part_set


def item(
    part: int,
    name: str,
    digest: str | None = None,
    *,
    size: int = 10,
    encrypted: bool = False,
) -> InputDocument:
    return InputDocument(
        path=Path(name),
        kind=DocumentKind.PDF,
        part=PartIdentity(part, f"Part {part}"),
        size=size,
        sha256=digest or str(part),
        page_count=1,
        encrypted=encrypted,
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


def test_out_of_range_part_warns_without_satisfying_expected_range() -> None:
    docs = [item(1, "Part 1.pdf"), item(121, "Part 121.pdf")]

    result = validate_part_set(docs, DocumentKind.PDF, 1, 1)

    assert result.ready
    assert result.found_parts == [1]
    warning_messages = [diagnostic.message for diagnostic in result.diagnostics]
    assert "Part 121 is outside the configured expected range." in warning_messages


def test_excluded_encrypted_and_zero_byte_files_do_not_block_numbered_merge() -> None:
    part_1 = item(1, "Part 1.pdf")
    excluded_encrypted = item(121, "Part 121.pdf", encrypted=True)
    excluded_zero_byte = item(122, "Part 122.pdf", size=0)

    result = validate_part_set(
        [part_1, excluded_encrypted, excluded_zero_byte],
        DocumentKind.PDF,
        1,
        1,
        merge_documents=[part_1],
    )

    assert result.ready
    assert not any(
        diagnostic.level.value in {"ERROR", "FATAL"} for diagnostic in result.diagnostics
    )


def test_selected_encrypted_file_still_blocks_without_password() -> None:
    encrypted = item(1, "Part 1.pdf", encrypted=True)

    result = validate_part_set(
        [encrypted],
        DocumentKind.PDF,
        1,
        1,
        merge_documents=[encrypted],
    )

    assert not result.ready
    assert any("password protected" in diagnostic.message for diagnostic in result.diagnostics)


def test_duplicate_file_hashes() -> None:
    docs = [item(1, "Part 1.pdf", "same"), item(2, "Part 2.pdf", "same")]
    assert "same" in duplicate_hashes(docs)
