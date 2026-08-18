import json
from pathlib import Path

import pytest

from docmergeforge.docx.libreoffice_uno_acceptance import (
    LibreOfficeUnoAcceptanceEvidence,
    LibreOfficeUnoContentSnapshot,
    LibreOfficeUnoStructureSnapshot,
)
from scripts import check_libreoffice_uno_merge_acceptance as script


def _evidence(output: Path, *, accepted: bool) -> LibreOfficeUnoAcceptanceEvidence:
    expected_structure = LibreOfficeUnoStructureSnapshot(
        paragraphs=4,
        tables=2,
        inline_shapes=0,
        headings=0,
    )
    output_structure = (
        expected_structure
        if accepted
        else LibreOfficeUnoStructureSnapshot(
            paragraphs=2,
            tables=1,
            inline_shapes=0,
            headings=0,
        )
    )
    expected_content = LibreOfficeUnoContentSnapshot(
        body_paragraphs_sha256="a" * 64,
        tables_sha256="b" * 64,
    )
    output_content = (
        expected_content
        if accepted
        else LibreOfficeUnoContentSnapshot(
            body_paragraphs_sha256="c" * 64,
            tables_sha256="d" * 64,
        )
    )
    return LibreOfficeUnoAcceptanceEvidence(
        source_count=2,
        source_sha256=("e" * 64, "f" * 64),
        output=output,
        output_sha256="0" * 64,
        expected_structure=expected_structure,
        output_structure=output_structure,
        expected_content=expected_content,
        output_content=output_content,
        source_risks=(),
        output_risks=(),
        new_risks=(),
        structure_matches=accepted,
        content_matches=accepted,
    )


def test_acceptance_command_preserves_input_order_and_writes_json(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first = tmp_path / "Part 1.docx"
    second = tmp_path / "Part 2.docx"
    output = tmp_path / "merged.docx"
    evidence_path = tmp_path / "evidence.json"
    captured: dict[str, object] = {}

    def fake_acceptance(
        sources: list[Path], destination: Path, **kwargs: object
    ) -> LibreOfficeUnoAcceptanceEvidence:
        captured["sources"] = tuple(sources)
        captured["destination"] = destination
        captured["kwargs"] = kwargs
        return _evidence(destination, accepted=True)

    monkeypatch.setattr(script, "run_libreoffice_uno_acceptance", fake_acceptance)
    exit_code = script.main(
        [
            "--input",
            str(first),
            "--input",
            str(second),
            "--output",
            str(output),
            "--evidence",
            str(evidence_path),
            "--timeout",
            "45",
            "--no-start-each-on-new-page",
        ]
    )

    assert exit_code == 0
    assert captured["sources"] == (first, second)
    assert captured["destination"] == output
    assert captured["kwargs"] == {
        "timeout_seconds": 45,
        "start_each_on_new_page": False,
    }
    payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert payload["accepted"] is True
    assert payload["source_count"] == 2


def test_acceptance_command_returns_two_for_measured_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output = tmp_path / "merged.docx"
    evidence_path = tmp_path / "evidence.json"
    monkeypatch.setattr(
        script,
        "run_libreoffice_uno_acceptance",
        lambda sources, destination, **kwargs: _evidence(destination, accepted=False),
    )

    exit_code = script.main(
        [
            "--input",
            str(tmp_path / "Part 1.docx"),
            "--output",
            str(output),
            "--evidence",
            str(evidence_path),
        ]
    )

    assert exit_code == 2
    assert json.loads(evidence_path.read_text(encoding="utf-8"))["accepted"] is False


def test_acceptance_command_refuses_evidence_overwrite(tmp_path: Path) -> None:
    evidence_path = tmp_path / "evidence.json"
    evidence_path.write_text("{}", encoding="utf-8")

    with pytest.raises(SystemExit, match="Refusing to overwrite existing"):
        script.main(
            [
                "--input",
                str(tmp_path / "Part 1.docx"),
                "--output",
                str(tmp_path / "merged.docx"),
                "--evidence",
                str(evidence_path),
            ]
        )


def test_acceptance_command_rejects_nonpositive_timeout() -> None:
    with pytest.raises(SystemExit, match="timeout must be at least one second"):
        script.main(
            [
                "--input",
                "Part 1.docx",
                "--output",
                "merged.docx",
                "--evidence",
                "evidence.json",
                "--timeout",
                "0",
            ]
        )
