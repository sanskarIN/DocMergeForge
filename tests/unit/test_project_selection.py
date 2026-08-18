from pathlib import Path

import pytest

from docmergeforge.core.models import (
    DocumentKind,
    InputDocument,
    MergeProject,
    MergeSettings,
    PartIdentity,
)
from docmergeforge.project.selection import (
    apply_project_selection,
    automatic_numbered_documents,
    project_merge_documents,
)


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


def test_automatic_numbered_documents_excludes_unnumbered_and_out_of_range() -> None:
    part_1 = item("Part 1.pdf", DocumentKind.PDF, 1)
    part_2 = item("Part 2.pdf", DocumentKind.PDF, 2)
    old_master = item("Book Master.pdf", DocumentKind.PDF, None)
    part_121 = item("Part 121.pdf", DocumentKind.PDF, 121)
    docx = item("Part 1.docx", DocumentKind.DOCX, 1)

    selected = automatic_numbered_documents(
        [part_1, old_master, part_121, docx, part_2],
        DocumentKind.PDF,
        1,
        120,
    )

    assert selected == [part_1, part_2]


def test_project_automatic_merge_uses_only_configured_numbered_range() -> None:
    project = MergeProject(
        "Book",
        [Path("input")],
        Path("output"),
        settings=MergeSettings(expected_start=1, expected_end=2),
    )
    part_1 = item("Part 1.pdf", DocumentKind.PDF, 1)
    part_2 = item("Part 2.pdf", DocumentKind.PDF, 2)
    old_master = item("Book Master.pdf", DocumentKind.PDF, None)
    extra = item("Part 3.pdf", DocumentKind.PDF, 3)

    assert project_merge_documents(
        project,
        [part_1, old_master, extra, part_2],
        DocumentKind.PDF,
    ) == [part_1, part_2]


def test_project_explicit_selection_can_include_reviewed_unnumbered_material() -> None:
    front_matter = item("Front Matter.pdf", DocumentKind.PDF, None)
    part_1 = item("Part 1.pdf", DocumentKind.PDF, 1)
    project = MergeProject(
        "Book",
        [Path("input")],
        Path("output"),
        selected_files=[front_matter.path, part_1.path],
    )

    discovered = apply_project_selection(
        [front_matter, part_1],
        project.selected_files,
    )

    assert project_merge_documents(project, discovered, DocumentKind.PDF) == [
        front_matter,
        part_1,
    ]


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
