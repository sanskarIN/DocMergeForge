# DOCX Fidelity Adapters and Acceptance

DocMergeForge separates **adapter implementation**, **local automation availability**, and **production-readiness**. These are different states and must never be collapsed into one claim.

The portable OOXML path remains the production-supported DOCX merge engine. LibreOffice and Microsoft Word now have explicit source-preserving round-trip adapter boundaries and measurable acceptance evidence, but neither external adapter is automatically selected for production merging.

## Fidelity states

`docmergeforge fidelity-capabilities` reports these fields for each mode:

- `mode` — `portable`, `libreoffice`, or `word`;
- `available` — the local automation host/executable can be detected;
- `automation_ready` — DocMergeForge has an implementation path that can attempt the operation;
- `production_ready` — the mode is allowed by the production merge gate;
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

The normal DOCX merge engine still calls the production-fidelity gate before document work begins. Selecting a non-production fidelity mode is rejected rather than silently falling back.

## LibreOffice adapter

The LibreOffice adapter searches for:

```text
libreoffice
soffice
```

The explicit round-trip operation:

1. requires separate `.docx` source and destination paths;
2. refuses to overwrite an existing destination;
3. snapshots the source SHA-256;
4. invokes LibreOffice without a shell using headless/no-startup UI options;
5. writes the converted document into a temporary directory beside the destination;
6. validates the temporary OOXML package;
7. verifies the source hash is unchanged;
8. promotes the validated copy to the requested destination;
9. validates the final destination again;
10. verifies the source hash again.

LibreOffice automation is an **acceptance tool**, not an implicit replacement for the portable merge engine.

## Microsoft Word adapter

The Microsoft Word adapter is Windows-only and uses Windows PowerShell to drive installed Word through COM. No `pywin32` runtime dependency is required.

The generated PowerShell automation:

- starts Word invisibly;
- disables interactive alerts;
- opens the source read-only;
- saves a DOCX copy with Word's DOCX format identifier;
- closes the document;
- quits Word in a `finally` block;
- releases COM objects;
- writes only to a temporary destination before DocMergeForge validates/promotes it.

The Python boundary applies the same timeout, source-hash, no-overwrite, separate-output, and OOXML validation rules used by the LibreOffice adapter.

Detecting Windows PowerShell does **not** prove Microsoft Word is installed. Actual COM availability is verified only when the adapter is run.

## Native command safety boundary

External office execution is centralized in the native DOCX command boundary.

Safety properties include:

- argument-vector execution with `shell=False` behavior through `subprocess.run`;
- no command-string concatenation;
- mandatory positive timeout;
- captured stdout/stderr;
- non-zero exit codes treated as failures;
- OS launch errors translated to validation failures;
- bounded error detail in raised messages;
- post-command DOCX package validation;
- source-integrity verification.

A command that exits successfully but produces no output, an empty file, or invalid OOXML is still a failure.

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

## Explicit round-trip acceptance

To test one representative document with LibreOffice:

```bash
docmergeforge fidelity-roundtrip \
  --input "./samples/representative.docx" \
  --output "./evidence/representative-libreoffice.docx" \
  --mode libreoffice \
  --timeout 300
```

On a Windows machine with Microsoft Word installed:

```powershell
docmergeforge fidelity-roundtrip `
  --input ".\samples\representative.docx" `
  --output ".\evidence\representative-word.docx" `
  --mode word `
  --timeout 300
```

The command exits with:

- `0` when the measured structural acceptance passes;
- `2` when the produced document is valid but the measured acceptance criteria do not match;
- an error when the adapter cannot run safely or output validation fails.

The acceptance output is a separate copy. Originals remain untouched.

## Evidence fields

Round-trip evidence contains:

- selected adapter mode;
- source/output paths;
- source/output SHA-256;
- source/output structural counts;
- source/output risky-construct findings;
- whether measured structural counts match;
- newly introduced risky constructs;
- overall `accepted` status.

Measured structural counts currently include:

- paragraphs;
- tables;
- inline shapes;
- sections;
- headings.

`accepted=true` requires the selected structural snapshot to match and no new risk categories to appear.

This is deliberately narrower than a claim of visual/layout identity.

