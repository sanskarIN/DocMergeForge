from __future__ import annotations

import shutil
import sys
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

_WORD_ROUNDTRIP_SCRIPT = r"""
param(
    [Parameter(Mandatory=$true)][string]$Source,
    [Parameter(Mandatory=$true)][string]$Destination
)
$ErrorActionPreference = 'Stop'
$word = $null
$document = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $word.AutomationSecurity = 3
    $document = $word.Documents.Open($Source, $false, $true, $false)
    $document.SaveAs2($Destination, 16)
    $document.Close($false)
    [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($document)
    $document = $null
}
finally {
    if ($null -ne $document) {
        try { $document.Close($false) } catch { }
        [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($document)
    }
    if ($null -ne $word) {
        try { $word.Quit() } catch { }
        [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($word)
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
""".strip()


def find_word_powershell_host() -> str | None:
    if sys.platform != "win32":
        return None
    return shutil.which("powershell.exe") or shutil.which("powershell")


def word_roundtrip_copy(
    source: Path,
    destination: Path,
    *,
    powershell: str | None = None,
    timeout_seconds: int = 300,
) -> NativeCommandResult:
    """Re-save one DOCX through installed Microsoft Word into a validated copy.

    The adapter is explicit, Windows-only, and source-preserving. Successful execution
    demonstrates that Word automation worked for the selected document; it is not a
    blanket production-fidelity claim for arbitrary manuscripts.
    """
    if source.suffix.casefold() != ".docx" or destination.suffix.casefold() != ".docx":
        raise ValidationError("Microsoft Word fidelity round-trip accepts DOCX paths only.")
    if not source.exists() or not source.is_file():
        raise FileNotFoundError(source)
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite existing DOCX output: {destination}")
    if source.resolve() == destination.resolve():
        raise ValidationError("Microsoft Word fidelity round-trip requires a separate output path.")

    host = powershell or find_word_powershell_host()
    if host is None:
        raise UnsupportedDocumentError(
            "Microsoft Word fidelity automation requires Windows PowerShell and installed Word."
        )

    destination.parent.mkdir(parents=True, exist_ok=True)
    before = sha256_file(source)
    with tempfile.TemporaryDirectory(
        prefix="docmergeforge-word-fidelity-", dir=destination.parent
    ) as temp_name:
        temp_dir = Path(temp_name)
        script = temp_dir / "word_roundtrip.ps1"
        temporary_output = temp_dir / destination.name
        script.write_text(_WORD_ROUNDTRIP_SCRIPT, encoding="utf-8")
        result = run_native_command(
            [
                host,
                "-NoLogo",
                "-NoProfile",
                "-NonInteractive",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(script),
                "-Source",
                str(source.resolve()),
                "-Destination",
                str(temporary_output.resolve()),
            ],
            timeout_seconds=timeout_seconds,
        )
        validate_native_docx_output(temporary_output)
        verify_native_source_unchanged(source, before)
        temporary_output.replace(destination)

    validate_native_docx_output(destination)
    verify_native_source_unchanged(source, before)
    return result
