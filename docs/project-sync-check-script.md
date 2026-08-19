# Project Sync Drift Check Script

The repository provides a non-mutating automation helper for checking whether a saved project selection still matches the current deterministic automatic source proposal:

```bash
python scripts/check_project_sync.py --project "./Book.json"
```

The script loads the project, builds the same synchronization proposal used by the maintained project-sync core, prints structured JSON, and exits without modifying the project or manuscript files.

## Exit codes

- `0` — the saved `selected_files` sequence exactly matches the deterministic proposal and the proposal has no same-kind duplicate-part ambiguity.
- `2` — the selection has drifted or duplicate same-kind candidates make the automatic proposal ambiguous.

A missing expected manuscript part does **not** by itself make this drift check fail. Missing numbers remain separate validation/preflight evidence. This allows a work-in-progress project to have a synchronized selection even while the manuscript is incomplete.

## Important JSON fields

The output includes the synchronization-plan evidence plus:

- `project` — the project file passed to the script;
- `in_sync` — the automation-oriented selection/ambiguity result;
- `changed` — whether current and proposed selected-file sequences differ;
- `safe_to_apply` — whether same-kind duplicate-part ambiguity is absent;
- `duplicate_parts` — duplicate PDF/DOCX part numbers;
- `missing_parts` — missing expected numbers for manuscript kinds that are currently available;
- `numbering_complete_for_available_kinds` — numbered-source completeness evidence.

## CI example

```bash
python scripts/check_project_sync.py --project "./Book.json"
docmergeforge merge --project "./Book.json" --dry-run
```

The first command checks project-selection drift/ambiguity. The second command remains the publication-readiness gate and can fail for missing parts, encrypted/corrupt input, storage, output, or other validation conditions.

## Safety boundary

The drift script never applies a proposal and has no removal-approval option. It is safe to run in automated verification because it is read-only with respect to project metadata and manuscript sources.

Do not use a passing drift check as proof that a publication is ready to merge. Always run project preflight for that decision.
