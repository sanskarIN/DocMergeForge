# Architecture

DocMergeForge is a local-first Python application with a shared domain/application layer behind two user surfaces: a PySide6 desktop application and an `argparse` CLI. The architecture deliberately separates discovery/validation, format-specific merge engines, project orchestration, reporting, and filesystem publication safety.

## Architectural goals

The design prioritizes:

- deterministic numbered-part discovery/order;
- strict PDF/DOCX type separation;
- source immutability and integrity evidence;
- companion-code separation;
- format-specific validation;
- transactional publication of complete output bundles;
- crash-recoverable final promotion;
- local/private processing;
- reusable project configuration;
- cross-platform desktop/CLI operation;
- testable packaging and CI boundaries.

## High-level layers

```text
┌───────────────────────────────────────────────────────────────┐
│ User surfaces                                                 │
│  PySide6 Desktop UI                 CLI (`docmergeforge`)      │
└──────────────────────────────┬────────────────────────────────┘
                               │
┌──────────────────────────────▼────────────────────────────────┐
│ Application orchestration                                     │
│  MergeApplicationService · Preflight · progress/cancellation  │
└───────────────┬───────────────────────────────┬───────────────┘
                │                               │
┌───────────────▼──────────────┐  ┌────────────▼───────────────┐
│ Discovery / project / models │  │ Audit / reports / compare  │
│ classification · ordering    │  │ manifest · checksums       │
│ validation · settings        │  │ companion index · checklist│
└───────────────┬──────────────┘  └────────────┬───────────────┘
                │                               │
┌───────────────▼───────────────────────────────▼───────────────┐
│ Format engines                                                 │
│  PDF (`pypdf`, publication helpers) · DOCX (OOXML/docxcompose)│
└──────────────────────────────┬────────────────────────────────┘
                               │
┌──────────────────────────────▼────────────────────────────────┐
│ Filesystem safety                                              │
│ hashing · storage/write probe · staging · journal · rollback   │
└───────────────────────────────────────────────────────────────┘
```

## Package map

The installable source package is `src/docmergeforge/`.

### `app/`

Application orchestration. `MergeApplicationService` is the main coordinator for project discovery, validation, storage checks, format-engine execution, reporting, source revalidation, and final transaction promotion.

`app/preflight.py` builds read-only evidence for the CLI/desktop workflow.

### `audit/`

Publication text-audit primitives. It extracts text from PDF/DOCX and reports targeted findings without rewriting sources.

### `cli/`

The command-line application. It parses commands/options and delegates document work to shared application/domain services instead of implementing a separate merge stack.

### `companion/`

Companion/source-code related helpers. Companion material is kept outside manuscript engines.

### `core/`

Shared dataclasses/enums/exceptions. Important models include:

- `InputDocument`;
- `PartIdentity`;
- `ValidationResult`;
- `PdfSettings`;
- `DocxSettings`;
- `MergeSettings`;
- `MergeProject`;
- `OutputArtifact`;
- `CompanionReference`;
- `MergeManifest`.

### `diagnostics/`

Privacy-aware logging/diagnostic behavior.

### `discovery/`

Recursive scanning, file classification, part-number detection, PDF inspection, hashing, and natural-sort helpers.

### `docx/`

Portable DOCX merge engine, fidelity capability/risk analysis, OOXML package validation, and supporting utilities.

### `ordering/`

Ordering-specific domain/UI support.

### `packaging/`

Shared PyInstaller argument/root-validation configuration so scripts/tests/CI use one build definition.

### `pdf/`

PDF merge engine, passwords/encryption handling, publication helpers, and output validation.

### `presets/`

Guided project definitions, including SQL Full Mastery Parts 1–120.

### `profiles/`

Merge-profile definitions/selection support.

### `project/`

Project JSON persistence, selected-file behavior, recent/recovery-related state.

### `reports/`

Manifest, checksums, project/preset reports, companion indexes, and publishing checklist generation.

### `settings/`

Application preference model/persistence.

### `ui/`

PySide6 desktop dialogs/windows/workers. UI code is a client of the shared application/domain layer.

### `utilities/`

Cross-cutting low-level safety helpers such as hashing, storage estimation/writeability probe, atomic output naming, and journaled output transactions.

### `validation/`

Numbered-part validation and output/source comparison logic.

## Core data flow

A full project run follows this conceptual path:

```text
MergeProject
   │
   ▼
Discover source roots
   │
   ├── PDF inputs
   ├── DOCX inputs
   ├── companion inputs
   └── ignored/other
   │
   ▼
Validate expected numbered sets
   │
   ▼
Snapshot tracked source hashes
   │
   ▼
Check output writeability + storage
   │
   ▼
Open OutputTransaction
   │
   ├── stage/merge/validate PDF (if present)
   ├── stage/merge/validate DOCX (if present)
   ├── verify source hashes unchanged
   ├── stage reports/manifest/checksums/index/checklist
   └── cancellation checks
   │
   ▼
Write `promoting` journal
   │
   ▼
Backup existing finals if needed
   │
   ▼
Promote complete staged bundle
   │
   ▼
Write `committed` journal
   │
   ▼
Cleanup backups/staging
```

