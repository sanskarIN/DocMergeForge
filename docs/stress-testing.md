# Stress and Recovery Acceptance

DocMergeForge has two complementary stress paths: fast automated regression coverage and a manually scalable GitHub Actions workflow for larger synthetic manuscripts. Neither path should be described as multi-gigabyte acceptance unless the configured run actually produced and merged a multi-gigabyte source set successfully.

## Continuous regression coverage

The normal test suite and 120-Part Regression workflow cover deterministic numbered-part discovery and validation, transactional output recovery, source-integrity protection, and repeated cancellation cleanup.

`tests/regression/test_repeated_transaction_recovery.py` performs repeated cancelled publication transactions and then a successful recovery transaction. This detects stale staging directories and accidental replacement of the last published PDF/DOCX bundle.

`tests/unit/test_atomic.py` includes an injected `ENOSPC` failure and verifies that the previous published file is preserved and temporary `.part` files are removed.

## Generate a scalable fixture locally

Use the synthetic fixture generator when a larger source set is needed without storing huge binary fixtures in Git:

```bash
python scripts/generate_stress_fixture.py fixtures/stress \
  --parts 120 \
  --pdf-pages 5 \
  --pdf-lines-per-page 40 \
  --docx-paragraphs 50 \
  --paragraph-kib 1
```

The generator creates, for every part:

- one valid PDF with deterministic text markers;
- one valid DOCX with deterministic paragraph payloads;
- one companion ZIP that remains separate from the manuscript.

It prints the total generated source bytes at the end so an acceptance record can state the actual fixture size rather than an estimate.

## Manual GitHub Actions stress workflow

Run **Manual Stress Acceptance** from GitHub Actions and choose the scale with these inputs:

- `parts`: numbered PDF/DOCX part count;
- `pdf_pages`: PDF pages per part;
- `docx_paragraphs`: DOCX paragraphs per part;
- `paragraph_kib`: approximate deterministic payload KiB per DOCX paragraph.

The workflow then:

1. generates the fixture;
2. validates every expected part;
3. creates a project file;
4. runs merge preflight;
5. performs the merge;
6. compares merged PDF/DOCX evidence with the source set;
7. records output sizes; and
8. uploads the resulting publication bundle as a short-retention workflow artifact.

## Scaling guidance

Increase one dimension at a time. A useful progression is:

1. default 120-part run;
2. increased PDF page count;
3. increased DOCX paragraph count;
4. increased DOCX payload size;
5. combined high-load run sized to the target acceptance class.

Record the generated source bytes, output sizes, runner OS, workflow run ID, and result for every release-gate run.

## Remaining real-world acceptance

Synthetic stress coverage does not prove all real manuscript behavior. Before a stable release claim, perform separate acceptance with representative large books containing real styles, tables, images, sections, headers/footers, numbering, hyperlinks, fields, and other OOXML/PDF structures.

A real filesystem-exhaustion run and abrupt process-termination recovery run are also distinct from injected exceptions and graceful cancellation tests. Keep those release gates open until their evidence is recorded.
