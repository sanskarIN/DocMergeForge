from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from docmergeforge.core.exceptions import ValidationError
from docmergeforge.docx.fidelity import require_fidelity_automation
from docmergeforge.docx.native import run_native_command
from docmergeforge.docx.word_process import cleanup_word_process_identity

_WORD_TIMEOUT_SCRIPT = r"""
param(
    [Parameter(Mandatory=$true)][string]$ProcessIdentityFile,
    [Parameter(Mandatory=$true)][int]$HoldSeconds
)
$ErrorActionPreference = 'Stop'

Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;

public static class DocMergeForgeWordTimeoutNativeMethods
{
    [DllImport("user32.dll")]
    public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint processId);
}
'@

$word = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $word.AutomationSecurity = 3

    [uint32]$wordProcessId = 0
    $wordHwnd = [IntPtr]$word.Hwnd
    [void][DocMergeForgeWordTimeoutNativeMethods]::GetWindowThreadProcessId(
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

    Start-Sleep -Seconds $HoldSeconds
}
finally {
    if ($null -ne $word) {
        try { $word.Quit() } catch { }
        [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($word)
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
""".strip()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Force a controlled Microsoft Word automation timeout, then verify the exact "
            "recorded Word process can be cleaned without broad WINWORD termination."
        )
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("word-timeout-evidence"),
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=20,
        help="Seconds before the native PowerShell command must time out.",
    )
    parser.add_argument(
        "--hold-seconds",
        type=int,
        default=120,
        help="How long the child automation would hold Word if no timeout occurred.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.timeout < 1:
        raise SystemExit("--timeout must be at least one second")
    if args.hold_seconds <= args.timeout:
        raise SystemExit("--hold-seconds must be greater than --timeout")

    capability = require_fidelity_automation("word")
    if capability.executable is None:
        raise ValidationError("Microsoft Word timeout acceptance has no PowerShell host.")

    output_dir: Path = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    identity_path = output_dir / "word-timeout-process-identity.json"
    evidence_path = output_dir / "word-timeout-cleanup-evidence.json"
    for path in (identity_path, evidence_path):
        if path.exists():
            raise SystemExit(
                f"Refusing to overwrite existing Word timeout acceptance artifact: {path}"
            )

    timeout_message = ""
    with tempfile.TemporaryDirectory(
        prefix="docmergeforge-word-timeout-", dir=output_dir
    ) as temp_name:
        script = Path(temp_name) / "hold_word_for_timeout.ps1"
        script.write_text(_WORD_TIMEOUT_SCRIPT, encoding="utf-8")
        try:
            run_native_command(
                [
                    capability.executable,
                    "-NoLogo",
                    "-NoProfile",
                    "-NonInteractive",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(script),
                    "-ProcessIdentityFile",
                    str(identity_path.resolve()),
                    "-HoldSeconds",
                    str(args.hold_seconds),
                ],
                timeout_seconds=args.timeout,
            )
        except ValidationError as exc:
            timeout_message = str(exc)
            if "timed out after" not in timeout_message:
                raise
        else:
            raise ValidationError(
                "Controlled Word timeout acceptance did not observe the required timeout."
            )

    if not identity_path.exists():
        raise ValidationError(
            "Controlled Word timeout occurred before Word process identity was recorded."
        )

    cleanup = cleanup_word_process_identity(
        identity_path,
        powershell=capability.executable,
    )
    if not cleanup.identity_present:
        raise ValidationError("Controlled Word timeout cleanup lost its process identity.")

    evidence = {
        "timeout_seconds": args.timeout,
        "hold_seconds": args.hold_seconds,
        "timeout_observed": True,
        "timeout_message": timeout_message,
        "identity_recorded": True,
        "process_found_during_cleanup": cleanup.process_found,
        "forced_termination": cleanup.terminated,
        "accepted": True,
    }
    evidence_path.write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(evidence_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
