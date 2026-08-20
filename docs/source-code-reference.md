# Source Code Reference

This page documents the runtime Python package under `src/docmergeforge/` by responsibility, dependency direction, important contracts, and maintenance expectations. For a literal every-file inventory, see [Complete Repository File Reference](repository-reference.md).

## Package entry points

`src/docmergeforge/__init__.py` exposes package metadata, while `src/docmergeforge/__main__.py` provides the `python -m docmergeforge` path. `src/docmergeforge/py.typed` marks the installed distribution as typed under PEP 561. The executable entry points declared in `pyproject.toml` are `docmergeforge` for the CLI, `docmergeforge-gui` for the synchronization-enabled desktop UI, and `docmergeforge-web` for the responsive browser host.

## Architectural dependency direction

The intended dependency flow is broadly:

1. Desktop UI, CLI, and web layers collect user intent.
2. Application services coordinate workflows where the full project/publication pipeline is required.
3. Discovery, ordering, validation, project persistence, and settings provide domain services.
4. PDF/DOCX engines perform format-specific work.
5. Utility modules provide filesystem, hashing, naming, locking, and transactional publication primitives.
6. Reports and diagnostics turn operation state into reviewable evidence.

Low-level utility modules should not depend on the desktop UI or web layer. Engine code should not require a GUI or HTTP server. CLI/desktop layers may depend on application services, while the focused web merge surface may compose the shared discovery and document engines directly inside a per-request temporary workspace. Core merge safety should remain independently testable.

## `app` — workflow orchestration

### `app/service.py`

The primary application facade. It coordinates source discovery, validation, ordering, document-engine selection, output naming, output transactions, reporting, and recovery-facing behavior. This module is the main place where separate safety contracts become one user-visible merge operation.

Maintenance expectations:

- keep format separation explicit;
- do not bypass preflight or validation to make a merge appear successful;
- publish final artifacts only through the maintained transactional/atomic paths;
- propagate structured failures that CLI/UI layers can present without losing diagnostics.

### `app/preflight.py`

Builds the readiness decision before a merge starts. Preflight is expected to catch invalid source sets, unsafe output conditions, range problems, unsupported inputs, and other failures before expensive or destructive work begins.

### `app/state_machine.py`

Defines the merge lifecycle/state-transition contract. UI and orchestration code should use valid transitions rather than inventing ad-hoc progress states.

### `app/companion_archive.py`

Creates companion-code archives separately from manuscript outputs. It exists to preserve the central rule that code/material attachments are not silently merged into PDF or DOCX manuscripts.

## `core` — shared domain contracts

### `core/models.py`

Contains shared enums, dataclasses, and value objects used across discovery, validation, engines, projects, reports, and UI layers. Changes here can have repository-wide effects and should be accompanied by typing and regression review.

### `core/exceptions.py`

Defines project-specific exception classes so callers can distinguish expected validation/workflow failures from programming errors.

### `core/part_range.py`

Centralizes parsing and validation for expected numbered-part ranges. The maintained contract caps individual part numbers at 999,999 and range spans at 10,000 parts. Consumers should use this shared contract rather than duplicating range logic.

## `discovery` — source scanning and part detection

### `discovery/part_detection.py`

Extracts supported numbered part/chapter identifiers from filenames and provides the numeric key used by ordering and expected-range checks.

### `discovery/scanner.py`

Recursively scans source trees, prunes excluded directories, filters unsupported/non-regular entries, deduplicates path identities, classifies supported source types, and returns candidates for later validation/order logic.

The scanner is a security and correctness boundary: symlinks, generated output trees, duplicate identities, and non-file entries should not be treated as ordinary source documents without explicit design changes.

## `ordering` — deterministic and manual ordering

### `ordering/editor.py`

Implements order-list operations used when automatic numeric ordering needs review or deliberate manual adjustment. The module should preserve explicit user intent while preventing invalid indices, duplicates, or silent file loss.

## `validation` — input/output correctness

### `validation/service.py`

High-level validation coordinator. It checks source collections and generated artifacts and translates lower-level findings into operation-ready validation results.

### `validation/ooxml.py`

Inspects DOCX/OOXML package structure and risk indicators. It supports the fidelity model by identifying relationships/features that may not be safely preserved by every adapter.

### `validation/compare.py`

Compares source/output evidence and is used by audit/acceptance paths to detect unexpected structural or content changes.

## `pdf` — PDF processing

