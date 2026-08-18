# Microsoft Word Native Merge Acceptance

DocMergeForge includes an explicit Microsoft Word multi-document merge prototype for acceptance work on controlled Windows machines. It is **not** connected to the normal production DOCX merge engine and it does not make the `word` fidelity mode production-ready.

The purpose of this subsystem is to make Word-native merge behavior measurable before any production capability claim is considered.

## Current status

Current implementation state:

```text
round-trip Word adapter: implemented
native Word merge prototype: implemented
measured native-merge evidence: implemented
production Word merge mode: disabled
controlled real-Word acceptance: still required
representative corpus acceptance: still required
manual rendering review: still required
```

The normal `docmergeforge docx` workflow continues to use the portable production-supported OOXML engine.

## Native merge prototype

Implementation:

```text
src/docmergeforge/docx/word_merge.py
```

The prototype accepts an ordered DOCX source sequence and a separate non-existing destination.

Before Word is started, it:

1. requires at least one source;
2. requires `.docx` sources and destination;
3. requires every source to exist;
4. rejects a source path that resolves to the destination;
5. rejects duplicate resolved source paths;
6. validates every source as a non-empty OOXML DOCX package;
7. records source SHA-256 hashes;
8. refuses to overwrite an existing destination.

## Word automation behavior

The prototype writes an ordered JSON manifest into a temporary local working directory and invokes Windows PowerShell without a shell command string.

The PowerShell automation:

- creates `Word.Application` through COM;
- keeps Word invisible;
- disables interactive alerts;
- force-disables automation macros for the session;
- opens the first source read-only and saves it as a separate DOCX working copy;
- opens that working copy for modification;
- inserts a Word section boundary before every later source;
- uses `Range.InsertFile(...)` to insert each later source in manifest order;
- saves and closes the merged copy;
- closes/releases Word COM objects in `finally`;
- requests garbage collection/finalizer completion after COM release.

The first source is never edited in place.

## Section boundary strategy

A plain page break is not used as the document boundary.

When `start_each_on_new_page=true`, the automation uses:

```text
wdSectionBreakNextPage = 2
```

When `start_each_on_new_page=false`, it uses:

```text
wdSectionBreakContinuous = 3
```

A section boundary gives Microsoft Word a place to preserve or resolve section-specific properties such as page orientation, margins, headers, footers, and page-numbering behavior.

This choice improves the merge boundary but does not prove that every source section property is preserved correctly. Actual Word acceptance remains required.

## Temporary output and source preservation

The native merge writes to a temporary destination beside the requested output.

After the Word process returns, DocMergeForge:

1. requires the temporary output to exist and be non-empty;
2. validates the temporary output as DOCX/OOXML;
3. verifies every source SHA-256 is unchanged;
4. promotes the validated temporary document to the requested destination;
5. validates the final destination again;
6. verifies every source SHA-256 again.

A process exit code of zero is not sufficient acceptance by itself.

## Measured multi-document acceptance

Implementation:

```text
src/docmergeforge/docx/word_merge_acceptance.py
```

The acceptance layer calculates expected evidence from the ordered source set before invoking the native Word merge prototype.

### Structural evidence

The expected/output structural snapshot includes:

- non-empty body paragraph count;
- body table count;
- inline-shape count;
- heading count;
- section count;
- non-empty header paragraph count;
- non-empty footer paragraph count;
- header table count;
- footer table count.

The expected snapshot is the aggregate of the ordered source documents.

### Visible-text evidence

The acceptance layer also calculates privacy-safe SHA-256 fingerprints for ordered visible text from:

- non-empty body paragraphs;
- body table cells;
- header paragraphs/table cells;
- footer paragraphs/table cells.

The plain manuscript text is not serialized into acceptance JSON.

Length-delimited UTF-8 text records are hashed so different text sequences cannot be confused merely by concatenation boundaries.

### Risk evidence

The acceptance layer records:

