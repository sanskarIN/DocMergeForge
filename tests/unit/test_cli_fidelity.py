from pathlib import Path

import pytest

from docmergeforge.cli import main as cli
from docmergeforge.docx.fidelity import FidelityCapability
from docmergeforge.docx.fidelity_acceptance import (
    DocxStructureSnapshot,
    FidelityAcceptanceEvidence,
)


def test_cli_reports_fidelity_capabilities(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        cli,
        "fidelity_capabilities",
        lambda: [
            FidelityCapability(
                mode="portable",
                available=True,
                production_ready=True,
                detail="portable",
                automation_ready=True,
            )
        ],
    )

    exit_code = cli.main(["fidelity-capabilities"])
    output = capsys.readouterr().out

    assert exit_code == 0
    assert '"mode": "portable"' in output
    assert '"production_ready": true' in output
    assert '"automation_ready": true' in output


def test_cli_fidelity_roundtrip_returns_acceptance_status(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    structure = DocxStructureSnapshot(2, 1, 0, 1, 1)
    evidence = FidelityAcceptanceEvidence(
        mode="libreoffice",
        source=Path("input.docx"),
        output=Path("output.docx"),
        source_sha256="a" * 64,
        output_sha256="b" * 64,
        source_structure=structure,
        output_structure=structure,
        source_risks=(),
        output_risks=(),
        structure_matches=True,
        new_risks=(),
    )
    monkeypatch.setattr(
        cli,
        "run_fidelity_roundtrip_acceptance",
        lambda *args, **kwargs: evidence,
    )

    exit_code = cli.main(
        [
            "fidelity-roundtrip",
            "--input",
            "input.docx",
            "--output",
            "output.docx",
            "--mode",
            "libreoffice",
            "--timeout",
            "30",
        ]
    )
    output = capsys.readouterr().out

    assert exit_code == 0
    assert '"accepted": true' in output
    assert '"mode": "libreoffice"' in output


def test_cli_fidelity_timeout_must_be_positive() -> None:
    parser = cli.build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(
            [
                "fidelity-roundtrip",
                "--input",
                "input.docx",
                "--output",
                "output.docx",
                "--mode",
                "word",
                "--timeout",
                "0",
            ]
        )
