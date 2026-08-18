# Microsoft Word Native Merge Acceptance

DocMergeForge includes an explicit Microsoft Word multi-document merge prototype for acceptance work on controlled Windows machines. It is **not** connected to the normal production DOCX merge engine and it does not make the `word` fidelity mode production-ready.

The purpose of this subsystem is to make Word-native merge behavior measurable and fail-closed before any production capability claim is considered.

## Current status

```text
round-trip Word adapter: implemented
native Word multi-document merge prototype: implemented
measured structure/text evidence: implemented
section-layout/linkage evidence: implemented
page-number section-semantic evidence: implemented
source-revision binding: implemented
exact Word process identity/cleanup boundary: implemented
controlled synthetic Word smoke harness: implemented
controlled timeout-cleanup harness: implemented
manual self-hosted Word acceptance workflow: implemented
production Word merge mode: disabled
controlled real-Word passing run: still required
controlled real timeout-cleanup run: still required
representative corpus acceptance: still required
manual rendering/behavior review: still required
```

The normal `docmergeforge docx` workflow continues to use the portable production-supported OOXML engine.

## Native merge prototype

Implementation:

```text
src/docmergeforge/docx/word_merge.py
```

The prototype accepts an ordered DOCX source sequence and a separate non-existing destination. Before Word starts it validates source types/packages, rejects source/output collisions and duplicate resolved source paths, validates a positive timeout, records source SHA-256 hashes, and refuses to overwrite an existing destination.

The PowerShell automation starts `Word.Application` through COM, keeps Word invisible, disables alerts, forces automation macros off, opens the first source read-only, saves a separate working copy, and inserts later sources with `Range.InsertFile(...)` in manifest order.

The first source is never edited in place.

## Section boundary strategy

A plain page break is not used between source documents.

When `start_each_on_new_page=true`, Word uses:

```text
wdSectionBreakNextPage = 2
```

When `start_each_on_new_page=false`, Word uses:

```text
wdSectionBreakContinuous = 3
```

The explicit section boundary gives Word a place to preserve source-specific orientation, page geometry, headers, footers, linkage, and numbering behavior. This improves the native merge boundary but does not by itself prove universal fidelity.

## Exact Word process identity and cleanup

Immediately after COM startup, the PowerShell merge script resolves the process owning `Word.Application.Hwnd` with `GetWindowThreadProcessId`. It records a temporary identity containing:

```json
{
  "process_id": 1234,
  "process_name": "WINWORD",
  "start_time_utc_ticks": 638000000000000000
}
```

Implementation:

```text
src/docmergeforge/docx/word_process.py
```

PID alone is not sufficient cleanup authority because Windows can reuse process IDs. Forced cleanup is permitted only when the recorded PID, process name `WINWORD`, and process start-time fingerprint still match.

The cleanup path gives the exact process a short natural-exit grace period after COM `Quit()`. If it disappears naturally, no forced termination is reported. If it is still the same process after the grace period, the helper may use `Stop-Process -Force`, then polls until the PID disappears. PID reuse, a different process name, a changed start time, invalid identity JSON, or inability to confirm termination fails closed.

Windows PowerShell 5.1 may write UTF-8 JSON with a BOM, so the Python identity reader accepts UTF-8-with-BOM input.

If the native merge command fails or times out after the process identity exists, DocMergeForge attempts exact-instance cleanup before propagating failure. If that cleanup itself fails, the merge reports an explicit cleanup validation failure.

If the command reports success but Word still requires forced termination after its natural-exit window, the exact process is cleaned but the merge is rejected. Normal Word shutdown is part of acceptance.

The separate controlled-runner process-state script remains detection-only: it never kills an unknown pre-existing Word process.

## Temporary output and source preservation

The native merge writes into a temporary working directory beside the requested output. A successful command is not enough. DocMergeForge also requires recorded process identity, acceptable Word shutdown, non-empty structurally valid OOXML, unchanged source hashes, safe promotion to the final destination, final output validation, and a final source-integrity check.

## Measured multi-document acceptance

Implementation:

```text
src/docmergeforge/docx/word_merge_acceptance.py
src/docmergeforge/docx/section_evidence.py
```

Acceptance captures source SHA-256 values **before** expected evidence is calculated. The same hashes are checked after expected evidence construction, after Word automation, and again after output evidence is measured. Evidence therefore cannot silently combine different source revisions.

### Structural evidence

The expected/output structural snapshot measures:

- non-empty body paragraphs;
- body tables;
- inline shapes;
- headings;
- sections;
- non-empty header/footer paragraphs;
- header/footer tables.

### Visible-text evidence

Privacy-safe SHA-256 fingerprints cover ordered visible text from body paragraphs, body table cells, headers, and footers. Plain manuscript text is not serialized into acceptance JSON. Length-delimited UTF-8 records prevent concatenation-boundary ambiguity.

### Section-layout and linkage evidence

`section_properties_sha256` covers the ordered global section sequence and currently measures:

- section start type;
- orientation;
- page width/height;
- top/bottom/left/right margins;
- gutter;
- header/footer distances;
- different-first-page behavior;
- normal/first/even header linked-to-previous state;
- normal/first/even footer linked-to-previous state.

### Page-number section semantics

`page_number_properties_sha256` parses `word/document.xml` and measures each section's:

- `w:start`;
- `w:fmt`;
- `w:chapStyle`;
- `w:chapSep`.

Sections without explicit `w:pgNumType` remain represented by an empty record. Multiple input DOCX files are normalized into one monotonically increasing global section sequence because the result is one merged DOCX; source-document indices are deliberately not included in this fingerprint.

### Risk evidence

The acceptance layer records source risky-OOXML categories, output risky categories, and newly introduced output categories.

