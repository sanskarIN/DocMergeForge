from pathlib import Path

import pytest

from docmergeforge.core.exceptions import UnsupportedDocumentError
from docmergeforge.discovery.scanner import scan
from docmergeforge.docx.legacy import convert_legacy_doc_copy
from docmergeforge.utilities.hashing import sha256_file


def test_scanner_flags_legacy_doc_without_classifying_it_as_docx(tmp_path: Path) -> None:
    source = tmp_path / "Part 4.doc"
    source.write_bytes(b"legacy-doc-placeholder")

    result = scan([source])

    assert len(result) == 1
    assert result[0].kind.value == "other"
    assert any("explicitly" in warning for warning in result[0].warnings)


def test_legacy_conversion_requires_doc_source(tmp_path: Path) -> None:
    source = tmp_path / "Part 1.txt"
    source.write_text("text", encoding="utf-8")
    with pytest.raises(UnsupportedDocumentError, match="only .doc"):
        convert_legacy_doc_copy(source, tmp_path / "out")


def test_legacy_conversion_never_changes_source_when_converter_missing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "Part 1.doc"
    source.write_bytes(b"legacy-doc-placeholder")
    before = sha256_file(source)
    monkeypatch.setattr("docmergeforge.docx.legacy.find_legacy_doc_converter", lambda: None)

    with pytest.raises(UnsupportedDocumentError, match="not detected"):
        convert_legacy_doc_copy(source, tmp_path / "out")

    assert source.exists()
    assert sha256_file(source) == before
