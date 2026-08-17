# Output Artifacts

A DocMergeForge project publication is more than a single merged file. A successful full project can produce manuscript outputs plus validation/reproducibility evidence. These files are staged together and promoted as one publication bundle.

## Generic project outputs

For a generic project, the configured filename template is rendered into a project basename. If PDF inputs exist, the project can produce:

```text
<basename>.pdf
```

If DOCX inputs exist:

```text
<basename>.docx
```

Only document kinds discovered for the project are emitted.

## Generic evidence files

A generic full project run currently stages evidence such as:

```text
Companion_Code_Index.md
Companion_Code_Index.json
<basename>_Merge_Report.md
<basename>_Merge_Report.html
<basename>_Merge_Manifest.json
<basename>_SHA256SUMS.txt        # when checksum generation is enabled
Publishing_Checklist.md
```

These files are part of the same transaction boundary as the merged manuscripts.

## SQL Full Mastery preset outputs

The SQL preset uses fixed master-edition names.

Primary outputs:

```text
SQL_Full_Mastery_Complete_120_Part_Master_Edition.pdf
SQL_Full_Mastery_Complete_120_Part_Master_Edition.docx
```

Preset evidence names include:

```text
SQL_Full_Mastery_120_Part_Merge_Manifest.json
SQL_Full_Mastery_120_Part_Merge_Report.html
SQL_Full_Mastery_120_Part_Merge_Report.md
SQL_Full_Mastery_120_Part_SHA256SUMS.txt
```

The preset also produces companion/publishing evidence through the project reporting layer.

## Merged PDF

The PDF artifact is the ordered merged PDF manuscript with configured publication enhancements such as metadata, bookmarks, title page, TOC/page overlays, headers/footers/watermark, and numbering where enabled.

The PDF engine validates the result by reopening it and checking expected page evidence before the file is accepted as a staged output.

## Merged DOCX

The DOCX artifact is the portable OOXML-composed master manuscript using the configured DOCX policies.

The DOCX engine validates ZIP/XML/package structure and reopens the generated document before it is accepted.

DOCX fidelity should still receive human review in Microsoft Word/LibreOffice or the intended publication editor, especially for advanced OOXML constructs.

## Merge report (`.md` and `.html`)

The project report records human-readable validation/publication evidence. It is useful for:

- reviewing which manuscript kinds were validated;
- noting skipped kinds;
- documenting companion-package counts;
- keeping a portable release record in Markdown/HTML form.

The SQL preset uses preset-specific report filenames.

## Merge manifest (`.json`)

The manifest is the machine-readable publication record. The current manifest model includes concepts such as:

- application version;
- timestamp;
- operating system;
- profile;
- ordered source evidence;
- output evidence;
- ignored files;
- warnings.

For reproducible publication workflows, preserve the manifest alongside the released manuscripts.

## SHA-256 checksums

When checksum generation is enabled, DocMergeForge writes a checksum file covering relevant source/companion/output evidence.

SHA-256 helps answer questions such as:

- Did this file change after publication?
- Is this the same master file that was reviewed?
- Did a source/companion archive change between runs?

A checksum proves byte identity, not semantic correctness.

## Companion code index

Companion/source archives are deliberately not merged into PDF/DOCX manuscripts.

The companion index records references to independent companion artifacts so a publication can ship manuscript and code evidence together without corrupting format boundaries.

Current companion references include:

- detected part number when available;
- path;
- SHA-256;
- byte size.

## Publishing checklist

`Publishing_Checklist.md` provides a final human checklist tied to the expected part range. It is intended to remind the operator that successful automated merging is only one stage of publication acceptance.

## Output artifact model

Internally, a staged merged artifact records:

- final path;
- SHA-256 of the staged file;
- byte size;
- document kind;
- validation-passed state.

This evidence is generated from the staged file before final promotion.

## Transaction staging

During a project run, the application creates a hidden transaction folder in the output directory using a prefix like:

```text
.docmergeforge-staging-...
```

The final manuscript/report filenames are not immediately replaced. Instead:

1. each output is assigned a staging path;
2. merge/report generators write to staging paths;
3. staged files are validated/fingerprinted;
4. a promotion journal is written;
5. existing outputs may be moved to rollback backup paths;
6. staged outputs are promoted to their final names;
7. the journal is marked committed;
8. stale backups/staging data are removed after success.

This protects the publication bundle from partial updates.

## Overwrite versus versioned outputs

For document outputs, project `overwrite` controls whether an existing requested final path can be replaced.

When overwrite is disabled, output naming can select a versioned path rather than replacing an existing file.

Evidence/report paths in the full project transaction are intentionally staged with overwrite behavior so a new coherent report bundle replaces the old evidence only at the same final transaction boundary.

## Interrupted promotion artifacts

If a process terminates after the promotion journal is written, the staging directory can contain the only rollback copy of a previously published output.

Do not treat hidden transaction directories as disposable temp files after a crash.

Run:

```bash
docmergeforge recover-output --output-dir "./Master"
```

See [Publication Recovery](recovery.md).

## What to archive for a release

Recommended release archive contents:

- final PDF;
- final DOCX;
- merge manifest;
- SHA-256 checksum file;
- Markdown/HTML merge reports;
- companion-code index;
- publishing checklist;
- project file (if it does not expose sensitive/local-only paths);
- release notes/changelog;
- independent human QA notes when applicable.

Do not include encrypted-PDF passwords or sensitive diagnostic data.

## Verify artifacts after copying

If final outputs are copied to another disk/cloud/release system, use checksums to verify byte identity after transfer. A valid source-side checksum is most useful when it is stored separately from or alongside the transferred artifact and rechecked at the destination.

## Publication evidence is not signing

Checksums and manifests do not replace platform code signing, installer signing, or macOS notarization. Desktop-package authenticity is a separate release process documented in [Release Packaging](release-packaging.md) and [Release Process](release-process.md).
