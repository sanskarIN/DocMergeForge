# Microsoft Word Timeout Cleanup Acceptance

DocMergeForge includes a dedicated controlled acceptance harness for the failure mode where a Microsoft Word COM automation host exceeds its allowed execution time.

This harness is intentionally separate from the normal DOCX merge path. It exists to verify process-cleanup behavior on a dedicated Windows acceptance machine and does **not** make Word production-ready.

## Purpose

A native office timeout is different from an ordinary document-fidelity mismatch. If the PowerShell automation host is terminated while Word is still running, DocMergeForge must not:

- leave an orphaned Word process without detection;
- kill every `WINWORD` process on the machine;
- terminate a process that merely reused the same PID;
- treat cleanup failure as a successful merge; or
- hide unsafe cleanup state behind the original timeout error.

The timeout acceptance harness exercises this boundary using the same exact-process cleanup implementation used by Word native merge failures.

## Implementation

```text
scripts/check_word_timeout_cleanup_acceptance.py
src/docmergeforge/docx/word_process.py
```

Regression coverage:

```text
tests/integration/test_word_timeout_cleanup_acceptance_script.py
tests/unit/test_docx_word_process.py
tests/unit/test_docx_word_merge_cleanup_failure.py
```

## Controlled behavior

The harness:

1. requires Word automation capability and a Windows PowerShell host;
2. starts a dedicated invisible `Word.Application` COM session;
3. disables alerts and automation macros;
4. resolves the Word process from `Word.Application.Hwnd` through `GetWindowThreadProcessId`;
5. records PID, process name, and process start-time fingerprint;
6. intentionally holds the automation longer than the configured native-command timeout;
7. requires DocMergeForge's native command boundary to report a timeout;
8. rejects any other automation error as a timeout-acceptance result;
9. requires the Word process identity to have been written before timeout;
10. invokes exact-identity cleanup;
11. records whether the process was already gone, exited during the cleanup grace period, or required forced termination; and
12. writes privacy-limited JSON evidence.

If the command unexpectedly completes instead of timing out, the acceptance fails.

## Exact-process safety

Cleanup authority is bound to all three identity properties:

```text
process_id
process_name = WINWORD
start_time_utc_ticks
```

PID alone is never enough. If the PID was reused, the process name changed, the process start time changed, or identity cannot be verified, cleanup fails closed rather than terminating the process.

The broad pre/post process-state checks in the controlled workflow remain detection-only and do not kill unknown Word sessions.

## Run manually

On the dedicated Windows acceptance host:

```powershell
python scripts/check_word_timeout_cleanup_acceptance.py `
  --output-dir ".\word-timeout-evidence" `
  --timeout 20 `
  --hold-seconds 140
```

`--hold-seconds` must be greater than `--timeout`.

The default values are:

```text
timeout = 20 seconds
hold = 120 seconds
```

The dedicated GitHub Actions workflow calculates a hold duration longer than the selected timeout automatically.

## Evidence files

The harness writes:

```text
word-timeout-process-identity.json
word-timeout-cleanup-evidence.json
```

The cleanup helper can also create its temporary/generated cleanup PowerShell script beside the identity file. Treat the complete directory as technical acceptance evidence rather than publication output.

The evidence JSON contains:

```text
timeout_seconds
hold_seconds
timeout_observed
timeout_message
identity_recorded
process_found_during_cleanup
forced_termination
accepted
```

The identity file contains only the process-control values needed for exact cleanup; it does not contain manuscript text.

## Acceptance interpretation

A successful harness result means:

- the controlled native command actually timed out;
- Word process identity had been recorded before timeout;
- the exact-identity cleanup path completed without an unsafe identity mismatch; and
- the harness produced accepted evidence.

`forced_termination=false` can be a valid result when Word exits naturally after its automation host is terminated. `forced_termination=true` means the exact still-matching Word process required force termination.

The controlled workflow also performs a broad post-run process-state check. A complete workflow pass therefore requires no remaining `WINWORD` process after both normal merge and timeout-cleanup acceptance.

## Controlled workflow integration

`.github/workflows/word-native-acceptance.yml` runs the timeout cleanup acceptance only after:

1. the controlled runner started with a clean Word process state; and
2. the normal real Word native merge smoke passed.

The workflow then runs the timeout harness, performs the final clean-process check, uploads all available evidence, and fails unless normal merge, timeout cleanup, and final process cleanup all succeeded.

This workflow is manual-only and requires:

```text
[self-hosted, Windows, X64, docmergeforge-word]
```

The Ubuntu fidelity workflow executes only mocked/static regression coverage for this harness. It does not run Microsoft Word.

## What is still not proven until the workflow actually runs

Committing this harness does not prove:

- Microsoft Word is installed or licensed on a controlled runner;
- a real Word process survived long enough to require forced termination;
- every Word build behaves identically after automation-host termination;
- every COM deadlock can be recovered;
- external Office add-ins cannot affect cleanup;
- operating-system crashes or physical machine failure are recoverable by this mechanism; or
- Word is suitable for production unattended merging.

Record the real workflow run ID, environment metadata, timeout evidence, pre/post process-state evidence, and any deviations before citing this acceptance externally.

## Production policy

Even after a passing real timeout-cleanup run:

```text
word.production_ready = false
```

remains unchanged until the complete Word fidelity/application integration matrix, representative corpora, packaged integration where claimed, and human rendering/behavior review are complete.

See also:

- [Microsoft Word Native Merge Acceptance](word-native-merge-acceptance.md)
- [DOCX Fidelity Adapters and Acceptance](docx-fidelity-acceptance.md)
- [Testing and CI](testing-and-ci.md)
- [Known Limitations](known-limitations.md)
- [Release Evidence Ledger](release-evidence.md)
