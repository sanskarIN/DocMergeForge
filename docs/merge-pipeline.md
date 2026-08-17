# Merge Pipeline

1. Discover candidate files recursively.
2. Classify PDF, DOCX, companion package, or other.
3. Detect numeric part identity.
4. Hash every source.
5. Validate missing/duplicate parts and document readability.
6. Estimate storage before expensive merge work begins.
7. Create a transaction-owned staging directory inside the destination filesystem.
8. Merge PDF and DOCX independently into staged output paths.
9. Reopen and validate the staged document outputs.
10. Re-hash every tracked source and fail if any source changed during the run.
11. Compute output hashes and sizes from the staged documents.
12. Generate the companion index, reports, manifest, optional checksums, and publishing checklist into the same staging transaction.
13. Check cancellation one final time before publication.
14. Promote the complete staged publication bundle to its final paths as one batch.
15. If batch promotion fails, remove newly promoted files and restore the previous published files from transaction-local backups.
16. Remove transaction staging data after success, cancellation, or failure.

## Publication boundary

A project run has one publication boundary. PDF/DOCX outputs are not considered published merely because one merge engine completed; their reports and other generated evidence must also be ready before the transaction is promoted.

This prevents a mixed-format run from replacing the PDF while a later DOCX merge fails, and prevents a report-generation error from leaving document files newer than the report bundle that describes them.

## Cancellation and recovery

Cancellation raises a dedicated `MergeCancelled` exception. Merge engines check cancellation while processing documents and again during finalization. The application service also checks immediately before batch promotion.

Before promotion, cancellation or failure only removes staging data. Existing published outputs remain untouched. During promotion, overwrite targets are temporarily backed up inside the staging directory so a later replacement failure can roll back files already promoted in that batch.

## Storage-failure behavior

Individual document engines use atomic temporary files and the project service uses the outer publication transaction. Automated tests inject `ENOSPC` during an atomic write and verify that the previously published file remains unchanged and temporary `.part` files are removed.

That fault-injection test is a recovery guarantee, not a substitute for a real filled-filesystem acceptance run. Real disk-exhaustion testing remains part of release acceptance.
