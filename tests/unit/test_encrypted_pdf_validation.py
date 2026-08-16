from pathlib import Path

from docmergeforge.core.models import DocumentKind, InputDocument, PartIdentity
from docmergeforge.validation.service import validate_part_set


def encrypted_pdf() -> InputDocument:
    return InputDocument(
        path=Path("Part 1.pdf"),
        kind=DocumentKind.PDF,
        part=PartIdentity(1, "Part 1"),
        size=100,
        sha256="digest",
        page_count=1,
        encrypted=True,
    )


def test_encrypted_pdf_requires_local_password_by_default() -> None:
    result = validate_part_set([encrypted_pdf()], DocumentKind.PDF, 1, 1)
    assert not result.ready
    assert any("password protected" in item.message for item in result.diagnostics)


def test_verified_in_memory_password_allows_encrypted_pdf_validation() -> None:
    result = validate_part_set(
        [encrypted_pdf()],
        DocumentKind.PDF,
        1,
        1,
        allow_encrypted_pdf=True,
    )
    assert result.ready
    assert any("supplied in memory" in item.message for item in result.diagnostics)
