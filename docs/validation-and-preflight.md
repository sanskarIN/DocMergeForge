# Validation and Preflight

DocMergeForge treats validation as a prerequisite to publication, not an optional final check. The application validates numbered source sets, resolved merge-input safety, storage/destination safety, document-specific risks, output structure, and source integrity at multiple points.

## Numbered-part validation

For each manuscript kind, numbered validation compares discovered part numbers with an inclusive expected range.

Example expected range:

```text
1-120
```

A set is ready only when:

- no expected parts are missing;
- no duplicate part numbers exist; and
- no error/fatal diagnostics block the resolved merge input.

The result records:

- expected parts;
- found parts;
- missing parts;
- duplicate mapping; and
- diagnostics.

## Discovered files versus merge inputs

Validation deliberately sees a broader set than the automatic merge engines.

Automatic PDF/DOCX merge candidates must have a detected part number inside the configured expected range. Unnumbered files and numbered files outside that range remain visible to validation so the user receives diagnostics, but they do not silently become manuscript input.

Example for Parts 1–120:

```text
Part 001.pdf      -> automatic merge input
Part 120.pdf      -> automatic merge input
Part 121.pdf      -> warning / excluded automatically
Book Master.pdf   -> warning / excluded automatically
Front Matter.pdf  -> warning / excluded automatically
```

A project with an explicit persisted `selected_files` list is the deliberate exception. That reviewed selection can contain unnumbered front/back matter or special out-of-range material, and those selected files are treated as real merge inputs for file-specific safety checks.

## Merge-aware blocking diagnostics

File-specific blocking diagnostics such as zero-byte input and encrypted-PDF readiness are bound to the documents that can actually reach the merge engine.

This prevents an excluded old output or out-of-range encrypted PDF from stopping a valid numbered merge that cannot include it. Conversely, an explicitly selected encrypted/zero-byte special document remains blocking until handled safely.

Selected unnumbered encrypted PDFs are also checked before the unnumbered-filename warning is emitted, so reviewed front matter cannot bypass password safety simply because it has no part number.

## CLI validation

```bash
docmergeforge validate --input "./Book" --parts 1-120
```

Output is JSON with separate PDF and DOCX validation results.

Example shape:

```json
{
  "pdf": {
    "ready": true,
    "missing": [],
    "duplicates": {},
    "found": [1, 2, 3],
    "diagnostics": []
  },
  "docx": {
    "ready": true,
    "missing": [],
    "duplicates": {},
    "found": [1, 2, 3],
    "diagnostics": []
  }
}
```

The command exits with code `2` if either checked kind is not ready. Review the diagnostics even when readiness is true because warnings can identify excluded unnumbered/out-of-range files that should be relocated or explicitly reviewed.

## Project output-subtree exclusion

If the project output folder is strictly nested below a configured source root, that output subtree is excluded from project discovery.

This prevents a previous master, report, transaction artifact, or even an old generated file whose name resembles a numbered part from being rediscovered during the next project run.

If source and output are exactly the same directory, the whole directory cannot be excluded; the numbered/in-range automatic-input rule remains the primary protection. A separate source/output layout is recommended.

## Overlapping source roots

Scanner discovery deduplicates files by normalized resolved filesystem identity. If both a parent source directory and one of its child directories are configured, the same physical/resolved file is emitted once rather than creating a false duplicate-part error solely because it was reached through two roots.

## Project dry run

A project dry run is broader than plain part validation.

```bash
docmergeforge merge --project "./Book.json" --dry-run
```

It is read-only with respect to final manuscript publication and reports the evidence needed to decide whether a full run should start.

## Preflight evidence

Current preflight evidence includes:

- resolved PDF merge-input count;
- PDF missing/duplicate parts and readiness;
- PDF diagnostics;
- resolved DOCX merge-input count;
- DOCX missing/duplicate parts and readiness;
- DOCX diagnostics;
- readiness for available document kinds;
- companion count;
- ignored-file count;
- ordered PDF merge-input paths;
- ordered DOCX merge-input paths;
- expected output paths;
- likely DOCX package conflict count for the same resolved DOCX input set; and
- storage estimate and sufficiency based on the files that can actually merge.

Preflight order/conflict evidence and the actual merge service share the same project-input resolver. An unnumbered/out-of-range file therefore cannot appear in one surface as a merge input while being silently excluded/included by the other.

## Expected output calculation

For the SQL Full Mastery preset, output filenames are preset-specific.

For a generic project, DocMergeForge renders the configured project basename and adds `.pdf` and/or `.docx` only for kinds with resolved merge inputs.

Generated basenames are sanitized for cross-platform-invalid characters and bounded to 180 UTF-8 bytes. Very long names receive a deterministic SHA-256-derived suffix before the extension/version suffix is added.

Always inspect `expected_outputs` in the dry-run evidence before publication. This catches naming/location mistakes before expensive work begins.

## DOCX conflict analysis

When resolved DOCX merge inputs are present, preflight calls the DOCX engine conflict analyzer on exactly those inputs and reports a conflict count.

A non-zero count does not automatically prove the merge will fail; it indicates package/style/numbering complexity that deserves inspection, especially for large real-world Word documents.

Portable composition cannot promise perfect fidelity for every OOXML feature. See [DOCX Engine](docx-engine.md).

## Storage estimate

