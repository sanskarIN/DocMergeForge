from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from docmergeforge.core.exceptions import UnsupportedDocumentError, ValidationError
from docmergeforge.utilities.hashing import sha256_file
from docmergeforge.validation.ooxml import validate_docx_package


def find_legacy_doc_converter() -> str | None:
    return shutil.which("libreoffice") or shutil.which("soffice")


def convert_legacy_doc_copy(
    source: Path,
    destination_dir: Path,
    *,
    converter: str | None = None,
    timeout_seconds: int = 180,
) -> Path:
    """Explicitly convert a legacy .doc into a new .docx without touching the source."""
    if source.suffix.casefold() != ".doc":
        raise UnsupportedDocumentError("Legacy conversion accepts only .doc source files.")
    if not source.exists() or not source.is_file():
        raise FileNotFoundError(source)

    executable = converter or find_legacy_doc_converter()
    if executable is None:
        raise UnsupportedDocumentError(
            "LibreOffice/soffice was not detected. Install it or choose a different workflow; "
            "DocMergeForge will not silently convert legacy .doc files."
        )

    destination_dir.mkdir(parents=True, exist_ok=True)
    final_output = destination_dir / f"{source.stem}.docx"
    if final_output.exists():
        raise FileExistsError(
            f"Refusing to overwrite an existing converted document: {final_output}"
        )

    before = sha256_file(source)
    with tempfile.TemporaryDirectory(prefix="docmergeforge-doc-", dir=destination_dir) as temp_name:
        temp_dir = Path(temp_name)
        command = [
            executable,
            "--headless",
            "--convert-to",
            "docx",
            "--outdir",
            str(temp_dir),
            str(source),
        ]
        try:
            completed = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:
            raise ValidationError("Legacy DOC conversion timed out safely.") from exc

        if completed.returncode != 0:
            detail = (completed.stderr or completed.stdout or "unknown converter error").strip()
            raise ValidationError(f"Legacy DOC conversion failed: {detail}")

        converted = temp_dir / f"{source.stem}.docx"
        if not converted.exists() or converted.stat().st_size == 0:
            raise ValidationError("Legacy DOC converter did not produce a valid DOCX file.")
        diagnostics = validate_docx_package(converted)
        blocking = [item for item in diagnostics if item.level.value in {"ERROR", "FATAL"}]
        if blocking:
            raise ValidationError(
                f"Converted DOCX package validation failed: {blocking[0].message}"
            )
        if sha256_file(source) != before:
            raise ValidationError("Source integrity violation during legacy DOC conversion.")

        converted.replace(final_output)

    return final_output
