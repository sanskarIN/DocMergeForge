# DOCX Fidelity Adapters and Acceptance

DocMergeForge separates **adapter implementation**, **local automation availability**, **measured acceptance**, and **production-readiness**. These are different states and must never be collapsed into one claim.

The portable OOXML path remains the only production-supported DOCX merge engine. LibreOffice and Microsoft Word have explicit source-preserving one-document round-trip adapters plus separate native multi-document acceptance prototypes, but neither external mode is automatically selected for production merging.

## Fidelity states

`docmergeforge fidelity-capabilities` reports these fields for each mode:

- `mode` — `portable`, `libreoffice`, or `word`;
- `available` — the local automation host/executable can be detected;
- `automation_ready` — DocMergeForge has an implementation path that can attempt the external operation;
- `production_ready` — the mode is allowed by the normal production merge gate;
- `executable` — detected executable/automation host when applicable;
- `detail` — operator-facing explanation of the current state.

A detected external office application is not enough to make `production_ready=true`.

## Portable mode

Portable mode uses the bundled Python OOXML stack and remains the only production-enabled DOCX merge mode.

```text
mode = portable
available = true
automation_ready = true
production_ready = true
```

The normal DOCX merge engine calls the production-fidelity gate before document work begins. Selecting a non-production external fidelity mode is rejected rather than silently falling back or being promoted.

## LibreOffice one-document adapter

The round-trip adapter searches for `libreoffice` or `soffice` and:

1. requires separate `.docx` source and destination paths;
2. refuses an existing destination;
3. snapshots the source SHA-256;
4. creates an isolated temporary LibreOffice user profile;
5. invokes LibreOffice headlessly without a shell;
6. writes output into a temporary directory beside the requested destination; and
7. hands the result to the shared native-output promotion boundary.

The isolated user profile reduces interference from an already-running user profile. It does not make claims about every LibreOffice extension, enterprise policy, rendering behavior, or version.

## Supervised LibreOffice native multi-document acceptance

DocMergeForge also has one authoritative POSIX Writer/UNO multi-document **acceptance prototype**:

```text
src/docmergeforge/docx/libreoffice_uno_merge.py
src/docmergeforge/docx/libreoffice_uno_acceptance.py
scripts/check_libreoffice_uno_merge_smoke.py
scripts/check_libreoffice_uno_merge_acceptance.py
```

It is deliberately separate from normal production merging.

The supervised implementation:

- creates a unique temporary Writer user profile;
- creates a unique UNO pipe;
- copies the first source into a writable master working copy;
- selects a Python interpreter that can actually `import uno`;
- launches LibreOffice in a new POSIX session/process group;
- connects through UNO and inserts later documents in exact supplied order with Writer's document insertion API;
- optionally requests a page-before insertion boundary;
- exports the working document with the `Office Open XML Text` filter;
- supervises/reaps the launcher while tracking the complete process group;
- escalates only its isolated group from `SIGTERM` to `SIGKILL` when necessary;
- validates output and source revision identity around promotion; and
- records privacy-safe measured acceptance evidence.

The first native Writer pass rule currently measures body paragraph/table/inline-shape/heading structure, ordered body/table-cell text fingerprints, source SHA-256 values, and newly introduced risky-OOXML categories. It intentionally does **not** certify sections, page geometry, headers/footers, page numbering, exact pagination, floating objects, field rendering, charts/SmartArt, embedded objects, custom XML, or font substitution.

See [LibreOffice Native Multi-Document Merge Acceptance](libreoffice-native-merge-acceptance.md).

## Microsoft Word one-document adapter

The Microsoft Word round-trip adapter is Windows-only and uses Windows PowerShell to drive installed Word through COM. No `pywin32` runtime dependency is required.

The generated PowerShell automation starts Word invisibly, disables alerts, force-disables automation macros, opens the source read-only without adding it to recent files, saves a separate DOCX copy, closes the document, quits Word in `finally`, releases COM objects, and writes only to a temporary destination before DocMergeForge validates/promotes it.

Detecting Windows PowerShell does **not** prove Microsoft Word is installed. Actual COM availability is verified only when the adapter is run.

## Microsoft Word native multi-document acceptance

