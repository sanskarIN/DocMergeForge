from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from docmergeforge.core.exceptions import UnsupportedDocumentError, ValidationError
from docmergeforge.docx.native import (
    NativeCommandResult,
    run_native_command,
    validate_native_docx_output,
    verify_native_source_unchanged,
)
from docmergeforge.utilities.hashing import sha256_file


def find_libreoffice() -> str | None:
    return shutil.which("libreoffice") or shutil.which("soffice")


def libreoffice_roundtrip_copy(
    source: Path,
    destination: Path,
    *,
    executable: str | None = None,
    timeout_seconds: int = 300,
) -> NativeCommandResult:
    """Re-save one DOCX through LibreOffice into a separate validated copy.

    This is an explicit fidelity-acceptance building block. It never edits the source,
    never silently replaces the portable merge engine, and never implies that a
    LibreOffice round-trip proves production fidelity for every OOXML construct.
    """
    if source.suffix.casefold() != ".docx" or destination.suffix.casefold() != ".docx":
        raise ValidationError("LibreOffice fidelity round-trip accepts DOCX paths only.")
    if not source.exists() or not source.is_file():
        raise FileNotFoundError(source)
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite existing DOCX output: {destination}")
    if source.resolve() == destination.resolve():
        raise ValidationError("LibreOffice fidelity round-trip requires a separate output path.")

    office = executable or find_libreoffice()
    if office is None:
        raise UnsupportedDocumentError(
            "LibreOffice/soffice was not detected. Install LibreOffice or use portable mode."
        )

    destination.parent.mkdir(parents=True, exist_ok=True)
    before = sha256_file(source)
    with tempfile.TemporaryDirectory(
        prefix="docmergeforge-lo-fidelity-", dir=destination.parent
    ) as temp_name:
        temp_dir = Path(temp_name)
        profile_dir = temp_dir / "profile"
        profile_dir.mkdir()
        result = run_native_command(
            [
                office,
                f"-env:UserInstallation={profile_dir.resolve().as_uri()}",
                "--headless",
                "--nologo",
                "--nodefault",
                "--nofirststartwizard",
                "--norestore",
                "--convert-to",
                "docx",
                "--outdir",
                str(temp_dir),
                str(source),
            ],
            timeout_seconds=timeout_seconds,
        )
        converted = temp_dir / f"{source.stem}.docx"
        validate_native_docx_output(converted)
        verify_native_source_unchanged(source, before)
        converted.replace(destination)

    validate_native_docx_output(destination)
    verify_native_source_unchanged(source, before)
    return result
