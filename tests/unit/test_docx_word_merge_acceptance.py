import shutil
from pathlib import Path

import pytest
from docx import Document
from docx.enum.section import WD_SECTION

from docmergeforge.docx import word_merge_acceptance
from docmergeforge.docx.fidelity import FidelityCapability
from docmergeforge.docx.word_merge import WordNativeMergeResult
from docmergeforge.docx.native import NativeCommandResult


def _write_source(path: Path, heading: str, body: str) -> None:
    document = Document()
    document.add_heading(heading, level=1)
    document.add_paragraph(body)
    table = document.add_table(rows=1, cols=1)
    table.cell(0, 0).text = f"table-{heading}"
    document.save(path)


def _capability() -> FidelityCapability:
    return FidelityCapability(
        mode="word",
        available=True,
        production_ready=False,
        detail="test Word host",
        automation_ready=True,
        executable="fake-powershell",
    )


def _synthetic_merge(sources: tuple[Path, ...], output: Path) -> None:
    first = Document(str(sources[0]))
    merged = Document()
    merged._body.clear_content()
    for index, source in enumerate(sources):
        current = Document(str(source))
        if index:
            merged.add_section(WD_SECTION.NEW_PAGE)
        for paragraph in current.paragraphs:
            target = merged.add_paragraph(style=paragraph.style.name)
            target.add_run(paragraph.text)
        for table in current.tables:
            target_table = merged.add_table(rows=len(table.rows), cols=len(table.columns))
            for row_index, row in enumerate(table.rows):
                for column_index, cell in enumerate(row.cells):
                    target_table.cell(row_index, column_index).text = cell.text
    merged.save(output)


def test_word_merge_acceptance_accepts_measured_synthetic_merge(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    first = tmp_path / "Part 1.docx"
    second = tmp_path / "Part 2.docx"
    output = tmp_path / "merged.docx"
    _write_source(first, "Part 1", "Alpha")
    _write_source(second, "Part 2", "Beta")

    monkeypatch.setattr(
        word_merge_acceptance,
        "require_fidelity_automation",
        lambda mode: _capability(),
    )

    def fake_merge(
        sources: tuple[Path, ...], destination: Path, **kwargs: object
    ) -> WordNativeMergeResult:
        _synthetic_merge(sources, destination)
        return WordNativeMergeResult(
            source_count=len(sources),
            output=destination,
            command=NativeCommandResult(("fake-powershell",), "", ""),
        )

    monkeypatch.setattr(word_merge_acceptance, "word_merge_documents", fake_merge)
    evidence = word_merge_acceptance.run_word_merge_acceptance(
        [first, second],
        output,
    )

    assert evidence.accepted
    assert evidence.structure_matches
    assert evidence.content_matches
    assert evidence.source_count == 2
    assert evidence.output_sha256
    assert evidence.to_dict()["accepted"] is True


def test_word_merge_acceptance_rejects_missing_source_content(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    first = tmp_path / "Part 1.docx"
    second = tmp_path / "Part 2.docx"
    output = tmp_path / "merged.docx"
    _write_source(first, "Part 1", "Alpha")
    _write_source(second, "Part 2", "Beta")

    monkeypatch.setattr(
        word_merge_acceptance,
        "require_fidelity_automation",
        lambda mode: _capability(),
    )

    def incomplete_merge(
        sources: tuple[Path, ...], destination: Path, **kwargs: object
    ) -> WordNativeMergeResult:
        shutil.copy2(sources[0], destination)
        return WordNativeMergeResult(
            source_count=len(sources),
            output=destination,
            command=NativeCommandResult(("fake-powershell",), "", ""),
        )

    monkeypatch.setattr(word_merge_acceptance, "word_merge_documents", incomplete_merge)
    evidence = word_merge_acceptance.run_word_merge_acceptance(
        [first, second],
        output,
    )

    assert not evidence.accepted
    assert not evidence.structure_matches
    assert not evidence.content_matches


def test_word_merge_acceptance_rejects_empty_source_set(tmp_path: Path) -> None:
    with pytest.raises(Exception, match="at least one DOCX source"):
        word_merge_acceptance.run_word_merge_acceptance([], tmp_path / "merged.docx")
