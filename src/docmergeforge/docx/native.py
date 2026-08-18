from __future__ import annotations

import subprocess
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from docmergeforge.core.exceptions import ValidationError
from docmergeforge.utilities.hashing import sha256_file
from docmergeforge.validation.ooxml import validate_docx_package


@dataclass(slots=True, frozen=True)
class NativeCommandResult:
    command: tuple[str, ...]
    stdout: str
    stderr: str


def run_native_command(
    command: Sequence[str],
    *,
    timeout_seconds: int = 300,
    cwd: Path | None = None,
) -> NativeCommandResult:
    """Run a native office command without a shell and fail closed on timeout/error."""
    if not command:
        raise ValidationError("Native fidelity command cannot be empty.")
    if timeout_seconds < 1:
        raise ValidationError("Native fidelity command timeout must be at least one second.")

    normalized = tuple(str(item) for item in command)
    try:
        completed = subprocess.run(
            normalized,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            cwd=cwd,
        )
    except subprocess.TimeoutExpired as exc:
        raise ValidationError(
            f"Native DOCX fidelity command timed out after {timeout_seconds} seconds."
        ) from exc
    except OSError as exc:
        raise ValidationError(f"Native DOCX fidelity command could not start: {exc}") from exc

    stdout = completed.stdout or ""
    stderr = completed.stderr or ""
    if completed.returncode != 0:
        detail = (stderr or stdout or "unknown native office error").strip()
        if len(detail) > 1000:
            detail = f"{detail[:1000]}…"
        raise ValidationError(
            f"Native DOCX fidelity command failed with exit code {completed.returncode}: {detail}"
        )
    return NativeCommandResult(command=normalized, stdout=stdout, stderr=stderr)


def validate_native_docx_output(output: Path) -> None:
    """Require a non-empty, structurally valid DOCX package from an external office tool."""
    if not output.exists() or not output.is_file() or output.stat().st_size == 0:
        raise ValidationError(f"Native DOCX fidelity tool did not create output: {output}")
    diagnostics = validate_docx_package(output)
    blocking = [item for item in diagnostics if item.level.value in {"ERROR", "FATAL"}]
    if blocking:
        raise ValidationError(
            f"Native DOCX fidelity output validation failed: {blocking[0].message}"
        )


def verify_native_source_unchanged(source: Path, expected_sha256: str) -> None:
    """Verify an external office process did not modify a source document in place."""
    current = sha256_file(source)
    if current != expected_sha256:
        raise ValidationError(f"Source integrity violation during native DOCX processing: {source}")


def verify_native_sources_unchanged(source_hashes: Mapping[Path, str]) -> None:
    """Verify every tracked source still matches the hash captured before native work."""
    for source, expected_hash in source_hashes.items():
        verify_native_source_unchanged(source, expected_hash)


def promote_validated_native_docx_output(
    temporary_output: Path,
    destination: Path,
    source_hashes: Mapping[Path, str],
) -> None:
    """Promote a native-office DOCX and fail closed without leaving a false-success file.

    Callers must already have refused an existing destination. The temporary output and
    all tracked sources are checked before promotion. They are checked again immediately
    afterward to catch a last-moment source change or destination corruption. If that
    final verification fails, the destination created by this operation is removed.
    """
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite existing DOCX output: {destination}")

    validate_native_docx_output(temporary_output)
    verify_native_sources_unchanged(source_hashes)
    temporary_output.replace(destination)

    try:
        validate_native_docx_output(destination)
        verify_native_sources_unchanged(source_hashes)
    except Exception:
        try:
            destination.unlink(missing_ok=True)
        except OSError as cleanup_error:
            raise ValidationError(
                "Native DOCX final verification failed and the newly promoted output "
                "could not be removed safely."
            ) from cleanup_error
        raise
