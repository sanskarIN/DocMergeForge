import json
from pathlib import Path

import pytest

from docmergeforge.docx.word_merge_acceptance import (
    WordMergeAcceptanceEvidence,
    WordMergeContentSnapshot,
    WordMergeStructureSnapshot,
)
from scripts import check_word_native_merge_acceptance as script


def _accepted_evidence(output: Path) -> WordMergeAcceptanceEvidence:
    structure = WordMergeStructureSnapshot(
        paragraphs=4,
        tables=2,
        inline_shapes=0,
        headings=2,
        sections=2,
        header_paragraphs=0,
        footer_paragraphs=0,
        header_tables=0,
        footer_tables=0,
    )
    content = WordMergeContentSnapshot(
        body_paragraphs_sha256="a" * 64,
        tables_sha256="b" * 64,
        headers_sha256="c" * 64,
        footers_sha256="d" * 64,
    )
    return WordMergeAcceptanceEvidence(
        source_count=2,
        source_sha256=("e" * 64, "f" * 64),
        output=output,
        output_sha256="0" * 64,
        expected_structure=structure,
        output_structure=structure,
        expected_content=content,
        output_content=content,
        source_risks=(),
        output_risks=(),
        new_risks=(),
        structure_matches=True,
        content_matches=True,
    )


def test_word_native_merge_acceptance_script_writes_json(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    evidence_path = tmp_path / "evidence.json"
    output = tmp_path / "merged.docx"
    calls: list[tuple[list[Path], Path, int, bool]] = []

    def fake_acceptance(
        sources: list[Path],
        destination: Path,
        *,
        timeout_seconds: int,
        start_each_on_new_page: bool,
    ) -> WordMergeAcceptanceEvidence:
        calls.append(
            (sources, destination, timeout_seconds, start_each_on_new_page)
        )
        return _accepted_evidence(destination)

    monkeypatch.setattr(script, "run_word_merge_acceptance", fake_acceptance)
    exit_code = script.main(
        [
            "--input",
            str(tmp_path / "Part 1.docx"),
            "--input",
            str(tmp_path / "Part 2.docx"),
            "--output",
            str(output),
            "--evidence",
            str(evidence_path),
            "--timeout",
            "45",
            "--no-start-each-on-new-page",
        ]
    )

    payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert exit_code == 0
    assert payload["accepted"] is True
    assert payload["source_count"] == 2
    assert calls == [
        (
            [tmp_path / "Part 1.docx", tmp_path / "Part 2.docx"],
            output,
            45,
            False,
        )
    ]


def test_word_native_merge_acceptance_script_refuses_evidence_overwrite(
    tmp_path: Path,
) -> None:
    evidence_path = tmp_path / "evidence.json"
    evidence_path.write_text("existing", encoding="utf-8")

    with pytest.raises(SystemExit, match="Refusing to overwrite existing evidence"):
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
