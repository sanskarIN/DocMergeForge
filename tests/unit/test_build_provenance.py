from pathlib import Path

import pytest

from docmergeforge.packaging.provenance import build_provenance, write_provenance
from docmergeforge.utilities.hashing import sha256_file


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


def test_build_provenance_binds_exact_archive(tmp_path: Path) -> None:
    archive = tmp_path / "DocMergeForge-Linux-unsigned.tar.gz"
    archive.write_bytes(b"packaged-archive-bytes")

    payload = build_provenance(
        build_mode="onedir",
        artifact_label="DocMergeForge-Linux-unsigned",
        artifact_path=archive,
        environment={"GITHUB_SHA": "abc123"},
    )

    assert payload["artifact"]["archive_filename"] == archive.name
    assert payload["artifact"]["archive_size"] == archive.stat().st_size
    assert payload["artifact"]["archive_sha256"] == sha256_file(archive)


def test_build_provenance_rejects_invalid_mode_empty_label_and_missing_artifact(
    tmp_path: Path,
) -> None:
    with pytest.raises(ValueError, match="build_mode"):
        build_provenance(build_mode="portable", artifact_label="artifact", environment={})
    with pytest.raises(ValueError, match="artifact_label"):
        build_provenance(build_mode="onedir", artifact_label=" ", environment={})
    with pytest.raises(FileNotFoundError, match="Build artifact does not exist"):
        build_provenance(
            build_mode="onedir",
            artifact_label="artifact",
            artifact_path=tmp_path / "missing.zip",
            environment={},
        )


def test_write_provenance_is_json_and_replaces_existing_file(tmp_path: Path) -> None:
    path = tmp_path / "provenance.json"
    archive = tmp_path / "DocMergeForge-Windows-onefile-unsigned.zip"
    path.write_text("stale", encoding="utf-8")
    archive.write_bytes(b"archive")

    result = write_provenance(
        path,
        build_mode="onefile",
        artifact_label="DocMergeForge-Windows-onefile-unsigned",
        artifact_path=archive,
        environment={"GITHUB_SHA": "deadbeef"},
    )

    text = result.read_text(encoding="utf-8")
    assert result == path
    assert '"commit_sha": "deadbeef"' in text
    assert '"build_mode": "onefile"' in text
    assert f'"archive_sha256": "{sha256_file(archive)}"' in text
    assert not path.with_suffix(".json.tmp").exists()