A separate Word-native acceptance prototype uses ordered `Range.InsertFile(...)`, real next-page/continuous section boundaries, exact COM-created Word process identity, source-revision binding, structural/text/section/page-number/risk evidence, and controlled timeout cleanup.

The process identity is PID + `WINWORD` name + process start-time fingerprint. Cleanup authority is restricted to that still-matching instance; PID reuse or mismatches fail closed.

See [Microsoft Word Native Merge Acceptance](word-native-merge-acceptance.md) and [Microsoft Word Timeout Cleanup Acceptance](word-timeout-cleanup-acceptance.md).

## Native command and output safety boundary

External-office command execution and final output promotion are fail-closed.

Command safety includes:

- argument-vector execution rather than shell command concatenation;
- mandatory positive timeouts;
- captured stdout/stderr where appropriate;
- non-zero exit codes treated as failures;
- OS launch errors translated to validation failures;
- bounded native error detail; and
- no assumption that exit code `0` means valid DOCX output.

Final promotion safety includes:

1. refusal to overwrite an existing acceptance destination;
2. temporary DOCX package validation before promotion;
3. tracked source-hash validation immediately before promotion;
4. promotion to the separate final destination;
5. final destination package validation;
6. tracked source-hash validation immediately after promotion; and
7. removal of the newly created destination if final validation/integrity fails.

This shared promotion rule applies to both one-document adapters and both maintained native multi-document prototypes.

## Capability inspection

Run:

```bash
docmergeforge fidelity-capabilities
```

Example shape:

```json
[
  {
    "mode": "portable",
    "available": true,
    "production_ready": true,
    "detail": "Portable OOXML merge engine bundled with DocMergeForge.",
    "automation_ready": true,
    "executable": null
  }
]
```

Exact external executable paths and availability depend on the machine.

## Explicit one-document round-trip acceptance

LibreOffice:

```bash
docmergeforge fidelity-roundtrip \
  --input "./samples/representative.docx" \
  --output "./evidence/representative-libreoffice.docx" \
  --mode libreoffice \
  --timeout 300
```

Microsoft Word on a controlled Windows machine with Word installed:

```powershell
docmergeforge fidelity-roundtrip `
  --input ".\samples\representative.docx" `
  --output ".\evidence\representative-word.docx" `
  --mode word `
  --timeout 300
```

The command exits with `0` when measured round-trip acceptance passes, `2` when a valid result exists but measured acceptance differs, and an error when the adapter cannot run safely or output validation fails.

## Round-trip evidence fields

One-document evidence contains source/output hashes, structural snapshots, privacy-safe visible-text fingerprints, source/output risk categories, newly introduced risk categories, structure/content match flags, and overall `accepted` status.

Measured structural counts currently include body paragraphs/tables, inline shapes, sections, headings, and header/footer paragraphs/tables. Content fingerprints cover body paragraph/table-cell text and header/footer paragraph/table-cell text without serializing the text itself.

`accepted=true` requires structural equality, measured content equality, and no new risky-construct category.

This is deliberately narrower than visual/layout identity.

## Risky OOXML construct review

The scanner reports categories including VBA/macros, OLE/package embeddings, ActiveX, custom XML, comments, external relationships, tracked revisions/moves, content controls, Word field codes, Office Math, `altChunk`, charts, SmartArt/diagram parts, and unusually large markup parts skipped by the bounded scan.

Markup scanning uses XML namespace/local-name parsing rather than depending on one literal prefix or quote style. External relationship detection parses relationship XML and handles `TargetMode` case-insensitively.

Risk detection is a review signal. A finding does not automatically mean corruption, and absence of findings does not prove universal fidelity.

## One-document synthetic acceptance fixture

```bash
python scripts/check_docx_fidelity_acceptance.py \
  --mode libreoffice \
  --output-dir fidelity-evidence
```

The fixture contains heading/normal/formatted/bullet text, a table, and section header/footer content. The real LibreOffice one-document workflow uses this fixture and uploads its synthetic evidence.

## Supervised LibreOffice multi-document commands

Synthetic Writer smoke:

```bash
python scripts/check_libreoffice_uno_merge_smoke.py \
  --output-dir libreoffice-uno-evidence \
  --timeout 300
```

