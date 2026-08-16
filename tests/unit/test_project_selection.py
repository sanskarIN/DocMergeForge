from pathlib import Path

import pytest

from docmergeforge.core.models import DocumentKind, InputDocument, PartIdentity
from docmergeforge.project.selection import apply_project_selection


def item(path: str, kind: DocumentKind, part: int | None) -> InputDocument:
    return InputDocument(
        path=Path(path),
        kind=kind,
        part=PartIdentity(part, f"Part {part}" if part is not None else "Unnumbered"),
        size=1,
        sha256=path,
    )


def test_selection_filters_mergeable_files_and_preserves_manual_order() -> None:
    part_1 = item("Part 1.pdf", DocumentKind.PDF, 1)
    part_2 = item("Part 2.pdf", DocumentKind.PDF, 2)
    part_3 = item("Part 3.pdf", DocumentKind.PDF, 3)
    companion = item("Part 2 Companion.zip", DocumentKind.COMPANION, 2)

    selected = apply_project_selection(
        [part_1, part_2, part_3, companion],
        [part_3.path, part_1.path],
    )

    assert selected[:2] == [part_3, part_1]
    assert part_2 not in selected
    assert selected[-1] is companion


def test_empty_selection_keeps_discovery_results() -> None:
    inputs = [
        item("Part 1.pdf", DocumentKind.PDF, 1),
        item("notes.txt", DocumentKind.OTHER, None),
    ]
    assert apply_project_selection(inputs, []) == inputs


def test_selected_companion_never_becomes_a_mergeable_document() -> None:
    pdf = item("Part 1.pdf", DocumentKind.PDF, 1)
    companion = item("Part 1 Companion.zip", DocumentKind.COMPANION, 1)

    selected = apply_project_selection([pdf, companion], [companion.path, pdf.path])

    assert selected[0] is pdf
    assert selected[1] is companion


def test_missing_selected_file_is_rejected() -> None:
    pdf = item("Part 1.pdf", DocumentKind.PDF, 1)
    with pytest.raises(ValueError, match="not found"):
        apply_project_selection([pdf], [Path("Part 2.pdf")])


def test_duplicate_selected_file_is_rejected() -> None:
    pdf = item("Part 1.pdf", DocumentKind.PDF, 1)
    with pytest.raises(ValueError, match="more than once"):
        apply_project_selection([pdf], [pdf.path, pdf.path])
