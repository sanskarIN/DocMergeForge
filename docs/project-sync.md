# Project Synchronization

`docmergeforge project-sync` is a local project-maintenance command for rebuilding a project's explicit `selected_files` list from the numbered PDF/DOCX sources currently present in its configured source folders.

It is designed around a review-first rule: **preview is the default; mutation requires explicit approval.**

## What synchronization changes

Synchronization changes only the project JSON metadata field `selected_files`.

It does **not**:

- rename source files;
- delete manuscript files;
- move files between folders;
- convert PDF/DOCX content;
- merge a publication;
- modify companion archives;
- change expected part-range settings;
- change PDF/DOCX merge settings.

## Preview first

```bash
docmergeforge project-sync --project "./Book.json"
```

The command loads the project and a SHA-256 content revision from the **same exact byte snapshot** before synchronization planning begins. That revision is retained for a later approved apply so project-file changes that happen between load/preview and replacement can be detected instead of silently overwritten.

The preview scans the project's configured source folders recursively. If the output folder is strictly nested below a source root, the scanner excludes that output subtree **before hashing or PDF inspection** so old publications, staging/report artifacts, and transaction residue do not become synchronization candidates or consume document-inspection work.

The automatic proposal contains only files that are:

1. classified as PDF or DOCX;
2. assigned a detected part number; and
3. inside the project's configured `expected_start`/`expected_end` range.

Companion archives, unsupported files, unnumbered PDF/DOCX material, and out-of-range PDF/DOCX files are not placed in the automatic proposal.

## Deterministic order

Eligible paths are de-duplicated using the same platform-aware resolved-path identity approach used by explicit project selection.

The proposal is then ordered by:

1. detected part number;
2. document kind;
3. natural filename order; and
4. normalized full path as a deterministic final tie breaker.

This means filesystem directory enumeration order is not used as publication order.

## Duplicate-part ambiguity

Synchronization detects duplicate part numbers **per document kind** before an apply can occur.

For example, this is ambiguous and blocks apply:

```text
Part 1.pdf
Part 1 copy.pdf
```

Likewise, two DOCX candidates for Part 1 are ambiguous.

This is **not** considered a duplicate conflict:

```text
Part 1.pdf
Part 1.docx
```

PDF and DOCX are independent manuscript pipelines, so one PDF Part 1 and one DOCX Part 1 are expected in a dual-format publication.

The preview keeps all detected candidates visible instead of silently picking a winner. It reports same-kind duplicate numbers in `duplicate_parts.pdf` and `duplicate_parts.docx`, and sets `safe_to_apply=false` when either list is non-empty.

An apply with an ambiguous same-kind duplicate set exits with code `2` before removal approval, backup creation, or project replacement. Resolve/rename/remove the unintended duplicate source candidate, preview again, and only then consider applying the new selection.

## Missing-part evidence

Synchronization also compares the automatic proposal with the project's expected inclusive part range for every manuscript kind that is actually present.

For expected Parts 1–3:

```text
Part 1.pdf
Part 3.pdf
```

produces:

```json
{
  "missing_parts": {
    "pdf": [2],
    "docx": []
  },
  "numbering_complete_for_available_kinds": false
}
```

If the project currently contains no DOCX synchronization candidates, the preview does not fabricate Parts 1–3 as missing DOCX items. Missing-part evidence is calculated only for a kind that has at least one eligible source candidate.

`numbering_complete_for_available_kinds=true` requires:

- at least one proposed mergeable source;
- no same-kind duplicate part numbers; and
- no missing expected part numbers for each available manuscript kind.

Missing parts do **not** make a synchronization plan unsafe to write. `safe_to_apply` is intentionally limited to synchronization ambiguity such as duplicate candidates. An operator may need to persist a partial work-in-progress selection while Parts are still arriving. Therefore a preview can report `safe_to_apply=true` and `numbering_complete_for_available_kinds=false` at the same time.

That does not make the project publishable. Project dry-run/preflight remains the authoritative merge-readiness gate.

## Preview JSON

A preview reports fields including:

- `changed`;
- `safe_to_apply`;
- `numbering_complete_for_available_kinds`;
- `current_count`;
- `proposed_count`;
- `current`;
- `proposed`;
- `added`;
- `removed`;
- `reordered`;
- `duplicate_parts.pdf`;
- `duplicate_parts.docx`;
- `missing_parts.pdf`;
- `missing_parts.docx`;
- `project`;
- `applied`;
- `approval_required`;
- `removal_approval_required`;
- `backup`.

`safe_to_apply` is a synchronization-ambiguity signal, not a publication-readiness claim. `numbering_complete_for_available_kinds` is only numbered-source completeness evidence. Even when both are true, encrypted inputs, corrupt documents, insufficient storage, output conflicts, or other conditions can still cause project preflight to reject publication.

Paths can reveal private workstation information. Treat saved preview logs as potentially sensitive metadata.

## Apply additions and reordering

After reviewing the preview:

```bash
docmergeforge project-sync --project "./Book.json" --apply
```

If the proposal is unambiguous and only adds paths and/or changes the deterministic order, the command can apply it directly.