Private ordered acceptance:

```bash
python scripts/check_libreoffice_uno_merge_acceptance.py \
  --input "./private-corpus/Part 1.docx" \
  --input "./private-corpus/Part 2.docx" \
  --output "./private-libreoffice-evidence/merged.docx" \
  --evidence "./private-libreoffice-evidence/evidence.json"
```

The explicit command returns `0` when its measured native-Writer rule passes and `2` when a valid merged result/evidence exists but measured content/structure/risk acceptance fails.

## GitHub Actions acceptance surfaces

`.github/workflows/fidelity-acceptance.yml` executes the general fidelity regressions and a **real one-document LibreOffice Writer round trip** on Ubuntu.

`.github/workflows/libreoffice-uno-acceptance.yml` is the single maintained **real multi-document LibreOffice Writer/UNO** lane. It installs Writer + `python3-uno`, verifies the UNO bridge, runs supervised boundary/command tests, performs a real two-document insertion, and uploads synthetic evidence.

`.github/workflows/libreoffice-uno-process-cleanup.yml` independently runs real POSIX subprocess cleanup regressions so process supervision does not depend on a document-fidelity outcome.

`.github/workflows/word-native-acceptance.yml` is manual-only on a controlled self-hosted Windows/Word runner and contains both normal native Word merge and timeout-cleanup stages.

A workflow definition is not evidence that it passed. Record exact run IDs/checkpoints/artifacts before citing a current-head external-application acceptance result.

## Private representative one-document corpus acceptance

For representative documents that cannot be committed publicly:

```bash
docmergeforge fidelity-corpus \
  --input-dir "./private-corpus" \
  --output-dir "./private-fidelity-evidence" \
  --mode libreoffice
```

On a controlled Windows machine with Word installed, use `--mode word`.

The corpus runner deterministically discovers DOCX files, preserves source-relative subdirectories below `roundtrip/`, applies structural/content/risk acceptance per file, records hashes/fingerprints without visible manuscript text, rewrites normal paths to relative values, redacts known roots from recorded errors, refuses output inside the source corpus, fails closed on no matches, and never treats a fail-fast partial run as accepted.

Generated round-trip DOCX files still contain manuscript content and remain sensitive.

See [Private DOCX Fidelity Corpus Testing](docx-fidelity-corpus.md).

## Microsoft Word acceptance requirement

GitHub-hosted Windows runners do not constitute Microsoft Word acceptance unless Word is actually installed and licensed in that environment. A production Word claim requires a controlled Windows acceptance machine with Word present.

At minimum, record Windows/Word version/build/architecture, DocMergeForge commit SHA, representative corpus identifier, capability output, measured evidence, repair-prompt result, manual review result, generated document hashes, and known deviations.

Do not mark Word production-ready merely because PowerShell is present.

## Representative corpus gate

Synthetic fixtures are smoke tests, not sufficient production corpora. Before an external adapter can become production-ready, run documents covering the constructs the project intends to support, including multiple sections/orientations, complex headers/footers/linking, page-number restarts, multi-level numbering, custom styles/themes, complex tables, images/drawings/text boxes/charts/SmartArt, hyperlinks/bookmarks, footnotes/endnotes, fields/TOC, equations, comments/tracked changes, content controls, embedded objects, custom XML, non-Latin text/fonts, very large documents, and documents produced by multiple office-suite versions.

For every claimed construct, record both automated evidence and manual rendering/behavior review in the target application.

## Production-readiness rule

External fidelity modes must remain `production_ready=false` until the complete supported application contract and acceptance matrix are verified.

Changing that flag requires at least:

1. complete multi-document behavior for the target application;
2. deterministic source-preserving semantics;
3. cancellation/timeout/error/process cleanup appropriate to the target OS;
4. structural/package/content/layout validation appropriate to the support claim;
5. representative corpus automation;
6. exact target-platform/application-version acceptance;
7. documented manual rendering/interoperability review;
8. regression coverage for discovered fidelity defects;
9. packaged-app integration/acceptance where the external mode is distributed; and
10. release-evidence records tied to exact commits/tool versions.

Until then, portable mode remains the only production-enabled merge path.