### `pdf/engine.py`

Implements PDF merging and output verification. Responsibilities include encrypted-input integration, page-level merge behavior, metadata/structure checks, and safe output creation.

### `pdf/passwords.py`

Provides the in-memory password provider/cache used for encrypted PDFs. Password values are intentionally not project-persisted by the normal application path.

### `pdf/rendering.py`

Provides rendering/sampling helpers used when acceptance needs more than parser-level success. Rendering evidence is supplementary to structural validation rather than a replacement for it.

## `docx` — DOCX processing and fidelity adapters

### `docx/engine.py`

Coordinates portable DOCX merging and fidelity adapter selection. It is responsible for choosing a supported path rather than representing an unavailable or unverified native path as production-ready.

### `docx/native.py`

Portable OOXML/DOCX merge implementation used for normal production-enabled DOCX operation. It is the broadly available path but still has documented fidelity limits for advanced Word features.

### `docx/analysis.py`

Extracts structural/content characteristics used by diagnostics, validation, and acceptance comparisons.

### `docx/publication.py`

Adds publication-level features such as title/closing material or page-number-related adjustments where supported by the portable engine.

### `docx/section_evidence.py`

Collects and compares section/page-layout evidence. This is especially important for native-office acceptance, where a document opening successfully is not sufficient proof of layout fidelity.

### `docx/fidelity.py`

Defines fidelity capability/profile metadata and adapter-readiness distinctions. Availability, acceptance-prototype readiness, and production readiness are intentionally separate concepts.

### `docx/fidelity_acceptance.py`

Runs maintained fidelity acceptance logic and produces evidence suitable for CI/operator review.

### `docx/fidelity_corpus.py`

Defines corpus/evidence handling for representative private DOCX fixtures without requiring those sensitive fixtures to be committed to the public repository.

### `docx/legacy.py`

Handles the legacy `.doc` boundary and conversion expectations. Legacy binary Word documents are not treated as equivalent to native DOCX input without an explicit conversion path.

### `docx/libreoffice.py`

Discovers LibreOffice availability and supports the maintained one-document round-trip/adapter surface.

### `docx/libreoffice_uno_merge.py`

Implements the supervised LibreOffice UNO multi-document merge prototype. It isolates profiles, supervises spawned processes/process groups, records evidence, and treats cleanup as part of correctness.

### `docx/libreoffice_uno_acceptance.py`

Evaluates the LibreOffice native prototype against maintained structural, revision, process, and acceptance requirements. Production readiness remains disabled until the broader documented acceptance matrix is complete.

### `docx/word.py`

Discovers Microsoft Word automation availability and exposes the controlled adapter boundary.

### `docx/word_merge.py`

Implements controlled native Microsoft Word multi-document automation for dedicated acceptance environments. It should not be used to imply portable cross-platform support.

### `docx/word_process.py`

Owns Word process supervision, timeout handling, and cleanup safeguards.

### `docx/word_merge_acceptance.py`

Builds and validates Word-native merge evidence, including section/page-number/source-revision/process-cleanup expectations. Production readiness remains disabled until controlled real-Word evidence and human acceptance are complete.

## `project` — reusable project state

### `project/store.py`

Loads, validates, and saves JSON project files. Persistence rejects project destinations addressed through symbolic links, validates project/range structure, and uses the maintained atomic text-save semantics. It also provides exact SHA-256 content-revision tokens, same-snapshot project/revision loading, and guarded saves that refuse an existing project file whose bytes changed after it was opened. These revision checks are optimistic stale-write protection, not a universal multi-process lock.

### `project/selection.py`

Normalizes selected source paths, validates containment/identity, prevents aliases/duplicates, and preserves platform-aware case behavior.

### `project/recovery.py`

Stores durable recovery checkpoints/snapshots. Checkpoint state should only advance after persistence succeeds.

### `project/discovery.py`

Discovers the current raw source tree for synchronization planning without first constraining discovery to the already-persisted `selected_files` list. The application service uses this shared project-aware discovery path so normal project runs and synchronization share the same nested-output exclusion boundary.

### `project/sync.py`

Builds a typed preview plan containing current/proposed/added/removed/reordered selections and applies reviewed changes through guarded persistence. Same-kind duplicate part numbers block apply, while missing parts remain review evidence rather than a metadata-write prohibition. Changed writes create versioned backups. CLI and desktop apply paths carry the exact project revision captured at load, preserve a separate removal-approval gate, perform exact and semantic stale-state checks, and recheck the expected revision before final atomic persistence.

