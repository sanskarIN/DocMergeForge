# Project Files

DocMergeForge project files are UTF-8 JSON documents that describe a repeatable merge configuration. They are used by the CLI and desktop application to preserve source locations, output location, expected part range, PDF/DOCX settings, selected-file order, state, checkpoints, and warnings.

Project files are configuration records, not containers. They do **not** embed manuscript bodies or encrypted-PDF passwords.

## Create a project from the CLI

```bash
docmergeforge project-create \
  --input "./Book" \
  --output-dir "./Master" \
  --project-file "./Book.json" \
  --name "Book Master Edition" \
  --parts 1-120
```

For the SQL preset:

```bash
docmergeforge project-create \
  --input "./SQL-Full-Mastery" \
  --output-dir "./SQL-Master" \
  --project-file "./sql-full-mastery.json" \
  --sql-preset
```

## Run a project

Dry-run/preflight:

```bash
docmergeforge merge --project "./Book.json" --dry-run
```

Full execution:

```bash
docmergeforge merge --project "./Book.json"
```

## Synchronize selected files from current sources

`project-sync` is an explicit project-maintenance workflow for rebuilding `selected_files` from the numbered PDF/DOCX files currently present in the configured source folders. It is deliberately **preview-only by default**.

Preview the proposed selection:

```bash
docmergeforge project-sync --project "./Book.json"
```

The command scans the project source roots and proposes only mergeable PDF/DOCX files that:

- have a detected part number;
- fall inside the project's configured inclusive expected range; and
- resolve to a unique platform-aware path identity.

When the output folder is strictly nested under a source root, project discovery excludes that output tree during recursive traversal. Excluded directories are pruned before their files reach classification, PDF inspection, byte-size evidence collection, or SHA-256 hashing. Normal project runs and `project-sync` share this same discovery boundary.

The proposed order is deterministic: part number first, then document kind, natural filename ordering, and normalized full path as the final tie breaker.

Preview JSON includes `current`, `proposed`, `added`, `removed`, `reordered`, counts, approval flags, same-kind duplicate-part evidence, missing-part evidence, `safe_to_apply`, and `numbering_complete_for_available_kinds`. A preview never writes the project or a backup.

Two automatic candidates of the same kind claiming the same part number are ambiguous. For example, two Part 1 PDFs set `safe_to_apply=false` and block apply. One Part 1 PDF plus one Part 1 DOCX is valid because those are separate manuscript pipelines.

`missing_parts` is calculated for each manuscript kind that has at least one eligible synchronization candidate. Missing expected numbers make `numbering_complete_for_available_kinds=false`, but do not by themselves block a metadata update. A work-in-progress selection can therefore be synchronized while incomplete; publication readiness must still be established with project preflight.

After reviewing an unambiguous proposal, apply an addition/reorder-only change with:

```bash
docmergeforge project-sync --project "./Book.json" --apply
```

If the proposal would remove any path already stored in `selected_files`, `--apply` fails closed with exit code `2`. This matters because an existing selection can intentionally contain unnumbered prefaces, appendices, covers, or other manually reviewed material that the automatic numbered-source proposal does not include.

Only after reviewing the `removed` list should intentional removals be approved with both flags:

```bash
docmergeforge project-sync \
  --project "./Book.json" \
  --apply \
  --allow-removals
```

`--allow-removals` cannot override duplicate-part ambiguity.

Before a changed synchronization is written, the project currently on disk is loaded again and compared semantically with the project instance used for the operation. If settings, source/output locations, selection, state, warnings, or checkpoint data changed on disk after load, synchronization refuses the stale write and requires a fresh load/preview.

A changed approved project is backed up before replacement. The first backup is normally `Book.json.bak`; existing backups are preserved with versioned names such as `Book.json_v2.bak`. The new project file is then saved through the same atomic text-persistence path used by normal project saving.

Additional safeguards:

- same-kind duplicate numbered candidates block apply before any project write;
- unchanged unambiguous proposals are true no-ops and create no backup;
- synchronization refuses to write a project file addressed through a symbolic link;
- a synchronization plan is rejected if the in-memory selection changed after the plan was created;
- a project changed semantically on disk after load is rejected instead of being overwritten;
- backup/project write `OSError`s are reported as structured CLI JSON failures;
- a failed project replacement leaves the already-created backup available for recovery and restores the caller's in-memory selection;
- synchronization changes only project metadata; it does not rename, delete, move, convert, or modify manuscript source files.

