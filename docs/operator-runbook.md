# Operator Runbook

This runbook is a practical procedure for running DocMergeForge on a real multi-part publication. It is written for the person responsible for producing and validating a master edition, not for code contributors.

## Golden rules

- Keep the original PDF/DOCX/source-code files unchanged and backed up.
- Validate exact numbered parts before merging.
- Review order explicitly.
- Keep PDF, DOCX, and companion code as separate content classes.
- Run preflight before publication.
- Do not bypass storage/writeability failures.
- Preserve transaction journals after an interrupted promotion.
- Keep manifests/checksums/reports with the released master files.
- Treat unsigned development packages as unsigned.

## Phase A — Prepare source material

1. Create a stable source directory.
2. Copy the final approved part files into it.
3. Remove obsolete drafts/duplicates from the scanned tree.
4. Use predictable part names.
5. Keep companion code archives intact.
6. Back up the complete source directory to a second location.

Recommended naming:

```text
Series - Part 001.pdf
Series - Part 001.docx
Series - Part 001 Code.zip
Series - Part 002.pdf
Series - Part 002.docx
Series - Part 002 Code.zip
```

## Phase B — Validate source completeness

```bash
docmergeforge validate --input "./Series" --parts 1-120
```

Stop if:

- any required part is missing;
- any part number is duplicated;
- expected numbers are detected incorrectly;
- encrypted PDFs are unexpected;
- important sources appear as `other`/ignored.

Fix source organization first, then rerun validation.

## Phase C — Create/save project

```bash
docmergeforge project-create \
  --input "./Series" \
  --output-dir "./Series-Master" \
  --project-file "./Series.json" \
  --name "Series Master Edition" \
  --parts 1-120
```

Or create it from the desktop application.

Save a copy of the project file with the release working records.

## Phase D — Dry-run/preflight

```bash
docmergeforge merge --project "./Series.json" --dry-run
```

Review all of the following:

- PDF count/readiness;
- DOCX count/readiness;
- missing parts;
- duplicates;
- companion count;
- ignored files;
- ordered PDF list;
- ordered DOCX list;
- expected output paths;
- DOCX conflict count;
- required/free storage;
- output directory correctness.

Stop if any value is surprising.

## Phase E — Review ordering

If using the GUI, open the order editor and review the complete sequence.

For a large book, spot-check:

- first 5 parts;
- around Part 9/10/11;
- around Part 99/100/101;
- final 5 parts;
- any manually renamed/special parts.

If selected/manual ordering is used, save the project after review.

## Phase F — Check DOCX fidelity risk

Before merging a complex Word manuscript, know whether it contains advanced features such as:

- complex fields;
- custom styles/numbering;
- multiple sections;
- headers/footers;
- equations;
- OLE/embedded objects;
- content controls;
- tracked changes;
- custom XML/external relationships.

Portable composition is the current production-supported mode but cannot guarantee perfect preservation of every advanced Word construct.

Keep originals and plan human comparison in the target office editor.

## Phase G — Execute publication

```bash
docmergeforge merge --project "./Series.json"
```

Or run the saved project in the desktop app.

Do not edit source files while the merge is running. Source-integrity validation is designed to catch changes, but operational discipline is still important.

Do not close/kill the application during final promotion unless testing recovery deliberately.

## Phase H — Confirm output bundle

After success, verify expected files exist, including as applicable:

```text
<basename>.pdf
<basename>.docx
Companion_Code_Index.md
Companion_Code_Index.json
<basename>_Merge_Report.md
<basename>_Merge_Report.html
<basename>_Merge_Manifest.json
<basename>_SHA256SUMS.txt
Publishing_Checklist.md
```

Keep the evidence files.

## Phase I — Automated post-checks

### Compare

```bash
docmergeforge compare \
  --input "./Series" \
  --pdf-output "./Series-Master/<basename>.pdf" \
  --docx-output "./Series-Master/<basename>.docx"
```

### Audit

```bash
docmergeforge audit --input "./Series-Master"
```

Interpret findings; do not mechanically delete/modify content solely to silence a generic audit warning.

## Phase J — Human PDF QA

Open the final PDF in an independent viewer and inspect:

- first page/front matter;
- title/author/edition metadata;
- bookmarks;
- TOC;
- page numbering;
- headers/footers/watermark;
- part boundaries;
- images/tables;
- mixed orientations/page sizes;
- final page;
- random sample pages throughout the book.