Before a changed apply is allowed to write, DocMergeForge verifies that the project file still has the exact content revision captured when the command loaded it. This is stricter than semantic object comparison: even byte-level drift such as external JSON reformatting is treated as a stale snapshot and requires a fresh preview. The existing semantic re-load comparison remains as an additional defense for callers that do not supply an exact revision token.

A changed project gets a backup before atomic replacement. The first backup is normally:

```text
Book.json.bak
```

If that backup already exists it is preserved and a versioned backup is used, for example:

```text
Book.json_v2.bak
Book.json_v3.bak
```

Immediately before the final project replacement, the guarded save checks the expected content revision again. If the file changed during the apply path, the replacement is refused and the caller's in-memory selection is restored. A backup already created before that late failure is intentionally retained for review/recovery.

An unchanged, unambiguous proposal is a true no-op: no backup or project rewrite is performed.

An unchanged but ambiguous proposal is still refused when `--apply` is requested. The absence of a metadata diff does not make duplicate source identity safe.

## Removal protection

Existing `selected_files` can intentionally contain material outside the automatic numbered rule, such as:

- cover/front-matter DOCX files;
- prefaces;
- appendices;
- unnumbered legal/copyright pages;
- reviewed out-of-range special material.

Those paths appear in the preview's `removed` list because they are not members of the automatic numbered/in-range proposal.

For that reason, this command refuses an apply that contains removals unless a second explicit approval is supplied:

```bash
docmergeforge project-sync \
  --project "./Book.json" \
  --apply \
  --allow-removals
```

Use `--allow-removals` only after checking every item in `removed`. The flag removes those paths from project metadata; it still does not delete the source files from disk.

Duplicate-part ambiguity is checked before the removal-approval gate. `--allow-removals` cannot override `safe_to_apply=false` and must never be used as a way to pick between duplicate source candidates.

## Write-safety behavior

The apply path has additional safeguards:

- same-kind duplicate numbered candidates block apply before any write;
- nested project output files are excluded before scanner hashing/PDF inspection;
- a project file addressed through a symbolic link is refused;
- the project and its SHA-256 revision are loaded from one exact byte snapshot;
- the synchronization plan records its current-selection baseline;
- if that selection changes before apply, the stale plan is rejected;
- if the project bytes change after the snapshot, exact revision checks reject the stale write even when the parsed JSON would still be semantically equivalent;
- the parsed on-disk project is also compared with the in-memory project before backup/write;
- the existing project JSON is copied to a durable versioned backup before replacement;
- the final guarded save rechecks the expected revision immediately before the shared atomic text-save path;
- the atomic save writes a unique sibling temporary file, flushes it, requests `fsync`, then uses `os.replace(...)`;
- if project saving fails, the caller's in-memory selection is restored;
- an already-created backup is retained for recovery/review;
- CLI `OSError`/validation failures are returned as structured JSON with exit code `2`.

The revision check is an **optimistic stale-write guard**, not a universal cross-process lock. An arbitrary external editor that writes in the very small interval after the final revision check and before atomic replacement is not participating in a coordinated lock protocol. For shared/multi-writer project files, use external coordination or version control rather than treating project JSON as a collaborative database.

## Recommended operator workflow

1. Back up important project/source data through your normal backup process.
2. Run `project-sync` without `--apply`.
3. Review `current`, `proposed`, `added`, `removed`, and `reordered`.
4. Confirm `safe_to_apply=true` and both `duplicate_parts` lists are empty.
5. Review `missing_parts` and `numbering_complete_for_available_kinds`; understand that incomplete numbering can still be synchronized but cannot be treated as publication readiness.
6. Confirm that the expected part range is still correct.
7. If no removals are proposed, apply with `--apply` when desired.
8. If removals are proposed, verify each path and use `--allow-removals` only when all removals are intentional.
9. If apply reports that the project changed on disk, stop and run a fresh preview instead of retrying against the stale proposal.
10. Keep the generated `.bak` project file until the changed project has been validated.
11. Run project preflight:

```bash
docmergeforge merge --project "./Book.json" --dry-run
```

12. Review ordered PDF/DOCX inputs, missing/duplicate diagnostics, encrypted-input status, output paths, and storage evidence.
13. Only then run the full publication command.

## Exit behavior

- `0`: preview succeeded, an unambiguous no-op succeeded, or an approved apply succeeded.
- `2`: duplicate-part ambiguity blocks apply, an apply requires removal approval, or a handled synchronization write/safety failure occurred.

A missing-part report does not by itself change the synchronization command's exit code; publication readiness belongs to project preflight.

Malformed/unreadable project files can still fail during project loading according to the normal project-file validation rules.

## Recovery from an unwanted metadata change

If an applied proposal was not what you intended, do not change manuscript files just to match the project. Instead:

1. stop before publication;
2. inspect the project JSON and its `.bak` file;
3. copy the intended backed-up project configuration to a separate review location;
4. restore the intended project metadata through a controlled/atomic save or verified file replacement;
5. run `project-sync` preview again if useful;
6. run `merge --dry-run` and review all resolved inputs before publishing.

A synchronization backup protects the project configuration only. It is not a manuscript-content backup.

## Related documentation

- [Project Files](project-files.md)
- [CLI Reference](cli-reference.md)
- [Validation and Preflight](validation-and-preflight.md)
- [Merge Pipeline](merge-pipeline.md)
- [Security Model](security.md)
- [Privacy](privacy.md)