The on-disk comparison reduces stale-write risk but is not a universal lock against arbitrary external editors. Normal project persistence remains atomic and logically last-writer-wins rather than a collaborative multi-writer protocol.

`project-sync` is not a replacement for project preflight. After applying a proposal, run:

```bash
docmergeforge merge --project "./Book.json" --dry-run
```

and review the resolved PDF/DOCX order, validation diagnostics, and storage evidence before publication.

## Top-level schema

A saved project contains these top-level fields:

```json
{
  "name": "Book Master Edition",
  "source_folders": ["Book"],
  "output_folder": "Master",
  "settings": {},
  "selected_files": [],
  "state": "CREATED",
  "last_successful_checkpoint": null,
  "warnings": []
}
```

The serializer currently writes the full dataclass structure, including default settings.

### `name`

Human-readable project name. The SQL preset uses a fixed preset name internally so preset-specific readiness behavior can be applied.

### `source_folders`

List of paths scanned for PDF, DOCX, companion, and other files.

Paths are serialized as strings. They can be relative or absolute depending on how the project was created/saved. For portable project files, prefer a stable directory layout and test the project after moving it.

Explicit selected-path identity follows platform path normalization rather than unconditional case folding. This avoids incorrectly treating case-distinct POSIX paths as the same source while retaining normal case-insensitive behavior where the platform path rules provide it.

### `output_folder`

Destination directory for the publication bundle.

The output directory must be writable and have enough free space for staging, final artifacts, reports, and possible overwrite rollback backups.

### `settings`

Nested merge/PDF/DOCX settings described below.

### `selected_files`

Optional explicit list of selected paths. The desktop order-selection workflow can use this to preserve chosen file/order information instead of silently replacing it with a fresh automatic order.

A repeated selected path is rejected rather than merged twice. Path aliases that resolve to the same path are treated as the same selection.

When `project-sync` is used, its proposal represents the current automatic numbered/in-range PDF/DOCX source set. Existing explicit material outside that automatic rule appears in `removed`; it is never deleted from disk, but replacing `selected_files` with the proposal would stop that path from participating as an explicit merge selection. That is why an apply containing removals requires the separate `--allow-removals` approval.

### `state`

Current project lifecycle state. Supported values in the current model are:

- `CREATED`
- `DISCOVERING`
- `VALIDATING`
- `READY`
- `MERGING`
- `VERIFYING`
- `REPORTING`
- `SUCCEEDED`
- `FAILED`
- `CANCELLED`

Project state is useful for workflow/recovery UX; it is not a substitute for validating the actual filesystem before resuming.

### `last_successful_checkpoint`

Optional checkpoint identifier used by recovery/resume workflows.

Checkpoint persistence is ordered conservatively: the recovery snapshot is saved first, and the live in-memory project is updated to the new checkpoint only after the save succeeds. A failed checkpoint write therefore does not falsely claim a newer persisted recovery boundary.

### `warnings`

List of project-level warning strings retained with the project.

## Merge settings

The `settings` object currently supports:

```json
{
  "expected_start": 1,
  "expected_end": 120,
  "checksum_generation": true,
  "automatic_validation": true,
  "overwrite": false,
  "profile_name": "Exact Preservation",
  "filename_template": "{series}_Master",
  "pdf": {},
  "docx": {}
}
```

### `expected_start` / `expected_end`

Inclusive numbered-part range expected during validation.

The range is deliberately bounded at every maintained entry point:

- part numbers must be positive;
- `expected_end` must be greater than or equal to `expected_start`;
- the largest supported numbered part is **999,999**, matching the six-digit filename detector boundary;
- one expected range may contain at most **10,000 parts**.

The 10,000-part span limit prevents malformed project/CLI input from forcing validation to materialize unbounded missing-part lists and diagnostics. Normal book/manuscript projects are far below this bound. Project loading, project saving, CLI `--parts` parsing, and validation services all enforce the same shared range contract.

### `checksum_generation`

Controls checksum evidence generation for project publication where supported.

### `automatic_validation`

Enables automatic validation behavior in project publication.

### `overwrite`

When `false`, output naming/versioning behavior avoids replacing an existing final path. When `true`, transactional publication can back up an existing final file during promotion so rollback remains possible.

Do not turn overwrite on merely to suppress naming conflicts. Confirm that replacing the existing publication is intentional.

### `profile_name`

Publication/profile label. Default: `Exact Preservation`.

### `filename_template`

Base naming template used by project output naming. Default: `{series}_Master`.

