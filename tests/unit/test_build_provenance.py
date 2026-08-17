from pathlib import Path

import pytest

from docmergeforge.packaging.provenance import build_provenance, write_provenance


def test_build_provenance_records_allowlisted_ci_identity_only() -> None:
    environment = {
        "GITHUB_SHA": "abc123",
        "GITHUB_REPOSITORY": "sanskarIN/DocMergeForge",
        "GITHUB_REF": "refs/heads/main",
        "GITHUB_RUN_ID": "12345",
        "GITHUB_RUN_ATTEMPT": "2",
        "GITHUB_WORKFLOW": "Package Desktop",
        "RUNNER_OS": "Linux",
        "RUNNER_ARCH": "X64",
        "TOKEN": "must-not-appear",
        "PASSWORD": "must-not-appear",
    }

    payload = build_provenance(
        build_mode="onedir",
        artifact_label="DocMergeForge-Linux-unsigned",
        environment=environment,
    )

    assert payload["application"]["name"] == "DocMergeForge"
    assert payload["source"]["commit_sha"] == "abc123"
    assert payload["artifact"]["build_mode"] == "onedir"
    assert payload["artifact"]["signed"] is False
    assert payload["artifact"]["notarized"] is False
    assert payload["ci"]["github_run_id"] == "12345"
    serialized = str(payload)
    assert "must-not-appear" not in serialized
    assert "TOKEN" not in serialized
    assert "PASSWORD" not in serialized


def test_build_provenance_rejects_invalid_mode_and_empty_label() -> None:
    with pytest.raises(ValueError, match="build_mode"):
        build_provenance(build_mode="portable", artifact_label="artifact", environment={})
    with pytest.raises(ValueError, match="artifact_label"):
        build_provenance(build_mode="onedir", artifact_label=" ", environment={})


def test_write_provenance_is_json_and_replaces_existing_file(tmp_path: Path) -> None:
    path = tmp_path / "provenance.json"
    path.write_text("stale", encoding="utf-8")

    result = write_provenance(
        path,
        build_mode="onefile",
        artifact_label="DocMergeForge-Windows-onefile-unsigned",
        environment={"GITHUB_SHA": "deadbeef"},
    )

    text = result.read_text(encoding="utf-8")
    assert result == path
    assert '"commit_sha": "deadbeef"' in text
    assert '"build_mode": "onefile"' in text
    assert not path.with_suffix(".json.tmp").exists()
