from pathlib import Path

from docmergeforge.core.models import DocumentKind
from docmergeforge.discovery.scanner import classify


def test_companion_archives_are_not_documents() -> None:
    assert classify(Path("Part 1 Companion Code.zip")) is DocumentKind.COMPANION
    assert classify(Path("Part 1.pdf")) is DocumentKind.PDF
    assert classify(Path("Part 1.docx")) is DocumentKind.DOCX
