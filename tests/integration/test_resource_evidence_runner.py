from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration


def _script_path() -> Path:
    return Path(__file__).resolve().parents[2] / "scripts" / "run_with_resource_evidence.py"


def test_resource_evidence_runner_records_child_metrics(tmp_path: Path) -> None:
    evidence = tmp_path / "evidence.json"

    completed = subprocess.run(
        [
            sys.executable,
            str(_script_path()),
            "--output",
            str(evidence),
            "--watch-path",
            str(tmp_path),
            "--",
            sys.executable,
            "-c",
            "print('measured-child')",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
    assert "measured-child" in completed.stdout
    payload = json.loads(evidence.read_text(encoding="utf-8"))
    assert payload["schema_version"] == 1
    assert payload["exit_code"] == 0
    assert payload["command_executable"] == Path(sys.executable).name
    assert payload["argument_count"] == 2
    assert payload["elapsed_seconds"] >= 0
    assert payload["user_cpu_seconds"] >= 0
    assert payload["system_cpu_seconds"] >= 0
    assert payload["max_rss_bytes"] > 0
    assert payload["disk_free_before_bytes"] > 0
    assert payload["disk_free_after_bytes"] > 0
    assert "command" not in payload
    assert "environment" not in payload


def test_resource_evidence_runner_propagates_child_failure(tmp_path: Path) -> None:
    evidence = tmp_path / "failure.json"

    completed = subprocess.run(
        [
            sys.executable,
            str(_script_path()),
            "--output",
            str(evidence),
            "--watch-path",
            str(tmp_path),
            "--",
            sys.executable,
            "-c",
            "raise SystemExit(7)",
        ],
        check=False,
    )

    assert completed.returncode == 7
    payload = json.loads(evidence.read_text(encoding="utf-8"))
    assert payload["exit_code"] == 7