## Risky OOXML construct review

The OOXML risk scanner now reports categories including:

- VBA/macros;
- embedded OLE/package objects;
- ActiveX controls;
- custom XML;
- comments/annotations;
- external relationships;
- tracked insertions, deletions, and move revisions;
- content controls;
- Word field codes;
- Office Math equations;
- alternative-format imported content (`altChunk`);
- charts;
- SmartArt/diagram parts;
- unusually large markup parts skipped by the bounded risk scan.

Risk detection is a review signal. A finding does not automatically mean the document is corrupt, and absence of findings does not prove universal fidelity.

## Synthetic acceptance fixture

The repository includes:

```bash
python scripts/check_docx_fidelity_acceptance.py \
  --mode libreoffice \
  --output-dir fidelity-evidence
```

The script creates a deterministic smoke fixture containing:

- a heading;
- normal text;
- bold and italic runs;
- bullet paragraphs;
- a table;
- a section header;
- a section footer.

It then executes the selected external adapter and writes:

```text
fidelity-source.docx
fidelity-<mode>-roundtrip.docx
fidelity-<mode>-evidence.json
```

Existing artifacts are never overwritten.

## GitHub Actions acceptance

`.github/workflows/fidelity-acceptance.yml` runs the LibreOffice path on an Ubuntu GitHub-hosted runner when fidelity-related code changes or when manually dispatched.

The workflow:

1. installs LibreOffice Writer;
2. installs DocMergeForge and development dependencies;
3. reports fidelity capabilities;
4. runs fidelity-focused unit tests;
5. performs a real LibreOffice round-trip using the synthetic fixture;
6. prints the JSON evidence;
7. uploads the source, round-trip output, and evidence JSON as a workflow artifact.

This provides real LibreOffice process evidence on Linux. It is not Windows/macOS LibreOffice acceptance and it is not Microsoft Word acceptance.

## Microsoft Word acceptance requirement

GitHub-hosted Windows runners do not constitute Microsoft Word acceptance unless Word is actually installed and licensed in that environment. A production Word claim therefore requires a controlled Windows acceptance machine with Word present.

At minimum, a Word acceptance record should capture:

- Windows version/build;
- Microsoft Word version/build and architecture;
- DocMergeForge commit SHA;
- representative corpus identifier;
- capability output;
- per-document fidelity evidence JSON;
- Word repair-prompt result;
- visual/manual review result;
- generated document hashes;
- failures or known deviations.

Do not mark Word production-ready merely because PowerShell is present.

## Representative corpus gate

The synthetic fixture is a smoke test, not a sufficient production corpus. Before an external adapter can become production-ready, run documents that cover the constructs the project intends to support, including where applicable:

- multiple sections and orientations;
- complex headers/footers and section linking;
- page-number restarts and continuous numbering;
- nested/multi-level numbering;
- custom styles and themes;
- tables with merges, widths, borders, and pagination behavior;
- images, drawings, text boxes, charts, and SmartArt;
- hyperlinks and bookmarks;
- footnotes/endnotes;
- fields and TOC behavior;
- equations;
- comments and tracked changes;
- content controls;
- embedded objects;
- custom XML;
- very large documents;
- non-Latin text and representative fonts;
- documents produced by multiple Word/LibreOffice versions.

For each supported construct, record both automated evidence and manual rendering/behavior review in the target application.

## Why round-trip before native merge certification

A native office-suite merge adapter can change document semantics even when the process exits successfully. The round-trip stage isolates one variable: whether the external application can safely open and re-save representative source material while preserving the measured structure.

Only after representative round-trip evidence is trustworthy should full native multi-document merge semantics be certified.

## Production-readiness rule

External fidelity modes must remain `production_ready=false` until all required implementation and acceptance work is complete.

Changing that flag requires, at minimum:

1. a complete multi-document adapter for the target application;
2. deterministic source-preserving behavior;
3. cancellation/timeout/error cleanup;
4. structural/package validation;
5. representative corpus automation;
6. target-platform acceptance;
7. documented manual rendering review;
8. regression coverage for discovered fidelity defects;
9. release-evidence records tied to exact commits and tool versions.

Until then, portable mode remains the only production-enabled merge path.
