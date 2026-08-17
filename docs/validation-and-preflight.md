# Validation and Preflight

DocMergeForge treats validation as a prerequisite to publication, not an optional final check. The application validates numbered source sets, storage/destination safety, document-specific risks, output structure, and source integrity at multiple points.

## Numbered-part validation

For each manuscript kind, numbered validation compares discovered part numbers with an inclusive expected range.

Example expected range:

```text
1-120
```

A set is ready only when:

- no expected parts are missing;
- no duplicate part numbers exist;
- no error/fatal diagnostics block the set.

The result records:

- expected parts;
- found parts;
- missing parts;
- duplicate mapping;
- diagnostics.

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
    "found": [1, 2, 3]
  },
  "docx": {
    "ready": true,
    "missing": [],
    "duplicates": {},
    "found": [1, 2, 3]
  }
}
```

The command exits with code `2` if either checked kind is not ready.

## Project dry run

A project dry run is broader than plain part validation.

```bash
docmergeforge merge --project "./Book.json" --dry-run
```

It is read-only with respect to final manuscript publication and reports the evidence needed to decide whether a full run should start.

## Preflight evidence

Current preflight evidence includes:

- PDF input count;
- PDF missing/duplicate parts and readiness;
- DOCX input count;
- DOCX missing/duplicate parts and readiness;
- readiness for available document kinds;
- companion count;
- ignored-file count;
- ordered PDF paths;
- ordered DOCX paths;
- expected output paths;
- likely DOCX package conflict count;
- storage estimate and sufficiency.

## Expected output calculation

For the SQL Full Mastery preset, output filenames are preset-specific.

For a generic project, DocMergeForge renders the configured project basename and adds `.pdf` and/or `.docx` only for kinds actually discovered.

Always inspect `expected_outputs` in the dry-run evidence before publication. This catches naming/location mistakes before expensive work begins.

## DOCX conflict analysis

When DOCX inputs are present, preflight calls the DOCX engine conflict analyzer and reports a conflict count.

A non-zero count does not automatically prove the merge will fail; it indicates package/style/numbering complexity that deserves inspection, especially for large real-world Word documents.

Portable composition cannot promise perfect fidelity for every OOXML feature. See [DOCX Engine](docx-engine.md).

## Storage estimate

The current storage estimator calculates:

```text
source_bytes = sum of existing input sizes
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
4. removes the probe;
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

Project/direct merge workflows can collect passwords and then allow encrypted-PDF validation/merge when the password is verified.

A project dry run invoked through `merge` first collects needed PDF passwords and passes an `allow_encrypted_pdf` readiness signal into preflight.

Passwords are not stored in preflight evidence.

## Source-integrity validation

Discovery captures SHA-256 hashes of inputs. Full project publication later revalidates source integrity before final promotion.

This protects against a source file being edited/replaced while a long merge is running.

If an input changes:

- do not publish the staged bundle;
- treat the run as failed;
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
- companion index;
- publishing checklist.

If later report generation or source revalidation fails, final outputs should not be partially updated.

## Validation vs audit vs compare

These are different concepts:

### Validation

Determines structural/readiness conditions such as part completeness and output integrity.

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

For a production publication, all three can be useful.

## Recommended acceptance sequence

1. Back up originals.
2. Run `validate`.
3. Resolve missing/duplicate parts.
4. Create/open the project.
5. Run `merge --dry-run`.
6. Review exact order and expected outputs.
7. Check destination writeability and storage sufficiency.
8. Inspect DOCX conflict/risk evidence.
9. Execute the merge.
10. Confirm successful transactional promotion.
11. Review reports/checksums/manifest.
12. Run `compare`.
13. Run `audit` when publication requirements call for it.
14. Open final PDF/DOCX in independent reader/editor applications for human acceptance.

## What validation does not prove

Automated validation does not prove:

- every page is visually perfect;
- every advanced Word feature is preserved exactly;
- every font is installed on every reader machine;
- screen-reader usability is fully accepted by humans;
- signed/notarized package distribution is complete;
- a synthetic stress run represents every multi-gigabyte real manuscript.

Those are separate acceptance gates documented in [Known Limitations](known-limitations.md) and [Release Process](release-process.md).
