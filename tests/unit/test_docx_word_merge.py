import json
import shutil
from pathlib import Path

import pytest
from docx import Document

from docmergeforge.core.exceptions import ValidationError
from docmergeforge.docx import word_merge
from docmergeforge.docx.native import NativeCommandResult


def _write_docx(path: Path, text: str) -> None:
    document = Document()
    document.add_heading(text, level=1)
    document.add_paragraph(f"Body for {text}")
    document.save(path)


def test_word_merge_documents_preserves_sources_and_manifest_order(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    first = tmp_path / "Part 1.docx"
    second = tmp_path / "Part 2.docx"
    destination = tmp_path / "accepted" / "merged.docx"
    _write_docx(first, "Part 1")
    _write_docx(second, "Part 2")
    before = {first: first.read_bytes(), second: second.read_bytes()}
    captured_manifest: list[str] = []
    captured_script = ""
    captured_command: list[str] = []

    def fake_run(command: list[str], **kwargs: object) -> NativeCommandResult:
        nonlocal captured_script
        captured_command.extend(command)
        manifest = Path(command[command.index("-Manifest") + 1])
        captured_manifest.extend(json.loads(manifest.read_text(encoding="utf-8")))
        script = Path(command[command.index("-File") + 1])
        captured_script = script.read_text(encoding="utf-8")
        temporary_output = Path(command[command.index("-Destination") + 1])
        shutil.copy2(first, temporary_output)
        return NativeCommandResult(tuple(command), "merged", "")

    monkeypatch.setattr(word_merge, "run_native_command", fake_run)
    result = word_merge.word_merge_documents(
        [first, second],
        destination,
        powershell="fake-powershell",
        timeout_seconds=30,
        start_each_on_new_page=False,
    )

    assert result.source_count == 2
    assert result.output == destination
    assert destination.exists()
    assert first.read_bytes() == before[first]
    assert second.read_bytes() == before[second]
    assert captured_manifest == [str(first.resolve()), str(second.resolve())]
    assert "$range.InsertFile" in captured_script
    assert "$word.AutomationSecurity = 3" in captured_script
    assert captured_command[captured_command.index("-StartEachOnNewPage") + 1] == "0"


def test_word_merge_documents_refuses_empty_sources(tmp_path: Path) -> None:
    with pytest.raises(ValidationError, match="at least one DOCX source"):
        word_merge.word_merge_documents(
            [],
            tmp_path / "merged.docx",
            powershell="fake-powershell",
        )


def test_word_merge_documents_refuses_existing_destination(tmp_path: Path) -> None:
    source = tmp_path / "source.docx"
    destination = tmp_path / "merged.docx"
    _write_docx(source, "Source")
    _write_docx(destination, "Existing")

    with pytest.raises(FileExistsError, match="Refusing to overwrite"):
        word_merge.word_merge_documents(
            [source],
            destination,
            powershell="fake-powershell",
        )


def test_word_merge_documents_refuses_source_as_destination(tmp_path: Path) -> None:
    source = tmp_path / "source.docx"
    _write_docx(source, "Source")

    with pytest.raises(ValidationError, match="separate output path"):
        word_merge.word_merge_documents(
            [source],
            source,
            powershell="fake-powershell",
        )