- the union of risky OOXML categories detected across all sources;
- risky categories detected in the output;
- newly introduced output risk categories.

### Acceptance rule

`accepted=true` currently requires:

1. expected and output measured structural snapshots match;
2. expected and output visible-text fingerprints match; and
3. the output introduces no new risky-construct category.

This is deliberately strict and deliberately incomplete as a universal fidelity proof.

## Acceptance command

Run the prototype on a Windows machine with Microsoft Word installed:

```powershell
python scripts/check_word_native_merge_acceptance.py `
  --input ".\private-corpus\Part 1.docx" `
  --input ".\private-corpus\Part 2.docx" `
  --output ".\private-word-evidence\merged.docx" `
  --evidence ".\private-word-evidence\word-merge-evidence.json"
```

Repeat `--input` in the exact merge order.

Optional controls:

```text
--timeout SECONDS
--start-each-on-new-page
--no-start-each-on-new-page
```

Default timeout is `900` seconds.

The command refuses to overwrite an existing evidence JSON file. The native merge layer separately refuses to overwrite an existing output DOCX.

Exit behavior:

- `0` — measured merge acceptance passed;
- `2` — a valid output was produced but measured acceptance failed;
- non-zero/error — the native automation, validation, input, source-integrity, or output boundary failed.

## What a passing result means

A pass means the selected source set survived the **currently measured** structural, visible-text, and risky-construct checks through the Word-native merge prototype.

It does not prove:

- identical pagination;
- identical line wrapping;
- identical font substitution behavior;
- identical floating-object coordinates;
- chart/SmartArt visual identity;
- field/TOC recalculation correctness;
- comment/tracked-change display equivalence;
- content-control behavior;
- embedded-object behavior;
- custom XML semantics;
- perfect section/header/footer linkage behavior;
- universal behavior across Word versions/builds;
- clean packaged-app integration;
- safe cancellation of every Word COM state.

Manual review in the exact Word version being claimed remains mandatory.

## Controlled Windows acceptance record

For each serious acceptance run, record at least:

- DocMergeForge commit SHA;
- Windows edition/version/build;
- Microsoft Word product/version/build;
- Word architecture;
- source corpus identifier/revision;
- exact ordered source list identifier;
- output/evidence SHA-256;
- measured acceptance result;
- whether Word displayed a repair prompt;
- manual visual/behavior review result;
- known deviations;
- regression issue/test references for failures.

Do not record confidential manuscript text in a public acceptance ledger.

## Why this is not wired into production

The production DOCX engine supports publication-specific behavior beyond simple source insertion, including settings, generated headings/TOC behavior, conflict policy, cancellation, project transactions, reports, and other integration guarantees.

The Word prototype does not yet implement and certify that complete contract.

Therefore:

```text
word.production_ready = false
```

must remain unchanged until the complete native merge/application integration and acceptance matrix are finished.

## Next required Word work

Before production certification, complete and verify at least:

1. real Word execution on a controlled Windows acceptance host;
2. representative multi-document corpus runs;
3. complex section/header/footer linkage cases;
4. styles/themes and list-numbering collision behavior;
5. floating images/drawings/text boxes;
6. fields/TOC/bookmarks/hyperlinks;
7. comments/tracked changes/content controls;
8. equations/charts/SmartArt/embedded objects/custom XML;
9. very large documents and long-running automation;
10. cancellation/timeout/Word-process cleanup behavior;
11. packaged desktop integration if Word mode will be distributed;
12. regression tests for every discovered defect;
13. documented human rendering review;
14. exact-version release evidence.

Until those gates are satisfied, use this subsystem only for explicit acceptance work.

See also:

- [DOCX Fidelity Adapters and Acceptance](docx-fidelity-acceptance.md)
- [Private DOCX Fidelity Corpus Testing](docx-fidelity-corpus.md)
- [DOCX Engine](docx-engine.md)
- [Known Limitations](known-limitations.md)
