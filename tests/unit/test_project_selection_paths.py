import os
from pathlib import Path

import pytest

from docmergeforge.core.models import DocumentKind, InputDocument, PartIdentity
from docmergeforge.project.selection import apply_project_selection


def _document(path: Path, *, sha256: str) -> InputDocument:
    return InputDocument(
        path=path,
        kind=DocumentKind.DOCX,
        part=PartIdentity(number=1, label="Part 1"),
        size=1,
        sha256=sha256,
    )


def test_project_selection_preserves_case_distinct_posix_paths(tmp_path: Path) -> None:
    if os.path.normcase("A") == os.path.normcase("a"):
        pytest.skip("Case-distinct path identity is not available on this platform.")

    upper = tmp_path / "Part-001.docx"
    lower = tmp_path / "part-001.docx"
    discovered = [
        _document(upper, sha256="upper"),
        _document(lower, sha256="lower"),
    ]

    selected = apply_project_selection(discovered, [upper])

    assert [item.path for item in selected] == [upper]
    assert selected[0].sha256 == "upper"


def test_project_selection_still_rejects_same_path_twice(tmp_path: Path) -> None:
    path = tmp_path / "Part-001.docx"
    discovered = [_document(path, sha256="one")]

    with pytest.raises(ValueError, match="appears more than once"):
        apply_project_selection(discovered, [path, path])


def test_project_selection_matches_resolved_path_alias(tmp_path: Path) -> None:
    path = tmp_path / "book" / "Part-001.docx"
    alias = tmp_path / "book" / ".." / "book" / "Part-001.docx"
    discovered = [_document(path, sha256="one")]

    selected = apply_project_selection(discovered, [alias])

    assert [item.path for item in selected] == [path]
