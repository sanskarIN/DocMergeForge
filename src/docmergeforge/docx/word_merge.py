from __future__ import annotations

import json
import tempfile
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from docmergeforge.core.exceptions import UnsupportedDocumentError, ValidationError
from docmergeforge.docx.native import (
    NativeCommandResult,
    promote_validated_native_docx_output,
    run_native_command,
    validate_native_docx_output,
)
from docmergeforge.docx.word import find_word_powershell_host
from docmergeforge.docx.word_process import cleanup_word_process_identity
from docmergeforge.utilities.hashing import sha256_file

_WORD_MERGE_SCRIPT = r"""
param(
    [Parameter(Mandatory=$true)][string]$Manifest,
    [Parameter(Mandatory=$true)][string]$Destination,
    [Parameter(Mandatory=$true)][string]$ProcessIdentityFile,
    [Parameter(Mandatory=$true)][ValidateSet(0, 1)][int]$StartEachOnNewPage
)
$ErrorActionPreference = 'Stop'

Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;

public static class DocMergeForgeWordNativeMethods
{
    [DllImport("user32.dll")]
    public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint processId);
}
'@

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

    [uint32]$wordProcessId = 0
    $wordHwnd = [IntPtr]$word.Hwnd
    [void][DocMergeForgeWordNativeMethods]::GetWindowThreadProcessId(
        $wordHwnd,
        [ref]$wordProcessId
    )
    if ($wordProcessId -lt 1) {
        throw 'Could not determine the Microsoft Word process ID.'
    }
    $wordProcess = Get-Process -Id $wordProcessId -ErrorAction Stop
    if ($wordProcess.ProcessName -ne 'WINWORD') {
        throw "Unexpected Microsoft Word process name: $($wordProcess.ProcessName)"
    }
    [ordered]@{
        process_id = [int]$wordProcessId
        process_name = [string]$wordProcess.ProcessName
        start_time_utc_ticks = [long]$wordProcess.StartTime.ToUniversalTime().Ticks
    } | ConvertTo-Json -Compress | Set-Content `
        -LiteralPath $ProcessIdentityFile `
        -Encoding UTF8

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
                # wdSectionBreakNextPage = 2
                $range.InsertBreak(2)
            }
            else {
                # wdSectionBreakContinuous = 3
                $range.InsertBreak(3)
            }
            $range.Collapse(0)
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
    resolved_sources: set[Path] = set()
    for source in normalized:
        if source.suffix.casefold() != ".docx":
            raise ValidationError(f"Microsoft Word native merge accepts DOCX files only: {source}")
        if not source.exists() or not source.is_file():
            raise FileNotFoundError(source)
        resolved_source = source.resolve()
        if resolved_source == destination_resolved:
            raise ValidationError("Microsoft Word native merge requires a separate output path.")
        if resolved_source in resolved_sources:
            raise ValidationError(f"Duplicate Microsoft Word merge source detected: {source}")
        resolved_sources.add(resolved_source)
        validate_native_docx_output(source)
    return normalized


def _cleanup_after_command(process_identity_file: Path, *, powershell: str) -> bool:
    cleanup = cleanup_word_process_identity(
        process_identity_file,
        powershell=powershell,
    )
    return cleanup.identity_present and cleanup.terminated


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
    if timeout_seconds < 1:
        raise ValidationError("Microsoft Word native merge timeout must be at least one second.")

    ordered_sources = _validate_sources(sources, destination)
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite existing DOCX output: {destination}")

    host = powershell or find_word_powershell_host()
    if host is None:
        raise UnsupportedDocumentError(
            "Microsoft Word native merge requires Windows PowerShell and installed Word."
        )

    source_hashes = {source: sha256_file(source) for source in ordered_sources}
    destination.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(
        prefix="docmergeforge-word-merge-", dir=destination.parent
    ) as temp_name:
        temp_dir = Path(temp_name)
        manifest = temp_dir / "sources.json"
        process_identity_file = temp_dir / "word-process-identity.json"
        script = temp_dir / "word_merge.ps1"
        temporary_output = temp_dir / destination.name
        manifest.write_text(
            json.dumps([str(source.resolve()) for source in ordered_sources]),
            encoding="utf-8",
        )
        script.write_text(_WORD_MERGE_SCRIPT, encoding="utf-8")

        try:
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
                    "-ProcessIdentityFile",
                    str(process_identity_file.resolve()),
                    "-StartEachOnNewPage",
                    "1" if start_each_on_new_page else "0",
                ],
                timeout_seconds=timeout_seconds,
            )
        except Exception:
            try:
                _cleanup_after_command(process_identity_file, powershell=host)
            except Exception as cleanup_error:
                raise ValidationError(
                    "Microsoft Word native merge failed and exact-process cleanup also failed."
                ) from cleanup_error
            raise

        if not process_identity_file.exists():
            raise ValidationError(
                "Microsoft Word native merge did not record its Word process identity."
            )
        forced_cleanup = _cleanup_after_command(
            process_identity_file,
            powershell=host,
        )
        if forced_cleanup:
            raise ValidationError(
                "Microsoft Word remained running after a successful native merge command; "
                "the exact recorded Word process was forcibly terminated."
            )

        promote_validated_native_docx_output(
            temporary_output,
            destination,
            source_hashes,
        )

    return WordNativeMergeResult(
        source_count=len(ordered_sources),
        output=destination,
        command=result,
    )
