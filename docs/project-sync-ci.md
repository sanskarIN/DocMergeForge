# Project Synchronization Drift Checks

DocMergeForge synchronization separates three questions that automation should not collapse into one result:

1. **Selection drift** — does the saved `selected_files` list still match the deterministic numbered/in-range source proposal?
2. **Synchronization ambiguity** — are there duplicate same-kind candidates for a part number?
3. **Publication completeness** — are expected numbers present for every available manuscript kind?

The core synchronization plan already exposes the evidence needed to keep those concerns separate:

- `changed` reports selected-file drift;
- `safe_to_apply` reports whether the automatic proposal is free of same-kind duplicate ambiguity;
- `duplicate_parts.pdf` and `duplicate_parts.docx` identify ambiguity;
- `missing_parts.pdf` and `missing_parts.docx` report numbering gaps for available kinds;
- `numbering_complete_for_available_kinds` summarizes numbered-source completeness for the available kinds.

A CI-oriented drift check should fail when the saved selection differs from the deterministic proposal or when duplicate source candidates make the proposal ambiguous. It should **not** treat missing manuscript parts as synchronization drift. Missing parts belong to validation/preflight and can exist while a work-in-progress project selection is intentionally synchronized.

Recommended automation sequence:

```text
1. Check project-selection drift/ambiguity.
2. Run `docmergeforge merge --project ... --dry-run`.
3. Treat preflight readiness as the publication-readiness gate.
```

Do not automate `--allow-removals`. Removal approval exists specifically so an operator reviews paths that would stop participating in the explicit project selection.

This document describes the contract for the maintained drift-check surface. The canonical command syntax remains documented in [CLI Reference](cli-reference.md) once the command-level check flag is enabled.
