# Architecture

DocMergeForge is a local-first Python application with shared document-processing/domain components behind three maintained user surfaces: a PySide6 desktop application, an `argparse` CLI, and a focused FastAPI responsive browser host. The architecture deliberately separates discovery/validation, format-specific merge engines, project orchestration, reporting, filesystem publication safety, and network-delivery concerns.

## Architectural goals

The design prioritizes:

- deterministic numbered-part discovery/order;
- strict PDF/DOCX type separation;
- source immutability and integrity evidence;
- companion-code separation;
- format-specific validation;
- transactional publication of complete project output bundles;
- crash-recoverable final promotion;
- local/private desktop and CLI processing;
- explicit browser-to-host network trust boundaries;
- reusable project configuration;
- cross-platform Windows/macOS/Linux desktop/CLI operation;
- responsive browser delivery for Android, iOS/iPadOS, ChromeOS, desktop browsers, and other modern browser platforms;
- testable packaging, web, and CI boundaries.

## High-level layers

```text
┌──────────────────────────────────────────────────────────────────────────┐
│ User surfaces                                                            │
│  PySide6 Desktop UI   CLI (`docmergeforge`)   Responsive Web Browser     │
└──────────────┬───────────────────┬──────────────────────┬────────────────┘
               │                   │                      │
               └──────────┬────────┘                      ▼
                          ▼                    ┌────────────────────────────┐
┌──────────────────────────────────────────┐  │ Focused FastAPI web adapter│
│ Application orchestration                │  │ upload/auth/temp workspace │
│ MergeApplicationService · Preflight      │  └──────────────┬─────────────┘
│ project/report/publication transactions  │                 │
└───────────────┬──────────────────────────┘                 │
                │                                             │
┌───────────────▼─────────────────────────────────────────────▼────────────┐
│ Shared discovery / ordering / models / platform capabilities             │
│ classification · natural order · validation helpers · runtime matrix     │
└───────────────┬─────────────────────────────────────────────┬────────────┘
                │                                             │
┌───────────────▼──────────────────┐           ┌──────────────▼────────────┐
│ Audit / reports / project state  │           │ Format engines             │
│ manifest · checksums · recovery  │           │ PDF · DOCX                 │
└───────────────┬──────────────────┘           └──────────────┬────────────┘
                │                                             │
                └──────────────────────┬──────────────────────┘
                                       ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ Filesystem safety                                                        │
│ hashing · storage/write probe · atomic/staged output · journal · rollback│
│ web request temporary workspaces                                         │
└──────────────────────────────────────────────────────────────────────────┘
```

The full project/CLI/desktop publication pipeline and the focused browser merge surface intentionally have different orchestration scopes. The web host reuses shared discovery and PDF/DOCX engines but does not pretend that a one-request browser merge is equivalent to the complete reusable-project transaction/report/recovery workflow.

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

Recursive scanning, file classification, part-number detection, PDF inspection, hashing, and natural-sort helpers. Both full project workflows and the browser host reuse these discovery primitives.

### `docx/`

Portable DOCX merge engine, fidelity capability/risk analysis, OOXML package validation, and supporting utilities.

### `ordering/`

Ordering-specific domain/UI support.

### `packaging/`

Shared PyInstaller argument/root-validation configuration so scripts/tests/CI use one build definition.

### `pdf/`

PDF merge engine, passwords/encryption handling, publication helpers, and output validation.

### `platforms.py`

Maintained runtime/delivery capability matrix. It distinguishes native Windows/macOS/Linux desktop/CLI support from browser-delivered Android/iOS/iPadOS/ChromeOS/web access so public surfaces do not overclaim native mobile packages.

### `presets/`

Guided project definitions, including SQL Full Mastery Parts 1–120.

### `profiles/`

Merge-profile definitions/selection support.

### `project/`

Project JSON persistence, selected-file behavior, synchronization, revision guards, and recovery-related state.

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

### `web/`

Responsive browser host and focused merge API.

- `web/main.py` implements the `docmergeforge-web` command, loopback-safe defaults, non-loopback token requirement, generated-token support, upload limit configuration, and Uvicorn startup.
- `web/app.py` implements the browser/PWA shell, health/platform endpoints, token-protected merge route, upload validation/sanitization, natural ordering, per-request temporary workspace, shared PDF/DOCX engine calls, generic remote error boundary, and response/workspace cleanup.

The web package is a network adapter around shared document-processing components, not a separate PDF/DOCX implementation.

## Full project data flow

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

## Responsive web merge data flow

The focused browser path follows a deliberately smaller request lifecycle:

```text
Browser selects homogeneous PDF or DOCX files
   │
   ▼
POST /api/merge
   │
   ├── optional X-DocMergeForge-Token authentication
   ├── file-count/type/total-size enforcement
   └── sanitized filenames
   │
   ▼
Per-request temporary host workspace
   │
   ▼
Shared scanner + natural part ordering
   │
   ▼
Shared PdfMergeEngine or DocxMergeEngine
   │
   ▼
Download response
   │
   ▼
Temporary workspace cleanup after response/error
```

This route is useful for responsive cross-platform access but does not create a reusable project JSON, project report bundle, publication transaction journal, or native mobile document engine. Those are separate workflows/capabilities.

## Domain states

`MergeState` models the full project/desktop/CLI workflow state:

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

Desktop recovery/checkpoint UX can use this state, but filesystem/source validation remains authoritative after a restart. The focused web request does not masquerade as this full persistent project state machine.

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

The browser endpoint additionally refuses a request that mixes PDF and DOCX uploads, and the shared scanner/engines still retain their format-specific validation responsibilities.

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