No full project manuscript is considered published until the final transaction promotion completes.

## Domain states

`MergeState` models workflow state:

```text
CREATED
DISCOVERING
VALIDATING
READY
MERGING
VERIFYING
REPORTING
SUCCEEDED
FAILED
CANCELLED
```

Desktop recovery/checkpoint UX can use this state, but filesystem/source validation remains authoritative after a restart.

## Discovery boundary

The discovery layer is intentionally format-light. It identifies:

- `.pdf` as PDF;
- `.docx` as DOCX;
- recognized archive suffixes as companion;
- everything else as other.

It detects part numbers from common `part`/`chapter`/`volume`/abbreviated naming forms and computes SHA-256 for every discovered file.

PDF inspection records page count where possible and marks encrypted files without trying to persist passwords.

## Validation boundary

Numbered validation decides whether an expected range is complete and duplicate-free for a specific kind.

The application service applies this independently to PDF and DOCX. A PDF cannot satisfy a missing DOCX part and vice versa.

## Format-engine boundary

### PDF

PDF processing uses `pypdf` plus DocMergeForge publication helpers. The engine is responsible for ordered page composition and PDF-specific features/validation.

### DOCX

Portable DOCX composition uses `python-docx`/`docxcompose` plus direct OOXML validation/repair-aware logic where needed.

The engine boundary exists because PDF page composition and DOCX package merging have fundamentally different correctness/fidelity models.

## Fidelity boundary

No generic library stack can guarantee exact rendering of every Word construct.

Portable mode is the current production-supported DOCX path. Risky/complex constructs should be detected/surfaced where practical.

LibreOffice and Microsoft Word high-fidelity integrations are architectural extension points, but they must not silently substitute for portable mode until their automation adapters and real acceptance tests are complete.

## Source-integrity boundary

Discovery hashes sources. A full project run snapshots hashes for PDF, DOCX, and companion material and verifies them again before final promotion.

If a tracked file changes during a long merge, the operation fails rather than publishing a bundle assembled from inconsistent source versions.

## Companion-code boundary

Companion archives never enter the PDF/DOCX engines.

The project service can:

- hash them;
- track them for source-integrity changes;
- create companion index evidence.

It does not extract, build, refactor, or merge their contents.

## Publication transaction boundary

`OutputTransaction` creates a hidden staging directory inside the output folder. Every final output receives a staging path.

Before final mutation it writes `transaction.json` containing staged fingerprints and rollback metadata.

The promotion algorithm supports:

- new output promotion;
- overwrite with previous-final backup;
- rollback on exceptions;
- preserved recovery evidence if rollback itself fails;
- fail-closed recovery after process interruption.

See [Publication Recovery](recovery.md).

## Storage boundary

The storage layer performs two independent checks:

1. output writeability probe;
2. free-space estimate.

This prevents a merge from doing expensive document work only to discover that the destination cannot create transaction files.

## Reporting boundary

Reports are generated before final transaction promotion so they remain consistent with the manuscript outputs.

Generic project evidence includes:

- companion index;
- Markdown/HTML merge report;
- JSON manifest;
- SHA-256 checksums when enabled;
- publishing checklist.

## UI architecture

The PySide6 UI uses workers/progress callbacks for long-running operations. It exposes application services rather than owning a second copy of merge logic.

Accessibility metadata is treated as implementation state and checked through `scripts/check_accessibility.py` in cross-platform Build Smoke.

## CLI architecture

The CLI is an `argparse` front end with commands for:

- `validate`;
- `pdf`;
- `docx`;
- `sql-preset`;
- `project-create`;
- `merge`;
- `recover-output`;
- `audit`;
- `compare`.

JSON is used for machine-readable validation/preflight/recovery/audit/compare evidence where appropriate.

## Packaging architecture

`scripts/build_desktop.py` delegates PyInstaller arguments to `docmergeforge.packaging.desktop`.

This shared configuration is used/tested consistently across local builds and GitHub Actions.

The current packaging pipeline is an unsigned development-build foundation, not the signing/notarization layer.

## Testing architecture

Quality is layered:

- unit tests;
- integration tests;
- generated regression fixtures;
- 120-Part Regression workflow;
- cross-platform Build Smoke;
- CodeQL security analysis;
- manual Stress Acceptance;
- Package Desktop workflow;
- human release acceptance.

Each layer proves a different property; no single green workflow is treated as complete production certification.

## Extension guidelines

When adding a new feature:

- keep user-interface code out of core merge engines;
- add behavior to shared application/domain services so CLI/desktop remain consistent;
- preserve source immutability;
- keep format-specific logic inside the relevant engine;
- stage new publication evidence inside the same transaction when it must be coherent with outputs;
- add recovery behavior/tests for any new final-path mutation;
- update project schema conservatively;
- add diagnostics without leaking sensitive data;
- extend CI/acceptance documentation when a new platform/tool boundary is introduced.
