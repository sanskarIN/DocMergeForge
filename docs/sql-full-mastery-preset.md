# SQL Full Mastery — 120-Part Preset

DocMergeForge includes a dedicated guided project definition for assembling the **SQL Full Mastery — Complete 120-Part Master Edition**. The preset enforces Parts 1–120, generates both master manuscript formats, applies publication defaults, and creates reproducibility/publication evidence while keeping companion code independent.

## Preset identity

Internal project name:

```text
SQL Full Mastery — 120-Part Master Edition
```

Expected inclusive range:

```text
1-120
```

Both the PDF and DOCX sets are mandatory for the full preset readiness path.

## Create/run directly

### Dry run first

```bash
docmergeforge sql-preset \
  --input "./SQL-Full-Mastery" \
  --output-dir "./SQL-Full-Mastery-Master-Edition" \
  --dry-run
```

The dry run prints JSON preflight evidence and exits successfully only when both expected manuscript sets are ready.

### Full publication

```bash
docmergeforge sql-preset \
  --input "./SQL-Full-Mastery" \
  --output-dir "./SQL-Full-Mastery-Master-Edition"
```

## Create a reusable preset project file

```bash
docmergeforge project-create \
  --input "./SQL-Full-Mastery" \
  --output-dir "./SQL-Full-Mastery-Master-Edition" \
  --project-file "./SQL-Full-Mastery.json" \
  --sql-preset
```

Then:

```bash
docmergeforge merge --project "./SQL-Full-Mastery.json" --dry-run
docmergeforge merge --project "./SQL-Full-Mastery.json"
```

Because the saved project's name matches the preset identity, the CLI applies strict PDF-and-DOCX preset readiness behavior.

## Required source organization

The source folder can contain PDF, DOCX, companion archives, and other files, but validation requires one unambiguous numbered PDF and DOCX part for each expected number 1–120.

Recommended layout:

```text
SQL-Full-Mastery/
  SQL Full Mastery - Part 001.pdf
  SQL Full Mastery - Part 001.docx
  SQL Full Mastery - Part 001 Code.zip
  SQL Full Mastery - Part 002.pdf
  SQL Full Mastery - Part 002.docx
  SQL Full Mastery - Part 002 Code.zip
  ...
  SQL Full Mastery - Part 120.pdf
  SQL Full Mastery - Part 120.docx
  SQL Full Mastery - Part 120 Code.zip
```

Companion archive per part is optional from the merge engine's perspective; PDF/DOCX completeness is the preset's manuscript requirement.

## Primary output filenames

PDF:

```text
SQL_Full_Mastery_Complete_120_Part_Master_Edition.pdf
```

DOCX:

```text
SQL_Full_Mastery_Complete_120_Part_Master_Edition.docx
```

## Preset evidence filenames

Manifest:

```text
SQL_Full_Mastery_120_Part_Merge_Manifest.json
```

HTML report:

```text
SQL_Full_Mastery_120_Part_Merge_Report.html
```

Markdown report:

```text
SQL_Full_Mastery_120_Part_Merge_Report.md
```

Checksums:

```text
SQL_Full_Mastery_120_Part_SHA256SUMS.txt
```

The project reporting layer also produces companion-code index and publishing-checklist evidence.

## PDF preset defaults

The preset currently configures:

```text
add_part_bookmarks = true
title = SQL Full Mastery — Complete 120-Part Master Edition
author = Ram Sandesh
edition = August 2026
include_title_page = true
visible_toc = true
page_numbers = true
footer_text = SQL Full Mastery • Ram Sandesh
optimization = balanced
```

Other PDF settings use model defaults unless explicitly set.

These publication defaults intentionally add/modify master-book structure compared with simply concatenating pages.

## DOCX preset defaults

The preset currently configures:

```text
start_each_part_on_new_page = true
preserve_sections = true
fidelity_mode = portable
add_part_headings = true
create_toc_field = true
style_conflict_policy = prefer_master
numbering_conflict_policy = remap
footer_text = SQL Full Mastery • Ram Sandesh
continuous_page_numbering = true
```

Portable mode is the current production-supported DOCX path; high-fidelity external office-suite adapters are not silently substituted.

## Dry-run evidence to review

Before starting the preset, confirm:

