from __future__ import annotations

import importlib.metadata
import json
import os
import platform
import sys
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from docmergeforge import __version__
from docmergeforge.utilities.hashing import sha256_file

PROVENANCE_SCHEMA_VERSION = 1

_SAFE_CI_ENV_KEYS = (
    "GITHUB_SHA",
    "GITHUB_REF",
    "GITHUB_REPOSITORY",
    "GITHUB_RUN_ID",
    "GITHUB_RUN_ATTEMPT",
    "GITHUB_WORKFLOW",
    "RUNNER_OS",
    "RUNNER_ARCH",
)


def _installed_distributions() -> list[dict[str, str]]:
    versions: dict[str, str] = {}
    for distribution in importlib.metadata.distributions():
        name = distribution.metadata.get("Name")
        if name:
            versions[name] = distribution.version
    return [
        {"name": name, "version": versions[name]} for name in sorted(versions, key=str.casefold)
    ]


def _artifact_evidence(path: Path | None) -> dict[str, object]:
    if path is None:
        return {}
    if not path.is_file():
        raise FileNotFoundError(f"Build artifact does not exist: {path}")
    return {
        "archive_filename": path.name,
        "archive_size": path.stat().st_size,
        "archive_sha256": sha256_file(path),
    }


def build_provenance(
    *,
    build_mode: str,
    artifact_label: str,
    artifact_path: Path | None = None,
    environment: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Return privacy-safe build provenance for a packaged application artifact."""

    if build_mode not in {"onedir", "onefile"}:
        raise ValueError("build_mode must be 'onedir' or 'onefile'.")
    if not artifact_label.strip():
        raise ValueError("artifact_label must not be empty.")

    env = os.environ if environment is None else environment
    ci = {key.casefold(): env[key] for key in _SAFE_CI_ENV_KEYS if env.get(key)}

    try:
        pyinstaller_version = importlib.metadata.version("pyinstaller")
    except importlib.metadata.PackageNotFoundError:
        pyinstaller_version = None

    return {
        "schema_version": PROVENANCE_SCHEMA_VERSION,
        "application": {
            "name": "DocMergeForge",
            "version": __version__,
        },
        "artifact": {
            "label": artifact_label,
            "build_mode": build_mode,
            "signed": False,
            "notarized": False,
            **_artifact_evidence(artifact_path),
        },
        "source": {
            "commit_sha": env.get("GITHUB_SHA", "unknown"),
            "repository": env.get("GITHUB_REPOSITORY", "unknown"),
            "ref": env.get("GITHUB_REF", "unknown"),
        },
        "build_environment": {
            "os": platform.system(),
            "os_release": platform.release(),
            "architecture": platform.machine(),
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation(),
            "python_executable_name": Path(sys.executable).name,
            "pyinstaller_version": pyinstaller_version,
        },
        "ci": ci,
        "dependencies": _installed_distributions(),
        "generated_at": datetime.now(UTC).isoformat(),
        "privacy_note": (
            "Only allowlisted CI identity fields and package/runtime metadata are recorded; "
            "environment secrets, manuscript paths, and document contents are excluded."
        ),
    }


def write_provenance(
    path: Path,
    *,
    build_mode: str,
    artifact_label: str,
    artifact_path: Path | None = None,
    environment: Mapping[str, str] | None = None,
) -> Path:
    """Atomically write build provenance JSON."""

    payload = build_provenance(
        build_mode=build_mode,
        artifact_label=artifact_label,
        artifact_path=artifact_path,
        environment=environment,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)
    return path
