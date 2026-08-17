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

### `output_folder`

Destination directory for the publication bundle.

The output directory must be writable and have enough free space for staging, final artifacts, reports, and possible overwrite rollback backups.

### `settings`

Nested merge/PDF/DOCX settings described below.

### `selected_files`

Optional explicit list of selected paths. The desktop order-selection workflow can use this to preserve chosen file/order information instead of silently replacing it with a fresh automatic order.

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

Project saving uses a temporary sibling path and replaces the final project file only after the complete JSON text is written. This reduces the chance of leaving a partially written JSON project after a normal write interruption.

The project file itself is still not a backup of the source manuscript. Back up important project files independently.

## Compatibility behavior

The loader supplies defaults for several missing settings so older/minimal project files can continue to load when fields were not present. The following project fields are required by the current loader:

- `name`;
- `source_folders`;
- `output_folder`.

Unknown or structurally invalid values can still fail loading. Do not hand-edit production project files without validation.

## Manual editing

Project JSON is human-readable, but editing it directly can create:

- invalid paths;
- inverted/incorrect part ranges;
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

## Version-control guidance

A project file can be committed to Git only when its paths/settings are safe to publish and useful to collaborators. Avoid committing machine-specific absolute paths or private publication filenames.

For reproducible internal workflows, a sanitized project template plus documented source layout is usually safer than committing a personal project file unchanged.
