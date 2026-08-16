# Merge Pipeline

1. Discover candidate files recursively.
2. Classify PDF, DOCX, companion package, or other.
3. Detect numeric part identity.
4. Hash every source.
5. Validate missing/duplicate parts and document readability.
6. Estimate storage.
7. Merge PDF and DOCX independently.
8. Write to temporary files.
9. Reopen and validate temporary outputs.
10. Atomically place validated outputs.
11. Re-hash every source and fail if any changed.
12. Generate manifest, checksums, companion index, reports, and publishing checklist.

Cancellation raises a dedicated exception before final placement. A partial file is never presented as a successful final artifact.