Browser delivery does not change this fidelity boundary; it calls the same maintained engines rather than introducing a hidden mobile/browser fidelity mode.

## Source-integrity boundary

Discovery hashes sources. A full project run snapshots hashes for PDF, DOCX, and companion material and verifies them again before final promotion.

If a tracked file changes during a long merge, the operation fails rather than publishing a bundle assembled from inconsistent source versions.

A browser request first copies uploaded bytes into an isolated temporary workspace. Its correctness boundary is the uploaded request snapshot, not a reusable source-tree/project revision contract.

## Companion-code boundary

Companion archives never enter the PDF/DOCX engines.

The project service can:

- hash them;
- track them for source-integrity changes;
- create companion index evidence.

It does not extract, build, refactor, or merge their contents.

The browser merge route accepts only `.pdf` and `.docx`; it does not accept or process companion archives.

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

The browser route does not publish into a user-selected project output directory. It returns one temporary generated document as a download and removes the request workspace after completion/error; therefore it does not use or claim the full publication transaction/recovery model.

## Storage boundary

The full project storage layer performs two independent checks:

1. output writeability probe;
2. free-space estimate.

This prevents a merge from doing expensive document work only to discover that the destination cannot create transaction files.

Browser mode instead uses host temporary storage and enforces a configurable total upload-byte limit. Host operators remain responsible for sizing/protecting the underlying temporary filesystem.

## Reporting boundary

Reports are generated before final project transaction promotion so they remain consistent with the manuscript outputs.

Generic project evidence includes:

- companion index;
- Markdown/HTML merge report;
- JSON manifest;
- SHA-256 checksums when enabled;
- publishing checklist.

The focused browser route returns the merged document only; it does not silently claim the full project evidence bundle.

## Desktop UI architecture

The PySide6 UI uses workers/progress callbacks for long-running operations. It exposes application services rather than owning a second copy of merge logic.

Accessibility metadata is treated as implementation state and checked through `scripts/check_accessibility.py` in cross-platform Build Smoke.

## CLI architecture

The CLI is an `argparse` front end with document, project, synchronization, recovery, audit/compare, fidelity, and preset commands including:

- `validate`;
- `pdf`;
- `docx`;
- `sql-preset`;
- `project-create`;
- `project-sync`;
- `merge`;
- `recover-output`;
- `audit`;
- `compare`;
- fidelity capability/round-trip/corpus surfaces documented in the CLI reference.

JSON is used for machine-readable validation/preflight/recovery/audit/compare/project-maintenance evidence where appropriate.

## Web architecture

`docmergeforge-web` is a separate console entry point so browser dependencies and network behavior remain explicit.

Safety defaults and boundaries:

- default bind is `127.0.0.1`;
- a non-loopback bind requires an access token;
- browser tokens are entered in a password field or bootstrapped through a `#token=...` fragment rather than an HTTP query parameter;
- token comparison uses `secrets.compare_digest`;
- the browser sends the token in `X-DocMergeForge-Token` for merge requests;
- browser upload/output names are sanitized before filesystem use;
- request workspaces are isolated under temporary storage and cleaned after success/error;
- upload handles close on validation/size failure paths;
- unexpected engine exceptions remain in host logs and are not reflected verbatim to remote clients;
- browser-shell security headers constrain framing/referrer/content loading/permissions;
- access-token authentication is not transport encryption.

Plain HTTP should stay on loopback or a trusted LAN. Internet/untrusted-network deployment requires HTTPS plus a deliberately configured reverse proxy/authentication/request-limit/host-hardening boundary; the built-in server is not represented as a public-Internet production deployment.

See [Platform Support](platform-support.md) and [Security Model](security.md).

## Platform capability architecture

`docmergeforge.platforms.support_matrix()` is the programmatic source for maintained delivery claims and `GET /api/platforms` exposes that data to browser/API clients.

The key distinction is delivery form:

- Windows/macOS/Linux can run the native PySide6 desktop UI and CLI and can also use the browser client;
- Android/iOS/iPadOS/ChromeOS/other modern browser platforms use the responsive browser client connected to a Python host;
- browser support is not relabeled as a native APK/AAB/IPA package.

## Packaging architecture

`scripts/build_desktop.py` delegates PyInstaller arguments to `docmergeforge.packaging.desktop`.

This shared configuration is used/tested consistently across local builds and GitHub Actions.

The current packaging pipeline is an unsigned development-build foundation for native desktop targets, not the signing/notarization layer and not a mobile-package builder.

## Testing architecture

Quality is layered:

- unit tests;
- integration tests including real generated PDF/DOCX browser merge requests;
- generated regression fixtures;
- 120-Part Regression workflow;
- cross-platform Build Smoke, including web entry-point smoke on supported desktop runners;
- CodeQL security analysis;
- manual Stress Acceptance;
- Package Desktop workflow;
- representative manual browser/device acceptance;
- human release acceptance.

Each layer proves a different property; no single green workflow is treated as complete production certification. Automated FastAPI tests do not become evidence that every Android/iOS/browser version has been manually accepted.

## Extension guidelines

When adding a new feature:

- keep user-interface/network-adapter code out of core merge engines;
- add shared behavior to application/domain/engine services so surfaces do not create contradictory document logic;
- preserve source immutability and explicit network trust boundaries;
- keep format-specific logic inside the relevant engine;
- stage new full-project publication evidence inside the same transaction when it must be coherent with outputs;
- keep focused web-request temporary output separate from persistent project publication semantics;
- add recovery behavior/tests for any new persistent final-path mutation;
- update project schema conservatively;
- add diagnostics without reflecting sensitive internals to remote clients;
- extend platform/security/CI/acceptance documentation when a new OS, browser, network, or external-tool boundary is introduced.
