from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from docmergeforge.core.exceptions import ValidationError
from docmergeforge.docx.native import run_native_command

_WORD_PROCESS_CLEANUP_SCRIPT = r"""
param(
    [Parameter(Mandatory=$true)][string]$IdentityFile
)
$ErrorActionPreference = 'Stop'

$identity = Get-Content -LiteralPath $IdentityFile -Raw | ConvertFrom-Json
$wordProcessId = [int]$identity.process_id
$expectedName = [string]$identity.process_name
$expectedStartTicks = [long]$identity.start_time_utc_ticks
if ($wordProcessId -lt 1) {
    throw 'Word process identity contains an invalid process ID.'
}
if ($expectedName -ne 'WINWORD') {
    throw 'Word process identity contains an unexpected process name.'
}
if ($expectedStartTicks -lt 1) {
    throw 'Word process identity contains an invalid start-time fingerprint.'
}

$process = Get-Process -Id $wordProcessId -ErrorAction SilentlyContinue
if ($null -eq $process) {
    [ordered]@{
        identity_match = $true
        process_found = $false
        terminated = $false
    } | ConvertTo-Json -Compress
    exit 0
}

$actualName = [string]$process.ProcessName
$actualStartTicks = [long]$process.StartTime.ToUniversalTime().Ticks
if ($actualName -ne 'WINWORD') {
    throw "Refusing to terminate PID $wordProcessId because it is '$actualName', not WINWORD."
}
if ($actualStartTicks -ne $expectedStartTicks) {
    throw "Refusing to terminate PID $wordProcessId because its start-time fingerprint changed."
}

Stop-Process -Id $wordProcessId -Force -ErrorAction Stop
for ($attempt = 0; $attempt -lt 40; $attempt++) {
    Start-Sleep -Milliseconds 250
    if ($null -eq (Get-Process -Id $wordProcessId -ErrorAction SilentlyContinue)) {
        [ordered]@{
            identity_match = $true
            process_found = $true
            terminated = $true
        } | ConvertTo-Json -Compress
        exit 0
    }
}
throw "WINWORD PID $wordProcessId did not terminate after exact-identity cleanup."
""".strip()


@dataclass(slots=True, frozen=True)
class WordProcessCleanupResult:
    identity_present: bool
    process_found: bool
    terminated: bool


def cleanup_word_process_identity(
    identity_file: Path,
    *,
    powershell: str,
    timeout_seconds: int = 15,
) -> WordProcessCleanupResult:
    """Terminate only the exact WINWORD process recorded by controlled automation.

    The identity includes both PID and process start time to prevent PID reuse from turning
    timeout cleanup into a broad or unsafe process kill. If the process is already gone,
    cleanup succeeds without terminating anything.
    """
    if timeout_seconds < 1:
        raise ValidationError("Word process cleanup timeout must be at least one second.")
    if not identity_file.exists():
        return WordProcessCleanupResult(
            identity_present=False,
            process_found=False,
            terminated=False,
        )
    if not identity_file.is_file():
        raise ValidationError(f"Word process identity is not a file: {identity_file}")

    try:
        identity = json.loads(identity_file.read_text(encoding="utf-8"))
        process_id = int(identity["process_id"])
        process_name = str(identity["process_name"])
        start_ticks = int(identity["start_time_utc_ticks"])
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        raise ValidationError(f"Invalid Word process identity file: {identity_file}") from exc
    if process_id < 1 or process_name != "WINWORD" or start_ticks < 1:
        raise ValidationError(f"Unsafe Word process identity file: {identity_file}")

    script = identity_file.with_name("cleanup_word_process.ps1")
    script.write_text(_WORD_PROCESS_CLEANUP_SCRIPT, encoding="utf-8")
    result = run_native_command(
        [
            powershell,
            "-NoLogo",
            "-NoProfile",
            "-NonInteractive",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(script),
            "-IdentityFile",
            str(identity_file),
        ],
        timeout_seconds=timeout_seconds,
    )

    try:
        payload = json.loads(result.stdout.strip())
        identity_match = bool(payload["identity_match"])
        process_found = bool(payload["process_found"])
        terminated = bool(payload["terminated"])
    except (ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        raise ValidationError("Word process cleanup returned invalid evidence.") from exc
    if not identity_match:
        raise ValidationError("Word process cleanup could not verify the recorded identity.")
    if process_found and not terminated:
        raise ValidationError("Word process cleanup found Word but did not terminate it.")

    return WordProcessCleanupResult(
        identity_present=True,
        process_found=process_found,
        terminated=terminated,
    )
