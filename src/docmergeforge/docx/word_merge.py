from __future__ import annotations

import json
import tempfile
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from docmergeforge.core.exceptions import UnsupportedDocumentError, ValidationError
from docmergeforge.docx.native import (
    NativeCommandResult,
    run_native_command,
    validate_native_docx_output,
    verify_native_source_unchanged,
)
from docmergeforge.docx.word import find_word_powershell_host
from docmergeforge.utilities.hashing import sha256_file

_WORD_MERGE_SCRIPT = r"""
param(
    [Parameter(Mandatory=$true)][string]$Manifest,
    [Parameter(Mandatory=$true)][string]$Destination,
    [Parameter(Mandatory=$true)][ValidateSet(0, 1)][int]$StartEachOnNewPage
)
$ErrorActionPreference = 'Stop'
$word = $null
$master = $null
try {
    $sources = @(Get-Content -LiteralPath $Manifest -Raw | ConvertFrom-Json)
    if ($sources.Count -lt 1) {
        throw 'Word merge manifest contains no source documents.'
    }

    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $word.AutomationSecurity = 3

    $first = $word.Documents.Open([string]$sources[0], $false, $true, $false)
    try {
        $first.SaveAs2($Destination, 16)
    }
    finally {
        $first.Close($false)
        [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($first)
    }

    $master = $word.Documents.Open($Destination, $false, $false, $false)
    for ($index = 1; $index -lt $sources.Count; $index++) {
        $range = $master.Content
        try {
            $range.Collapse(0)
            if ($StartEachOnNewPage -eq 1) {
                $range.InsertBreak(7)
                $range.Collapse(0)
            }
            $range.InsertFile([string]$sources[$index])
        }
        finally {
            [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($range)
        }
    }
    $master.Save()
    $master.Close($false)
    [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($master)
    $master = $null
}
finally {
    if ($null -ne $master) {
        try { $master.Close($false) } catch { }
        [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($master)
    }
    if ($null -ne $word) {
        try { $word.Quit() } catch { }
        [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($word)
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
""".strip()


@dataclass(slots=True, frozen=True)
class WordNativeMergeResult:
    source_count: int
    output: Path
    command: NativeCommandResult


def _validate_sources(sources: Sequence[Path], destination: Path) -> tuple[Path, ...]:
    if not sources:
        raise ValidationError("Microsoft Word native merge requires at least one DOCX source.")
    normalized = tuple(Path(source) for source in sources)
    destination_resolved = destination.resolve()
    for source in normalized:
        if source.suffix.casefold() != ".docx":
            raise ValidationError(f"Microsoft Word native merge accepts DOCX files only: {source}")
        if not source.exists() or not source.is_file():
            raise FileNotFoundError(source)
        if source.resolve() == destination_resolved:
            raise ValidationError("Microsoft Word native merge requires a separate output path.")
        validate_native_docx_output(source)
    return normalized


def word_merge_documents(
    sources: Sequence[Path],
    destination: Path,
    *,
    powershell: str | None = None,
    timeout_seconds: int = 900,
    start_each_on_new_page: bool = True,
) -> WordNativeMergeResult:
    """Merge DOCX sources using installed Microsoft Word into a validated copy.

    This is an explicit native-merge prototype/acceptance boundary. It is intentionally
    not wired to the production DOCX engine while Word fidelity remains uncertified.
    """
    if destination.suffix.casefold() != ".docx":
        raise ValidationError("Microsoft Word native merge output must use .docx.")
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite existing DOCX output: {destination}")
    if timeout_seconds < 1:
        raise ValidationError("Microsoft Word native merge timeout must be at least one second.")

    host = powershell or find_word_powershell_host()
    if host is None:
        raise UnsupportedDocumentError(
            "Microsoft Word native merge requires Windows PowerShell and installed Word."
        )

    ordered_sources = _validate_sources(sources, destination)
    source_hashes = {source: sha256_file(source) for source in ordered_sources}
    destination.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(
        prefix="docmergeforge-word-merge-", dir=destination.parent
    ) as temp_name:
        temp_dir = Path(temp_name)
        manifest = temp_dir / "sources.json"
        script = temp_dir / "word_merge.ps1"
        temporary_output = temp_dir / destination.name
        manifest.write_text(
            json.dumps([str(source.resolve()) for source in ordered_sources]),
            encoding="utf-8",
        )
        script.write_text(_WORD_MERGE_SCRIPT, encoding="utf-8")

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
                "-Manifest",
                str(manifest),
                "-Destination",
                str(temporary_output.resolve()),
                "-StartEachOnNewPage",
                "1" if start_each_on_new_page else "0",
            ],
            timeout_seconds=timeout_seconds,
        )

        validate_native_docx_output(temporary_output)
        for source, expected_hash in source_hashes.items():
            verify_native_source_unchanged(source, expected_hash)
        temporary_output.replace(destination)

    validate_native_docx_output(destination)
    for source, expected_hash in source_hashes.items():
        verify_native_source_unchanged(source, expected_hash)
    return WordNativeMergeResult(
        source_count=len(ordered_sources),
        output=destination,
        command=result,
    )