- `pdf_count` is correct;
- `pdf_ready` is true;
- `pdf_missing` is empty;
- `pdf_duplicates` is empty;
- `docx_count` is correct;
- `docx_ready` is true;
- `docx_missing` is empty;
- `docx_duplicates` is empty;
- companion count is expected;
- ignored-file count is understood;
- storage `sufficient` is true;
- `ordered_pdf` begins at Part 1 and ends at Part 120;
- `ordered_docx` begins at Part 1 and ends at Part 120;
- expected outputs point to the intended master-edition folder;
- DOCX conflict count has been reviewed.

## Companion code behavior

Recognized code/project archives are:

- excluded from PDF/DOCX merge inputs;
- SHA-256 hashed;
- tracked for changes during the run;
- recorded in companion indexes.

They are never automatically:

- extracted;
- combined;
- rewritten;
- refactored;
- compiled.

This is especially important for a 120-part educational series where each part may have independent example/project code.

## Transactional publication

The preset stages the primary manuscripts and evidence before one final promotion boundary.

This means a new preset PDF should not be published alone if:

- DOCX merge later fails;
- report/manifest generation fails;
- source integrity changes;
- cancellation occurs before promotion.

Overwrite publication uses transaction backups/recovery journal behavior just like generic projects.

## Encrypted PDFs

If one or more preset PDF parts are encrypted, the CLI project path prompts locally for passwords before readiness/merge.

The preset does not bypass PDF encryption and does not persist passwords.

For a 120-part series, ensure all required passwords are available before beginning a long run.

## Validation and source integrity

Before merging, both manuscript sets are validated against Parts 1–120.

Tracked PDF/DOCX/companion hashes are captured before merge and checked again before final publication. If any tracked file changes during the run, the publication fails instead of silently mixing source versions.

## 120-part regression fixture

The repository includes a synthetic generated fixture used by automated regression CI:

```bash
python scripts/generate_120_fixture.py fixtures/generated/sql-120
```

Validate it:

```bash
docmergeforge validate --input fixtures/generated/sql-120 --parts 1-120
```

The 120-Part Regression workflow also runs integration/regression tests against this generated structure.

This is important regression evidence but not a substitute for real large-manuscript fidelity/stress acceptance.

## Post-publication checks

After success:

### Compare

```bash
docmergeforge compare \
  --input "./SQL-Full-Mastery" \
  --pdf-output "./SQL-Full-Mastery-Master-Edition/SQL_Full_Mastery_Complete_120_Part_Master_Edition.pdf" \
  --docx-output "./SQL-Full-Mastery-Master-Edition/SQL_Full_Mastery_Complete_120_Part_Master_Edition.docx"
```

### Audit

```bash
docmergeforge audit --input "./SQL-Full-Mastery-Master-Edition"
```

The audit includes a targeted check for stale `Next: Part 121` text, which is especially relevant to the final part of a 120-part series.

## Human PDF review

Check:

- title page;
- visible TOC;
- Part 1/10/100/120 boundaries;
- bookmark sequence;
- page numbering;
- footer;
- metadata;
- random pages throughout;
- final page.

Because preset front matter adds pages, interpret raw source-page comparisons with that intentional structure in mind.

## Human DOCX review

Open in the target office editor and check:

- no repair prompt;
- TOC field/update;
- generated part headings;
- start-on-new-page behavior;
- styles/numbering;
- sections;
- footer/page numbering;
- tables/images/code blocks/examples;
- Part 1/10/100/120;
- final content has no stale continuation reference.

## Interrupted publication

If a process interruption leaves a hidden transaction journal:

```bash
docmergeforge recover-output \
  --output-dir "./SQL-Full-Mastery-Master-Edition"
```

Do not delete transaction staging manually before recovery.

## Final SQL preset checklist

- [ ] Exactly Parts 1–120 PDFs discovered.
- [ ] Exactly Parts 1–120 DOCX discovered.
- [ ] No duplicate numbers.
- [ ] Order reviewed.
- [ ] Companion archives classified separately.
- [ ] Dry run green.
- [ ] Storage/writeability green.
- [ ] DOCX conflict count reviewed.
- [ ] Preset publication completes.
- [ ] No pending transaction journal.
- [ ] Manifest/report/checksum/index/checklist preserved.
- [ ] PDF human QA complete.
- [ ] DOCX human QA complete.
- [ ] `audit` reviewed for stale Part 121/contact issues.
- [ ] Release hashes archived.