The current storage estimator calculates:

```text
source_bytes = sum of resolved existing merge-input sizes
projected_output_bytes = max(source_bytes, 1)
temporary_bytes = 1.25 × projected_output_bytes
safe_required_bytes = projected_output_bytes + temporary_bytes + 128 MiB
```

It then compares `safe_required_bytes` to free bytes on the filesystem containing the nearest existing output-path anchor.

This estimate is deliberately conservative but is still an estimate, not a mathematical upper bound for every pathological document or filesystem.

## Output writeability probe

Before expensive project merge work, DocMergeForge verifies that the output location can actually host transaction staging.

The probe:

1. creates the output directory if needed;
2. creates a temporary `.docmergeforge-write-probe-*` file inside it;
3. closes the file;
4. removes the probe; and
5. raises `OutputAccessError` if creation fails.

This catches cases where free-space checks alone would be misleading because the directory is read-only or otherwise inaccessible.

## Storage limitations and overwrite transactions

A full transaction can temporarily need more space than the new output alone because an existing published file may be moved into the transaction directory as a rollback backup while the replacement is promoted.

For especially large overwrite operations:

- keep more free space than the reported minimum where practical;
- avoid nearly-full filesystems;
- do not use unstable/removable/network storage unless its semantics are understood;
- run the manual stress workflow or a local representative acceptance run before release.

## Encrypted PDFs

Plain source validation does not unlock encrypted PDFs.

Project/direct merge workflows collect passwords only for encrypted PDFs in the resolved merge input. An excluded out-of-range/unnumbered encrypted PDF therefore does not produce an irrelevant password prompt.

A project dry run invoked through `merge` collects needed merge-input PDF passwords and passes an `allow_encrypted_pdf` readiness signal into preflight.

Passwords are not stored in preflight evidence.

## Strict project-file boundary

Saved merge-project JSON is publication-critical configuration and is loaded fail-closed rather than treated like disposable UI preference data.

The loader validates required non-empty names/paths, source-folder arrays, selected-file arrays, warning/state/checkpoint types, positive non-decreasing part ranges, booleans such as `overwrite`, PDF option types/choices, and DOCX fidelity/conflict-policy choices.

For example:

```json
{"overwrite": "false"}
```

is rejected because a non-empty string would otherwise be truthy in Python and could accidentally change replacement behavior. Missing known fields can still use documented defaults; malformed known fields are not silently coerced.

## Source-integrity validation

Discovery captures SHA-256 hashes of inputs. Full project publication later revalidates source integrity before final promotion.

Only resolved manuscript inputs plus companion references are bound into the active publication integrity snapshot. Excluded unrelated PDF/DOCX review files are not silently promoted into source identity.

If an active input changes:

- do not publish the staged bundle;
- treat the run as failed; and
- rerun discovery/preflight using the new source state.

## PDF output validation

PDF completion is not accepted simply because pages were appended successfully. The generated PDF is reopened and its expected page evidence is checked.

Additional publication helpers such as title pages, bookmarks, metadata, page overlays, headers/footers/watermarks, and numbering are applied through the PDF pipeline and must survive reopening.

## DOCX output validation

DOCX validation checks the output as an OOXML ZIP package, including required package members and XML parseability, and reopens it through the document parser.

This catches malformed ZIP/XML packages that a simple file-exists check would miss.

## Publication-bundle validation

A full project run stages both manuscript outputs and generated evidence before the final publication boundary.

Typical staged artifacts include:

- PDF output;
- DOCX output;
- manifest;
- checksums;
- reports;
- companion index; and
- publishing checklist.

If later report generation or source revalidation fails, final outputs should not be partially updated.

## Validation vs audit vs compare

These are different concepts.

### Validation

Determines structural/readiness conditions such as part completeness, resolved merge-input safety, and output integrity.

### Audit

Scans manuscript content for findings and reports them without rewriting originals.

```bash
docmergeforge audit --input "./Book"
```

### Compare

Checks merged output evidence against the source set.

```bash
docmergeforge compare --input "./Book" --pdf-output "./Master/Book.pdf"
```

Comparison is a review surface and can intentionally inspect a broader source set than automatic merge-input resolution. Interpret its evidence accordingly.

## Recommended acceptance sequence

1. Back up originals.
2. Run `validate` and review diagnostics.
3. Resolve missing/duplicate parts.
4. Relocate or explicitly review unnumbered/out-of-range manuscript-like files.
5. Create/open the project.
6. Run `merge --dry-run`.
7. Review exact resolved input order and expected outputs.
8. Check destination writeability and storage sufficiency.
9. Inspect DOCX conflict/risk evidence.
10. Execute the merge.
11. Confirm successful transactional promotion.
12. Review reports/checksums/manifest.
13. Run `compare`.
14. Run `audit` when publication requirements call for it.
15. Open final PDF/DOCX in independent reader/editor applications for human acceptance.

## What validation does not prove

Automated validation does not prove:

- every page is visually perfect;
- every advanced Word feature is preserved exactly;
- every font is installed on every reader machine;
- screen-reader usability is fully accepted by humans;
- signed/notarized package distribution is complete; or
- a synthetic stress run represents every multi-gigabyte real manuscript.

Those are separate acceptance gates documented in [Known Limitations](known-limitations.md) and [Release Process](release-process.md).
