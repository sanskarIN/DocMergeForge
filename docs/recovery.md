# Publication Recovery

DocMergeForge uses journaled output transactions so a multi-file publication bundle can be rolled back after a normal failure and recovered safely after an abrupt process interruption during final promotion.

This guide covers the transaction model, operator actions, the `recover-output` command, cross-process output locking, conflict handling, and what **not** to delete.

## Why recovery is needed

A publication can include multiple final files:

- PDF manuscript;
- DOCX manuscript;
- reports;
- manifest;
- checksums;
- companion index;
- publishing checklist.

Publishing each file independently creates a dangerous state: the first file could be replaced before a later file fails. DocMergeForge instead stages the complete bundle and promotes it as one transaction.

## Single-writer output lock

Each output directory now has an OS-level non-blocking lock file:

```text
.docmergeforge-output.lock
```

The file itself can remain on disk between runs. Ownership is determined by the operating-system file lock, not by the presence of the filename.

The same exclusive lock is held while:

- a publication transaction creates/stages outputs;
- final outputs are promoted;
- rollback is attempted;
- `recover-output` examines or repairs journaled recovery state.

If another DocMergeForge process already owns the output-directory lock, the second process fails immediately with `OutputLockError` instead of racing the first process.

The OS releases the lock automatically if the owning process exits or crashes. This means a stale `.docmergeforge-output.lock` filename after a crash is not itself evidence that a process is still active.

Do **not** delete the lock file as a way to bypass an active lock. Removing a pathname does not safely coordinate with a process that already has the underlying file open.

The lock is local filesystem coordination. Network filesystems can implement advisory locking differently; real shared-filesystem acceptance remains necessary before claiming robust multi-host locking semantics.

## Transaction folder

A project publication creates a hidden directory inside the output folder with a name beginning:

```text
.docmergeforge-staging-
```

During normal pre-promotion work this folder contains staged outputs. Immediately before final-path mutation, DocMergeForge writes:

```text
transaction.json
```

The journal contains promotion phase and per-output recovery metadata, including staged file fingerprints and whether a previous final file existed.

## Journal phases

Current journal phases are:

- `promoting` — final-path mutation may be in progress or may have been interrupted;
- `committed` — the complete promotion finished;
- `rolled-back` — automatic rollback finished.

A new output transaction refuses to start if a pending journaled transaction exists in the output folder. This prevents a new merge from overwriting evidence needed to recover the older interrupted operation.

## Normal failure behavior

If an exception occurs during promotion, DocMergeForge attempts automatic rollback:

1. remove newly promoted files from the failed transaction;
2. restore backed-up previous outputs;
3. mark the journal `rolled-back`;
4. propagate the original failure.

If rollback succeeds, cleanup can safely remove the transaction directory afterward.

## Incomplete automatic rollback

If automatic rollback itself fails, DocMergeForge deliberately preserves the transaction folder and raises a recovery error.

This is important: deleting the folder at that point could destroy the only backup of a previous publication.

## Abrupt process termination

Examples:

- operating system terminates the process;
- machine loses power;
- user force-kills the process;
- storage/device disconnects during promotion;
- interpreter crashes during final-path replacement.

In these cases Python cleanup code may never run. The operating-system output lock is released automatically, while a `promoting` journal can remain.

The next project publication should detect that pending transaction and fail closed until recovery is completed.

## Recovery command

Use:

```bash
docmergeforge recover-output --output-dir PATH
```

Example:

```bash
docmergeforge recover-output --output-dir "./Master"
```

Recovery first acquires the same exclusive output-directory lock used by publication. If an active DocMergeForge process is still publishing to the directory, recovery refuses to run concurrently.

Successful JSON shape:

```json
{
  "recovered": true,
  "output_dir": "Master",
  "transactions": [
    {
      "folder": "Master/.docmergeforge-staging-...",
      "status": "rolled-back",
      "restored": ["Master/Book.pdf"],
      "removed": ["Master/Book.docx"]
    }
  ]
}
```

If no pending journal directories exist, the command can succeed with an empty transaction list.

## Fail-closed recovery

Recovery does not blindly overwrite/delete whatever currently exists. It compares filesystem state with the journal evidence.

For a newly promoted file that did not exist before the transaction, recovery only deletes the current final file when it matches the staged transaction fingerprint.

For a file with a rollback backup, recovery checks that a current promoted file still matches the transaction when necessary before restoring the previous output.

If the current filesystem does not match safe assumptions, recovery raises `TransactionRecoveryError` and leaves evidence in place.

CLI failure shape:

```json
{
  "recovered": false,
  "output_dir": "Master",
  "error": "..."
}
```

