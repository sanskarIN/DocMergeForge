import json
import shutil
from pathlib import Path

import pytest

from docmergeforge.docx.fidelity_acceptance import (
    FidelityAcceptanceEvidence,
    snapshot_docx_structure,
)
from docmergeforge.utilities.hashing import sha256_file
from scripts import check_docx_fidelity_acceptance as script


def test_fidelity_acceptance_script_writes_reviewable_evidence(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_dir = tmp_path / "evidence"

    def fake_acceptance(
        source: Path,
        output: Path,
        mode: str,
        *,
        timeout_seconds: int = 300,
    ) -> FidelityAcceptanceEvidence:
        assert timeout_seconds == 30
        shutil.copy2(source, output)
        structure = snapshot_docx_structure(source)
        return FidelityAcceptanceEvidence(
            mode=mode,
            source=source,
            output=output,
            source_sha256=sha256_file(source),
            output_sha256=sha256_file(output),
            source_structure=structure,
            output_structure=structure,
            source_risks=(),
            output_risks=(),
            structure_matches=True,
            new_risks=(),
        )

    monkeypatch.setattr(script, "run_fidelity_roundtrip_acceptance", fake_acceptance)
    exit_code = script.main(
        [
            "--mode",
            "libreoffice",
            "--output-dir",
            str(output_dir),
            "--timeout",
            "30",
        ]
    )

    evidence_path = output_dir / "fidelity-libreoffice-evidence.json"
    payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert exit_code == 0
    assert payload["accepted"] is True
    assert payload["mode"] == "libreoffice"
    assert (output_dir / "fidelity-source.docx").exists()
    assert (output_dir / "fidelity-libreoffice-roundtrip.docx").exists()