### Acceptance rule

`accepted=true` currently requires:

1. expected and output structural snapshots match;
2. visible-text fingerprints match;
3. section-layout/linkage fingerprints match;
4. page-number section-semantic fingerprints match; and
5. no new risky-construct category appears in the output.

This is deliberately strict and deliberately incomplete as a universal rendering proof.

## Acceptance command

On a controlled Windows machine with Microsoft Word installed:

```powershell
python scripts/check_word_native_merge_acceptance.py `
  --input ".\private-corpus\Part 1.docx" `
  --input ".\private-corpus\Part 2.docx" `
  --output ".\private-word-evidence\merged.docx" `
  --evidence ".\private-word-evidence\word-merge-evidence.json"
```

Repeat `--input` in exact merge order. Optional controls are `--timeout`, `--start-each-on-new-page`, and `--no-start-each-on-new-page`. Existing output/evidence artifacts are not overwritten.

Exit behavior:

- `0` — measured acceptance passed;
- `2` — a valid output was produced but measured acceptance failed;
- other non-zero/error — automation, cleanup, validation, input, source-integrity, or output safety failed.

## Controlled synthetic smoke

Run:

```powershell
python scripts/check_word_native_merge_smoke.py `
  --output-dir ".\word-merge-evidence" `
  --timeout 900
```

The smoke creates two deterministic documents with distinct body/table/header/footer content. Source 1 is portrait and uses page numbering starting at decimal 1. Source 2 is landscape, uses distinct margins/header/footer distances, and restarts page numbering at upper-Roman 7. `w:pgNumType` is inserted at a schema-safe location before `w:cols` in `w:sectPr`.

A real smoke therefore exercises more than paragraph counts: it exercises ordered content, section geometry, header/footer evidence, and non-default page-number semantics.

## Controlled timeout cleanup

A separate acceptance harness now intentionally holds an invisible Word COM session longer than the native command timeout:

```powershell
python scripts/check_word_timeout_cleanup_acceptance.py `
  --output-dir ".\word-timeout-evidence" `
  --timeout 20 `
  --hold-seconds 140
```

It requires an actual timeout, requires the exact Word process identity to exist before timeout, invokes the same PID/name/start-time cleanup boundary used by native merge failures, and writes `word-timeout-cleanup-evidence.json`.

A cleanup result may show either natural process exit after the host timeout or exact-process forced termination. Both are distinguished in evidence. Unsafe identity mismatch or cleanup failure is never accepted.

See [Microsoft Word Timeout Cleanup Acceptance](word-timeout-cleanup-acceptance.md) for the complete evidence contract.

## Controlled self-hosted workflow

`.github/workflows/word-native-acceptance.yml` is manual-only and requires:

```text
[self-hosted, Windows, X64, docmergeforge-word]
```

The workflow records Windows/Word environment metadata and `fidelity-capabilities.json`, requires `word.automation_ready=true`, and deliberately fails if `word.production_ready` has been flipped to true before certification.

It rejects a dirty pre-acceptance `WINWORD` process state, runs Word boundary/evidence/process tests, executes the real Word COM merge smoke, executes the controlled timeout-cleanup harness, verifies a clean post-acceptance process state, and uploads available environment/capability/process/merge/timeout evidence even when measured acceptance fails.

A complete workflow pass requires the pre-process state, normal Word merge smoke, timeout-cleanup stage, and final process-state check all to succeed.

A generic GitHub-hosted Windows runner is not treated as Word acceptance because Word installation/licensing/configuration is not assumed.

Defining this workflow is not proof that it has run. A controlled run ID and its artifacts must be reviewed before being cited as Word acceptance.

## What a passing result does not prove

Even a passing synthetic real-Word run plus controlled timeout-cleanup run does not prove identical pagination or line wrapping, font availability/substitution, floating-object coordinates, field/TOC recalculation, rendered page-number fields, chart/SmartArt visual identity, tracked-change/comment display, content controls, embedded objects, custom XML semantics, every Office add-in state, packaged desktop integration, every COM deadlock/cancellation case, or behavior across untested Word builds.

Manual review in the exact Word version being claimed remains mandatory.

## Production gate

The production DOCX engine also owns project settings, generated headings/TOC behavior, conflict policy, cancellation, publication transactions, reports, and other application-level guarantees. The Word prototype has not yet certified that complete contract.

Therefore:

```text
word.production_ready = false
```

must remain unchanged.

## Remaining Word acceptance work

Before production certification, complete and record at least:

1. a real passing controlled Windows/Word native merge smoke;
2. a real passing controlled Word timeout-cleanup run using the implemented harness;
3. representative private multi-document corpus runs;
4. complex multi-section header/footer linkage and numbering cases;
5. rendered fields/TOC/bookmarks/hyperlinks/page-number/chapter-number behavior;
6. styles/themes and list-numbering collision cases;
7. floating images/drawings/text boxes;
8. comments/tracked changes/content controls;
9. equations/charts/SmartArt/embedded objects/custom XML;
10. very large/long-running documents;
11. packaged desktop integration if Word mode will be distributed;
12. regression tests for every discovered defect;
13. documented human rendering/behavior review; and
14. exact supported Word/Windows version evidence.

See also:

- [Microsoft Word Timeout Cleanup Acceptance](word-timeout-cleanup-acceptance.md)
- [DOCX Fidelity Adapters and Acceptance](docx-fidelity-acceptance.md)
- [Private DOCX Fidelity Corpus Testing](docx-fidelity-corpus.md)
- [DOCX Engine](docx-engine.md)
- [Testing and CI](testing-and-ci.md)
- [Known Limitations](known-limitations.md)
