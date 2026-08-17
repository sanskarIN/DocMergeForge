# PDF Engine

DocMergeForge's PDF engine uses `pypdf` to assemble ordered source pages without rasterizing them, apply optional publication enhancements, validate the temporary result, verify source integrity, and only then allow atomic/final project publication.

## Responsibilities

The PDF engine is responsible for:

- deterministic input order;
- encrypted-PDF password enforcement;
- optional generated front matter;
- source page appending;
- part bookmarks;
- page overlays such as numbers/header/footer/watermark;
- selected content-stream compression;
- metadata;
- cancellation checks through finalization;
- output reopen/page-count validation;
- source hash revalidation;
- atomic single-output write behavior.

A full project wraps this engine inside the broader multi-output `OutputTransaction`.

## Input order

Unless `preserve_order=True`, inputs are sorted by:

1. whether a part number was detected;
2. detected numeric part number;
3. case-insensitive filename.

Files with detected part numbers therefore precede unnumbered files.

When a project has explicit `selected_files`, the application service requests order preservation so the reviewed project sequence is not replaced by automatic sorting.

## No input PDFs

An empty input list raises a validation error. The engine never creates an empty “successful” PDF.

## Source integrity snapshot

Before reading pages, the engine snapshots SHA-256 evidence for every ordered source PDF.

After generating/reopening the temporary output, it verifies that source hashes remain unchanged. A changed source causes `ValidationError` before the temporary file is promoted.

Full project publication performs an additional broader source/companion integrity check at the application-service level.

## Atomic output path

For a direct engine call:

- if overwrite is disabled, a versioned output path is selected when needed;
- the actual PDF is written to a temporary atomic-output path;
- the temporary file is validated;
- only successful completion promotes it to the final output path.

For a full project run, the engine's requested output path is already a project transaction staging path, providing a second outer publication boundary across PDF, DOCX, and evidence files.

## Generated front matter

Before source pages, the engine calls the PDF rendering layer to generate configured front matter.

`PdfSettings` currently contains:

```text
add_part_bookmarks
title
author
edition
include_title_page
visible_toc
page_numbers
page_number_start
header_text
footer_text
watermark_text
optimization
```

`render_front_matter()` can use these settings to create publication pages such as a title page/visible TOC where enabled.

The generated front-matter page count is included in the expected output page total.

## Source page composition

Each source is opened using:

```python
PdfReader(..., strict=False)
```

Pages are appended as PDF page objects. They are not converted to images merely for merging, so page geometry/rotation/content streams are retained according to `pypdf` semantics.

## Encrypted PDFs

If a source reader is encrypted, the engine requires a `password_provider`.

Failure cases include:

- no password provider;
- provider returns no password;
- decrypt operation raises;
- decrypt result indicates an incorrect password.

DocMergeForge does not attempt to bypass encryption.

The CLI/desktop layers collect passwords locally and keep them in memory for the active operation. The engine receives only the password it needs through a callback.

## Part bookmarks

When `add_part_bookmarks` is true, each input gets a top-level outline item at the page where that part begins.

Bookmark text combines:

```text
Part label — detected title/filename stem
```

The bookmark start index is calculated after any generated front matter already added to the writer.

## Progress reporting

After each input PDF is appended, an optional progress callback receives:

```text
current index
total input count
source path
```

The application service maps this to the `merging-pdf` stage for desktop progress reporting.

## Cancellation

The engine checks cancellation:

- before writer setup;
- while adding generated front matter;
- before each source;
- while appending source pages;
- while finalizing every output page/overlay;
- before writing;
- after writing/before validation.

A cancellation raises `MergeCancelled("PDF merge cancelled safely.")`.

The goal is to avoid a long finalization loop ignoring a user's cancellation request and to ensure the outer project transaction never promotes a cancelled bundle.

## Overlays

For every output page, the engine asks the rendering layer to create an overlay using the page's actual media-box width/height and current output page index.

Depending on settings, this can implement publication elements such as:

- page numbers;
- header text;
- footer text;
- watermark text.

If no overlay is needed, the page is left without an overlay merge.

## Optimization modes

When `optimization` is:

```text
balanced
archive
```

the engine calls `compress_content_streams()` on each output page.

`preserve` avoids that extra compression step.

Optimization affects content stream representation/size and should be included in fidelity/size acceptance for the intended publication.

## Metadata

The engine maps configured settings to PDF metadata:

- `title` -> `/Title`;
- `author` -> `/Author`;
- `edition` -> `/Subject` as `Edition: ...`.

It also writes:

```text
/Creator = DocMergeForge — Made by the Sanskar
```

Metadata should be reviewed for publication/privacy correctness before release.

## Output validation

After writing the temporary PDF, the engine reopens it with `PdfReader(strict=False)` and verifies:

```text
actual pages == expected pages
```

Expected pages are:

```text
generated front-matter pages + every appended source page
```

A mismatch raises `ValidationError` and prevents promotion.

## Standalone `validate_output`

The engine exposes validation returning evidence:

```text
path
pages
sha256
size
```

It also rejects an unexpectedly encrypted output and can enforce a caller-provided expected page count.

## Direct CLI PDF merge

```bash
docmergeforge pdf \
  --input "./Book" \
  --parts 1-120 \
  --output "./Master/Book.pdf"
```

The CLI validates the numbered set before invoking the engine.

Direct merge is useful for a simple one-format workflow; it does not generate the complete project report/manifest/checksum bundle.

## Project PDF merge

A full project run:

1. validates the PDF set;
2. snapshots all tracked PDF/DOCX/companion sources;
3. checks storage/writeability;
4. creates an outer transaction staging path;
5. invokes the PDF engine with `overwrite=True` on that staging path;
6. later stages DOCX/report/evidence output;
7. revalidates sources;
8. promotes the entire project bundle together.

This prevents a successful PDF from being published alone when a later DOCX/report stage fails.

## PDF comparison

After publication:

```bash
docmergeforge compare --input "./Book" --pdf-output "./Master/Book.pdf"
```

The comparison reports source/output page counts and per-part page ranges. Interpret it alongside intentionally generated front matter/other page-adding features.

## PDF audit

```bash
docmergeforge audit --input "./Book"
```

Unencrypted PDFs are text-extracted page-by-page for targeted publication audit patterns. Encrypted PDFs produce a warning in the current audit path because audit does not request passwords.

## Fidelity notes

Because source pages are appended rather than rasterized, the engine avoids a major class of quality loss. However, final human PDF acceptance is still required for:

- viewer compatibility;
- fonts/transparency;
- mixed page sizes/rotations;
- generated overlays;
- front matter/TOC/bookmarks;
- metadata;
- compression effects;
- unusual annotations/forms/interactive content.

## Safety checklist for PDF changes

Any engine change should preserve tests for:

- natural/manual input order;
- empty-input rejection;
- encrypted password success/failure/cancellation;
- page-count validation;
- generated front matter;
- bookmarks;
- overlays;
- metadata;
- optimization modes;
- progress/cancellation during finalization;
- source-integrity violation;
- atomic failure cleanup;
- full-project transaction behavior.