### `project/drift.py`

Provides reusable synchronization-drift evaluation for scripts/CI without requiring mutation.

## `audit` — manuscript/publication inspection

### `audit/document.py`

Produces document-level audit information.

### `audit/publication.py`

Aggregates publication-wide audit findings across source/output artifacts.

### `audit/repetition.py`

Detects repeated content patterns that can reveal accidental duplication across a large multi-part publication.

## `reports` — operation evidence

### `reports/generator.py`

Generates merge/report artifacts from operation state, source evidence, output evidence, warnings, and validation results. Reports are review evidence; they should not claim checks that did not actually run.

## `diagnostics` — supportability

### `diagnostics/logging.py`

Configures application logging and redaction behavior. Diagnostics should provide actionable technical detail without unnecessarily persisting sensitive document contents or passwords.

### `diagnostics/export.py`

Builds support-oriented diagnostic exports from maintained logs/evidence.

### `diagnostics/docs_links.py`

Scans local Markdown links and reports broken repository-relative targets. It powers `scripts/check_docs_links.py` and the Quality workflow.

## `settings` — configuration

### `settings/config.py`

Defines application settings, defaults, persistence, validation, and loading behavior. Settings changes should be mirrored in `docs/settings-reference.md`.

## `profiles` — fidelity profile catalog

### `profiles/catalog.py`

Stores built-in fidelity profiles and profile lookup behavior used by CLI/UI/engine selection.

## `presets` — guided publication presets

### `presets/sql_full_mastery.py`

Defines the SQL Full Mastery 120-part preset used by guided desktop/CLI workflows. Presets should remain explicit conveniences rather than hidden special cases inside general merge logic.

## `companion` — companion-file organization

### `companion/organizer.py`

Classifies and organizes companion/source-code material. Its key contract is separation from manuscript merging.

## `packaging` — executable/release metadata

### `packaging/desktop.py`

Builds the maintained PyInstaller command/configuration used by the desktop build helper. Build-root validation requires the base window, synchronization-enabled desktop entry, synchronization preview dialog, and packaged entry so an incomplete desktop source tree fails preflight before PyInstaller starts.

### `packaging/provenance.py`

Defines build provenance records, artifact hashing, serialization, and verification. Provenance describes what was built; signing/notarization remain separate release gates.

## `utilities` — filesystem safety and reusable primitives

### `utilities/atomic.py`

Provides atomic text/binary publication helpers using temporary files, flush/durability requests, and replace semantics.

### `utilities/output_transaction.py`

Owns multi-artifact staged publication. It creates transaction journals, stages completed artifacts, records promotion state, backs up conflicting outputs where required, promotes final files, and supports explicit interrupted-transaction recovery.

This module is a critical integrity boundary. Journal parsing, child paths, symlinks, duplicate targets, checksums, promotion ordering, and rollback behavior should remain fail-closed.

### `utilities/output_lock.py`

Coordinates an output-directory lock and defends the lock path against unsafe symlink substitution.

### `utilities/output_naming.py`

Constructs safe output names, version suffixes, and reserved-name protections. Windows device-name rules are enforced even when names include suffixes/extensions.

### `utilities/filename_template.py`

Validates and renders user-facing filename templates.

### `utilities/hashing.py`

Provides file hashing used for source identity, provenance, and transactional evidence.

### `utilities/storage.py`

Provides storage/free-space/writeability checks. The maintained output probe performs an actual flushed write rather than treating empty-file creation alone as sufficient evidence.

## `platforms.py` — maintained platform capability matrix

Defines the repository's canonical runtime/delivery support descriptions for Windows, macOS, Linux, Android, iOS/iPadOS, ChromeOS/browser access, and the current host runtime. The matrix deliberately distinguishes native desktop/CLI capability from responsive browser access so documentation and API responses do not overclaim native mobile packaging.

Changes to platform claims should be reflected in `docs/platform-support.md`, installation guidance, tests, and release documentation where applicable.

## `web` — responsive browser host and API

### `web/app.py`

Creates the FastAPI browser application and focused PDF/DOCX merge API. It owns the responsive HTML/PWA shell, platform and health endpoints, upload validation, filename sanitization, natural upload ordering, per-request temporary workspace, shared-password encrypted-PDF handoff, download response, and workspace cleanup.

Security-sensitive contracts include:

- the merge API validates the configured `X-DocMergeForge-Token` using constant-time comparison;
- LAN tokens are entered in a password field or bootstrapped from a `#token=...` fragment rather than request query parameters;
- the page keeps the token only in tab-scoped session storage;
- upload handles close on both successful and failed save paths;
- unexpected engine exceptions are recorded in host logs but returned to remote clients as a generic error;
- the browser shell applies content-security, anti-framing, referrer, content-type, and permissions headers;
- temporary workspaces are removed after handled failures and after successful response completion.

The web path deliberately reuses `PdfMergeEngine`, `DocxMergeEngine`, discovery, and platform capability code rather than maintaining separate browser-only document algorithms.

### `web/main.py`

Implements the `docmergeforge-web` command. It defaults to loopback, validates host/port/upload limits, refuses a non-loopback bind without a token, supports `--token auto`, constructs the FastAPI app, and launches Uvicorn. Token-enabled startup guidance directs users to the browser LAN-token field or fragment handoff and explicitly warns against query-string tokens.

### `web/__init__.py`

Defines the web package surface without eagerly starting the server.

## `ui` — PySide6 desktop application

### `ui/main.py`

Creates the established base desktop window and connects project creation/resume, merge, workers, dialogs, progress state, recent projects, and output/report presentation. Existing-project resume loads the project and exact content revision together and refuses to overwrite a project changed on disk while the user reviews ordering. Direct desktop project-save and recovery-checkpoint failures are surfaced to the user and stop the affected workflow.

### `ui/desktop_entry.py`

Provides the maintained `docmergeforge-gui` startup and `ProjectSyncMainWindow` extension. The extension adds **Synchronize Project Sources** without duplicating `project.sync` logic: it loads a project/revision snapshot, builds the shared synchronization plan, opens the review dialog, refuses ambiguous duplicate-part proposals, requires a second explicit confirmation for removals, carries the exact revision into `apply_project_sync(...)`, records successful metadata maintenance in recent-project history, and surfaces stale/write failures instead of silently retrying.

### `ui/project_sync_dialog.py`

Provides the accessible read-only desktop synchronization preview. It displays current/proposed counts, added/removed paths, proposed order, reordering state, duplicate/missing part evidence, and the metadata-only safety boundary. The Apply button is enabled only for a changed unambiguous proposal; removals are not authorized by this dialog alone and require the separate confirmation in `desktop_entry.py`.

### `ui/dialogs.py`

Shared dialogs for application options, results, errors, diagnostics, and supporting workflows.

### `ui/source_picker.py`

Source selection surface for choosing publication folders/files.

### `ui/order_dialog.py`

Manual ordering/selection review UI with keyboard/accessibility considerations.

### `ui/dry_run_dialog.py`

Presents dry-run/preflight findings before mutation/merge execution.

### `ui/sql_wizard.py`

Guided creation/configuration of the SQL Full Mastery preset workflow.

### `ui/pdf_passwords.py`

Bridges encrypted-PDF password prompts to the in-memory password provider.

### `ui/recent.py`

Stores and presents recently used project references.

### `ui/first_run.py`

First-run onboarding/notice behavior.

### `ui/about_dialog.py`

Project attribution/version/about UI.

### `ui/support_dialog.py`

Support and diagnostic guidance UI.

### `ui/resources.py`

Locates branding/resources correctly both from source and packaged applications.

### `ui/paths.py`

Resolves platform-appropriate application data/config/log paths.

### `ui/theme.py`

Applies maintained desktop theme/palette behavior.

### `ui/workers.py`

Runs long operations away from the UI thread and communicates completion/failure/progress back to the desktop layer.

### `ui/packaged_entry.py`

Provides packaged-application startup behavior and diagnostics that differ from normal source execution. Normal packaged startup delegates to the synchronization-enabled desktop entry, and packaged smoke instantiates the same extended window before exercising the real temporary PDF/DOCX publication smoke.

## Change checklist for runtime modules

When changing runtime code, review all of the following before claiming the change complete:

1. matching unit/integration/regression tests;
2. public CLI, desktop, or web behavior;
3. failure/rollback/cleanup behavior;
4. logging, authentication, and privacy implications;
5. docs for the affected subsystem;
6. the maintained repository-reference corpus if files are added/renamed/deleted;
7. `what_changed.md` for the current development pass;
8. release-evidence documents only when real acceptance evidence exists.
