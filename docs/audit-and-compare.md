# Audit and Compare

DocMergeForge provides two post-discovery/publication inspection tools with different purposes:

- `audit` searches manuscript text for selected publication-quality findings.
- `compare` measures merged-output evidence against source evidence.

Neither tool rewrites the original manuscripts.

## Audit command

```bash
docmergeforge audit --input PATH
```

Example:

```bash
docmergeforge audit --input "./Book"
```

The input may be a single supported file or a directory tree. Directory scanning is recursive and currently audits `.pdf` and `.docx` files.

Output is JSON:

```json
[
  {
    "code": "stale-next-part",
    "message": "Found a stale 'Next: Part 121' reference.",
    "path": "Book/Part 120.docx",
    "severity": "WARNING"
  }
]
```

## DOCX audit extraction

For DOCX files, the auditor opens the OOXML ZIP package directly, reads `word/document.xml`, extracts Word text nodes, and joins their text for pattern analysis.

This is intentionally a text audit, not a full rendering engine. Text in unsupported/other OOXML parts may not be represented in the same way as visible Word rendering.

## PDF audit extraction

For unencrypted PDFs, `pypdf` extracts text from each page. Findings are deduplicated by finding code/message/path before being returned.

For encrypted PDFs, the current audit command does not request a password. It returns an `encrypted-pdf` warning indicating that content was not audited.

## Current audit patterns

The current publication audit includes targeted checks such as:

### Stale next-part reference

Detects text matching a stale reference to:

```text
Next: Part 121
```

Finding code:

```text
stale-next-part
```

### Multiple GitHub profile URLs

The audit detects GitHub profile-style URLs in extracted text. If more than one distinct GitHub URL is found in the same audited document, it reports:

```text
github-inconsistent
```

This is intended to flag potentially inconsistent author/repository branding for review.

### Many email variants

If more than three distinct email addresses are detected in a document, it reports:

```text
email-review
```

This is a review signal, not a proof that any address is wrong.

## Audit limitations

The audit is deliberately narrow. It does not currently replace:

- grammar/spelling review;
- plagiarism checks;
- copyright/legal review;
- accessibility tagging inspection;
- rendered page-layout QA;
- malware scanning;
- source-code security scanning;
- full metadata consistency review;
- comprehensive link checking.

Treat zero audit findings as “none of the implemented patterns triggered,” not “publication is perfect.”

## Compare command

```bash
docmergeforge compare \
  --input PATH \
  [--pdf-output FILE.pdf] \
  [--docx-output FILE.docx]
```

At least one output option is required.

Example:

```bash
docmergeforge compare \
  --input "./Book" \
  --pdf-output "./Master/Book.pdf" \
  --docx-output "./Master/Book.docx"
```

## PDF comparison

PDF comparison calculates:

- total source pages;
- output pages;
- whether the counts match;
- expected per-part page ranges.

Source inputs are ordered by detected part number for this comparison.

If a source `InputDocument` already has a page count from discovery, that count is reused. Otherwise the source PDF is reopened to count pages.

Example output concept:

```json
{
  "pdf": {
    "source_pages": 240,
    "output_pages": 240,
    "page_count_matches": true,
    "part_page_ranges": {
      "1": [1, 2],
      "2": [3, 4]
    }
  }
}
```

### Important PDF caveat

Project PDF settings can add generated front matter such as a title page/visible TOC or other page-affecting features. A raw source-page comparison may therefore need interpretation when publication features intentionally add pages.

Use the merge engine's own validation plus human publication review as the authoritative acceptance process for enhanced PDFs.

## DOCX comparison

DOCX comparison opens each source and the output through `python-docx` and counts:

- paragraphs;
- tables;
- inline shapes;
- sections;
- headings whose style name starts with `Heading`.

Source counts are summed, then reported beside output counts.

Example shape:

```json
{
  "docx": {
    "sources": {
      "paragraphs": 1000,
      "tables": 50,
      "inline_shapes": 30,
      "sections": 120,
      "headings": 300
    },
    "output": {
      "paragraphs": 1120,
      "tables": 50,
      "inline_shapes": 30,
      "sections": 120,
      "headings": 420
    }
  }
}
```

Counts do not necessarily need to be identical. DocMergeForge can intentionally add part headings, TOC fields, page breaks/sections, headers/footers, or other publication structure.

The comparison is evidence for review, not a pass/fail semantic equivalence theorem.

## From review findings to project selection changes

`audit` and `compare` remain report-only tools. They do not automatically rewrite a project based on a finding or count difference, because those results do not provide enough information to prove that a source should be added, removed, or reordered.

When your review process leads you to add/remove numbered source files on disk and you want to refresh a reusable project's explicit automatic selection, use the separate preview-first synchronization command:

```bash
docmergeforge project-sync --project "./Book.json"
```

Review the complete `current`, `proposed`, `added`, `removed`, and `reordered` evidence. Apply an addition/reorder-only proposal with:

```bash
docmergeforge project-sync --project "./Book.json" --apply
```

If the proposal removes any existing selected path, apply is blocked until those removals receive the separate `--allow-removals` approval. This protects intentionally selected unnumbered front/back matter and other manual exceptions.

`project-sync` does **not** consume audit findings or compare results as mutation instructions. It independently rebuilds a deterministic numbered/in-range PDF/DOCX selection from the project's source folders. See [Project Synchronization](project-sync.md) for the full safety model.

After any applied selection change, run:

```bash
docmergeforge merge --project "./Book.json" --dry-run
```

and review resolved inputs/diagnostics before creating a new publication.

## Recommended post-publication workflow

For a high-value publication:

1. Run the full project merge and keep generated manifest/checksums/report.
2. Run `compare` for each produced format.
3. Review page/count differences against configured publication features.
4. Run `audit` on sources and/or final outputs as appropriate.
5. If source membership/order changed during review, preview `project-sync` and explicitly approve only the intended metadata changes.
6. Re-run project dry-run/preflight after any applied synchronization.
7. Open the PDF in at least one independent PDF reader.
8. Open the DOCX in the intended target editor (for example Microsoft Word or LibreOffice).
9. Check front matter, TOC, headings, page numbering, tables, images, footnotes/endnotes, headers/footers, and complex fields manually.
10. Record human QA evidence with release records.

## CI use

`compare` and audit primitives are suitable for regression fixtures where expected results are known. Avoid turning every count difference into a universal failure rule without considering intentional publication-generated structure.

`project-sync` can be parsed in automation for drift reporting, but do not mechanically add `--apply --allow-removals` to unattended CI. Removal approval exists to force review of project metadata changes that can alter publication membership.

## Privacy

Audit and comparison run locally. Audit output can expose detected email addresses, GitHub URLs, and file paths, so review exported logs/results before sharing them publicly.

Project-sync preview output likewise contains local source/project paths and should be treated as potentially sensitive metadata when archived or shared.
