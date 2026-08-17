from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.integration
def test_build_provenance_script_binds_archive_and_source_identity(tmp_path: Path) -> None:
    archive = tmp_path / "DocMergeForge-Linux-unsigned.tar.gz"
    output = tmp_path / "DocMergeForge-Linux-unsigned.provenance.json"
    archive.write_bytes(b"downloadable-archive-bytes")

    script = Path(__file__).resolve().parents[2] / "scripts" / "write_build_provenance.py"
    environment = {
        "GITHUB_SHA": "0123456789abcdef",
        "GITHUB_REPOSITORY": "sanskarIN/DocMergeForge",
        "GITHUB_REF": "refs/heads/main",
    }
    completed = subprocess.run(
        [
            sys.executable,
            str(script),
            "--output",
            str(output),
            "--mode",
            "onedir",
            "--artifact-label",
            "DocMergeForge-Linux-unsigned",
            "--artifact",
            str(archive),
        ],
        check=False,
        capture_output=True,
        text=True,
        env=environment,
        timeout=30,
    )

    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.strip() == str(output)
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["source"]["commit_sha"] == "0123456789abcdef"
    assert payload["artifact"]["label"] == "DocMergeForge-Linux-unsigned"
    assert payload["artifact"]["build_mode"] == "onedir"
    assert payload["artifact"]["archive_filename"] == archive.name
    assert payload["artifact"]["archive_size"] == archive.stat().st_size
    assert len(payload["artifact"]["archive_sha256"]) == 64