For high-value publications, compare expected per-part page ranges with source PDFs.

## Phase K — Human DOCX QA

Open the final DOCX in the intended editor.

Inspect:

- document opens without repair prompt;
- heading hierarchy;
- generated part headings;
- TOC field/update behavior;
- page breaks/sections;
- styles;
- numbered/bulleted lists;
- tables;
- images;
- headers/footers;
- page numbering;
- equations/fields/advanced content;
- last part/end matter.

If Word/LibreOffice reports repair or fidelity loss, stop publication and investigate from the original parts.

## Phase L — Archive release evidence

Preserve:

- project file;
- final PDF/DOCX;
- merge manifest;
- checksum file;
- reports;
- companion index;
- publishing checklist;
- application version/commit;
- human QA notes;
- release artifact hashes.

Use read-only/immutable storage for final release records where practical.

## Incident — merge cancelled normally

If the app reports safe cancellation:

1. confirm no final bundle was partially updated;
2. review cancellation reason;
3. rerun preflight;
4. restart publication when ready.

Ordinary pre-journal staging should be cleaned by normal context cleanup.

## Incident — process/machine crashed

If publication may have been interrupted during final promotion:

1. stop new merges into that output folder;
2. reveal/check hidden `.docmergeforge-staging-*` directories;
3. **do not delete them**;
4. back up the affected output folder;
5. run:

```bash
docmergeforge recover-output --output-dir "./Series-Master"
```

6. inspect restored/removed paths;
7. rerun preflight and a fresh publication.

See [Publication Recovery](recovery.md).

## Incident — recovery refuses to proceed

If recovery reports a conflict/fingerprint mismatch:

- do not force-delete the journal;
- copy all recovery evidence;
- identify who/what modified the final path after interruption;
- compare sizes/hashes/backups;
- restore manually only after identifying the authoritative version;
- document the incident.

## Incident — output folder not writable

If preflight raises an output-access error:

- confirm path exists/is intended;
- check filesystem permissions;
- check read-only/removable/network mount status;
- choose another output directory if necessary;
- do not run as Administrator/root merely to bypass an unexplained failure.

## Incident — insufficient storage

If storage preflight fails:

- free space on the output filesystem;
- move output to a larger local filesystem;
- remember overwrite transactions may need temporary backup space;
- avoid filling the disk to the exact estimate threshold;
- rerun dry-run afterward.

## Incident — missing/duplicate part

Do not use overwrite/sorting options to hide a numbered validation problem.

For duplicates:

1. identify authoritative file;
2. move obsolete duplicate outside scanned roots;
3. validate again.

For missing parts:

1. locate/restore the missing source;
2. verify its filename/part detection;
3. validate again.

## Incident — encrypted PDF password rejected

- confirm password with a trusted PDF viewer;
- ensure the correct file/version is being opened;
- retry interactive password entry;
- Ctrl+C cancels if the password is unavailable;
- never put the password in a project JSON or support issue.

## Incident — `.doc` file detected

DocMergeForge does not silently convert legacy `.doc`.

- preserve original `.doc`;
- convert to a separate `.docx` using a trusted office suite;
- inspect conversion fidelity;
- use the new `.docx` in the project.

## SQL Full Mastery runbook

For the 120-part preset:

```bash
docmergeforge sql-preset \
  --input "./SQL-Full-Mastery" \
  --output-dir "./SQL-Full-Mastery-Master-Edition" \
  --dry-run
```

Both PDF and DOCX sets must be ready for Parts 1–120.

Then:

```bash
docmergeforge sql-preset \
  --input "./SQL-Full-Mastery" \
  --output-dir "./SQL-Full-Mastery-Master-Edition"
```

Expected primary filenames are documented in [SQL Full Mastery Preset](sql-full-mastery-preset.md).

## Final release sign-off checklist

- [ ] Source backup exists.
- [ ] Part validation green.
- [ ] Order reviewed.
- [ ] Dry-run/preflight green.
- [ ] Storage/writeability green.
- [ ] DOCX risk reviewed.
- [ ] Merge succeeded.
- [ ] No pending transaction journal remains.
- [ ] Manifest/checksums/reports preserved.
- [ ] Compare reviewed.
- [ ] Audit reviewed.
- [ ] PDF human QA passed.
- [ ] DOCX human QA passed.
- [ ] Companion index/code package verified.
- [ ] Distributed file hashes verified.
- [ ] Packaged app signing/notarization status represented accurately.
