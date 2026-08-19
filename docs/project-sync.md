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

The preview scans the project's configured source folders recursively. If the output folder is strictly nested below a source root, the output subtree is excluded so old publications and staging/report artifacts cannot become synchronization candidates.

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

## Preview JSON

A preview reports fields including:

- `changed`;
- `current_count`;
- `proposed_count`;
- `current`;
- `proposed`;
- `added`;
- `removed`;
- `reordered`;
- `project`;
- `applied`;
- `approval_required`;
- `removal_approval_required`;
- `backup`.

Paths can reveal private workstation information. Treat saved preview logs as potentially sensitive metadata.

## Apply additions and reordering

After reviewing the preview:

```bash
docmergeforge project-sync --project "./Book.json" --apply
```

If the proposal only adds paths and/or changes the deterministic order, the command can apply it directly.

A changed project gets a backup before atomic replacement. The first backup is normally:

```text
Book.json.bak
```

If that backup already exists it is preserved and a versioned backup is used, for example:

```text
Book.json_v2.bak
Book.json_v3.bak
```

An unchanged proposal is a true no-op: no backup or project rewrite is performed.

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

## Write-safety behavior

The apply path has additional safeguards:

- a project file addressed through a symbolic link is refused;
- the synchronization plan records its current-selection baseline;
- if that selection changes before apply, the stale plan is rejected;
- the existing project JSON is copied to a durable versioned backup before replacement;
- project replacement uses the shared atomic text-save path;
- the atomic save writes a unique sibling temporary file, flushes it, requests `fsync`, then uses `os.replace(...)`;
- if project saving fails, the caller's in-memory selection is restored;
- the already-created backup is retained for recovery/review;
- CLI `OSError`/validation failures are returned as structured JSON with exit code `2`.

## Recommended operator workflow

1. Back up important project/source data through your normal backup process.
2. Run `project-sync` without `--apply`.
3. Review `current`, `proposed`, `added`, `removed`, and `reordered`.
4. Confirm that the expected part range is still correct.
5. If no removals are proposed, apply with `--apply` when desired.
6. If removals are proposed, verify each path and use `--allow-removals` only when all removals are intentional.
7. Keep the generated `.bak` project file until the changed project has been validated.
8. Run project preflight:

```bash
docmergeforge merge --project "./Book.json" --dry-run
```

9. Review ordered PDF/DOCX inputs, missing/duplicate diagnostics, encrypted-input status, output paths, and storage evidence.
10. Only then run the full publication command.

## Exit behavior

- `0`: preview succeeded, no-op succeeded, or an approved apply succeeded.
- `2`: an apply requires removal approval or a handled synchronization write/safety failure occurred.

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