Rendered output basenames are normalized for cross-platform-invalid characters and Windows reserved device names. Windows device-name protection applies to the component before the first dot, so names such as `CON`, `CON.txt`, `COM1.release`, and `LPT9.final.copy` are made safe instead of only checking exact extensionless names.

Very long names are capped at **180 UTF-8 bytes** before the final extension/version suffix is added. When truncation is necessary, DocMergeForge appends a deterministic 12-hex SHA-256-derived suffix so two different long names are unlikely to collapse to the same truncated basename.

This bound is a conservative filename-component safety measure; complete path limits still depend on the selected operating system, filesystem, mount, and parent-directory depth. Preflight/output write checks remain authoritative for the actual destination.

## PDF settings

Default PDF settings:

```json
{
  "add_part_bookmarks": true,
  "title": null,
  "author": null,
  "edition": null,
  "include_title_page": false,
  "visible_toc": false,
  "page_numbers": false,
  "page_number_start": 1,
  "header_text": null,
  "footer_text": null,
  "watermark_text": null,
  "optimization": "preserve"
}
```

See [PDF Engine](pdf-engine.md) for behavioral details.

## DOCX settings

Default DOCX settings:

```json
{
  "start_each_part_on_new_page": true,
  "preserve_sections": true,
  "fidelity_mode": "portable",
  "add_part_headings": true,
  "create_toc_field": true,
  "style_conflict_policy": "prefer_master",
  "numbering_conflict_policy": "remap",
  "header_text": null,
  "footer_text": null,
  "continuous_page_numbering": true
}
```

See [DOCX Engine](docx-engine.md).

## Atomic project saving

Project saving first validates the shared expected-part range contract, then uses the shared atomic text-persistence helper. Each save creates a **unique sibling temporary file**, writes UTF-8 JSON, flushes and `fsync`s that temporary file, and promotes it with `os.replace(...)` only after the write completes.

If range validation, writing, or replacement fails, an invalid new project file is not published. Write/promotion failures remove the temporary file and preserve the previously published project file.

Multiple writers no longer contend on one predictable `<project>.tmp` filename, although concurrent saves are still logically last-writer-wins and should not be used as a collaborative editing protocol. `project-sync` adds a semantic on-disk recheck immediately before its backup/write path, but arbitrary external writers that change the file after that check are still outside a universal coordinated lock.

The project file itself is still not a backup of the source manuscript. Back up important project files independently.

## Compatibility behavior

The loader supplies defaults for several missing settings so older/minimal project files can continue to load when fields were not present. The following project fields are required by the current loader:

- `name`;
- `source_folders`;
- `output_folder`.

Unknown or structurally invalid values can still fail loading. This is intentional: an explicitly opened publication project is not treated like disposable UI preference/history metadata, and DocMergeForge does not silently invent project-critical configuration when the JSON is malformed.

Do not hand-edit production project files without validation.

## Manual editing

Project JSON is human-readable, but editing it directly can create:

- invalid paths;
- inverted, oversized, or otherwise unsupported part ranges;
- unsupported fidelity modes/policies;
- accidental overwrite behavior;
- selected-file ordering that no longer matches source folders;
- invalid lifecycle states.

Prefer the desktop settings UI or `project-create` for normal changes. If manual edits are required, immediately run:

```bash
docmergeforge merge --project "./Book.json" --dry-run
```

## Moving a project

When moving a project between machines:

1. copy the project file;
2. copy or remap the source manuscripts;
3. choose a valid output location;
4. verify path semantics on the new OS;
5. run a dry run;
6. review detected order and storage;
7. never assume a saved `SUCCEEDED` state means the moved filesystem is still valid.

Windows drive-letter paths will not work unchanged on macOS/Linux, and POSIX paths will not work unchanged on Windows.

## Security and privacy

Project files may reveal local filesystem paths, project titles, and configuration choices. Treat them as potentially sensitive metadata if shared publicly.

They should not contain:

- encrypted-PDF passwords;
- API secrets;
- access tokens;
- private manuscript body content beyond what is inherently present in filenames/paths.

Project synchronization does not copy manuscript content into the project file, but its JSON preview can reveal source paths. Review captured CLI logs before sharing them publicly.

## Version-control guidance

A project file can be committed to Git only when its paths/settings are safe to publish and useful to collaborators. Avoid committing machine-specific absolute paths or private publication filenames.

For reproducible internal workflows, a sanitized project template plus documented source layout is usually safer than committing a personal project file unchanged.
