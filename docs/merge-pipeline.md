# Merge Pipeline

1. Discover candidate files recursively.
2. Classify PDF, DOCX, companion package, or other.
3. Detect numeric part identity.
4. Hash every source.
5. Validate missing/duplicate parts and document readability.
6. Verify the output destination is writable and estimate storage before expensive merge work begins.
7. Create a transaction-owned staging directory inside the destination filesystem.
8. Merge PDF and DOCX independently into staged output paths.
9. Reopen and validate the staged document outputs.
10. Re-hash every tracked source and fail if any source changed during the run.
11. Compute output hashes and sizes from the staged documents.
12. Generate the companion index, reports, manifest, optional checksums, and publishing checklist into the same staging transaction.
13. Check cancellation one final time before publication.
14. Fingerprint every staged artifact and write a durable `promoting` transaction journal before changing final paths.
15. Move overwrite targets into transaction-local rollback backups, then promote the complete staged publication bundle.
16. Mark the journal `committed` only after all replacements succeed.
17. If in-process promotion fails, remove promoted replacements, restore previous files, and mark the journal `rolled-back`.
18. If automatic rollback itself cannot complete, preserve the journal, staging files, and available backups for explicit recovery rather than deleting uncertain evidence.
19. Remove transaction staging data only after a known safe boundary has been reached.

## Publication boundary

A project run has one publication boundary. PDF/DOCX outputs are not considered published merely because one merge engine completed; their reports and other generated evidence must also be ready before the transaction is promoted.

This prevents a mixed-format run from replacing the PDF while a later DOCX merge fails, and prevents a report-generation error from leaving document files newer than the report bundle that describes them.

## Cancellation and recovery

Cancellation raises a dedicated `MergeCancelled` exception. Merge engines check cancellation while processing documents and again during finalization. The application service also checks immediately before batch promotion.

Before promotion, cancellation or failure only removes staging data. Existing published outputs remain untouched. During promotion, overwrite targets are temporarily backed up inside the staging directory so a later replacement failure can roll back files already promoted in that batch.

Promotion is journaled with the staged file size and SHA-256 fingerprint, whether a final path existed before promotion, and the rollback-backup name when applicable. A new output transaction refuses to start while a journaled interrupted transaction is pending.

Use:

```bash
docmergeforge recover-output --output-dir /path/to/output
```

A pending `promoting` journal is rolled back. Recovery restores available old backups and removes newly published files only when their fingerprints prove they came from the interrupted transaction. If a final file has changed since the interruption, recovery fails closed and leaves the journal/evidence untouched. A stale `committed` or `rolled-back` journal can be cleaned without modifying published files.

This journal supports deterministic recovery from an interrupted promotion boundary. Real abrupt-process-termination acceptance is still a release test: implementation coverage and simulated journal states do not replace killing the process at multiple real promotion points on each supported filesystem/platform.

## Storage-failure behavior

Individual document engines use atomic temporary files and the project service uses the outer publication transaction. Automated tests inject `ENOSPC` during an atomic write and verify that the previously published file remains unchanged and temporary `.part` files are removed.

That fault-injection test is a recovery guarantee, not a substitute for a real filled-filesystem acceptance run. Real disk-exhaustion testing remains part of release acceptance.