Exit code: `2`.

## Fingerprint checks

The journal records for each staged output:

- staged byte size;
- staged SHA-256.

Recovery uses these fields to avoid deleting a file that somebody modified/replaced after the interrupted transaction.

A fingerprint mismatch is a reason to stop and investigate, not a reason to disable the check.

## Backup restoration

When overwrite is enabled and a final path already exists, promotion can move the previous output into a transaction backup before replacing it.

If the process dies at the wrong moment, that backup may be the only copy of the previously published file at that path.

Therefore:

> Never manually delete a journaled `.docmergeforge-staging-*` folder just because it looks temporary.

## Recovery states by file

The recovery engine evaluates each journal entry conservatively.

Possible actions include:

- **restore** — a rollback backup exists and can safely replace the interrupted promoted file;
- **remove** — a new final file created by the interrupted transaction matches its recorded fingerprint and can be removed;
- **keep** — no filesystem mutation is required for that entry.

All actions are planned before recovery mutations are executed, reducing the risk of discovering an unsafe condition halfway through the recovery loop.

## Already-completed journals

A stale transaction directory whose journal phase is `committed` or `rolled-back` is already at a safe boundary. Recovery can clean that stale transaction directory and report a `cleaned-*` status.

## Corrupt journals

Recovery fails if:

- JSON cannot be read;
- journal version is unsupported;
- phase is invalid;
- entries are missing/empty;
- entry structure is incomplete;
- recorded paths are unsafe;
- fingerprints are invalid;
- expected backup/staging evidence is unavailable.

Do not edit the journal casually to make recovery pass. Preserve a copy first and investigate the filesystem state.

## Path safety

Recovery validates transaction child names and final paths so a journal cannot direct cleanup/restoration outside the intended transaction/output directories.

This is both a safety and security requirement.

## Operator procedure after a crash

1. **Stop new publication attempts** into the affected output folder.
2. Back up the entire output folder, including hidden `.docmergeforge-staging-*` directories, if the contents are important.
3. Do not open/save/modify suspected newly promoted outputs before recovery unless necessary for investigation.
4. Run:

   ```bash
   docmergeforge recover-output --output-dir "<affected-output-folder>"
   ```

5. If recovery succeeds, inspect restored/removed paths.
6. Rerun project dry-run.
7. Verify source hashes/readiness/order/storage again.
8. Start a fresh merge.
9. Inspect final reports/checksums/manifest.

## Procedure when recovery fails closed

If `recover-output` returns `recovered: false`:

1. Do not delete the transaction folder.
2. Copy the output folder/transaction evidence to a safe backup location.
3. Read the error and identify the conflicting final path.
4. Compare current final file size/hash with any release/source records.
5. Determine whether the current final file was changed manually after interruption.
6. Determine whether a transaction backup still exists.
7. Restore files manually only when you can prove which version is authoritative.
8. Keep a record of the manual decision.
9. After the output folder is in a known-safe state, remove stale transaction evidence only deliberately.

For uncertain/high-value publication data, work on a copy rather than experimenting on the only recovery evidence.

## Cancellation versus crash recovery

Graceful cancellation and abrupt process termination are different.

### Graceful cancellation

The application checks cancellation during project/document processing and before output promotion. A normal cancellation should avoid publishing a partial bundle and clean ordinary pre-journal staging.

### Abrupt termination during promotion

The operating-system lock releases when the process dies, but the journal/backups can remain. Use `recover-output`.

## Disk-full behavior

Disk exhaustion can happen during staging or promotion. The project performs storage estimation and a writeability probe before expensive work, but filesystems can still change after preflight.

The transaction/recovery layer is designed to keep failed staging from becoming a successful publication and to preserve recovery evidence if rollback cannot complete.

Never assume “disk full” means all temporary files are safe to delete; check for a transaction journal first.

## Testing recovery and locking

The repository contains automated recovery/cancellation tests, simulated interrupted-promotion coverage, and output-lock tests that verify a second transaction/recovery attempt is rejected while the first lock is active.

These are valuable regression checks but do not replace real forced-process-termination acceptance on each release platform or multi-host/network-filesystem locking acceptance.

Release acceptance should include controlled interruption testing on non-production fixtures.

## Recovery checklist

Before declaring an interrupted output folder safe:

- no active process owns the output-directory publication lock;
- no unresolved `promoting` journal remains;
- previous outputs are either restored or intentionally replaced;
- no unknown file was deleted due to a fingerprint mismatch;
- source/project preflight is rerun;
- output directory is writable;
- storage is sufficient;
- the fresh publication run completes;
- final outputs reopen/validate;
- reports/checksums/manifest match the fresh run.
