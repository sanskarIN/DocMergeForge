# Source Code Reference

This page documents the runtime Python package under `src/docmergeforge/` by responsibility, dependency direction, important contracts, and maintenance expectations. For a literal every-file inventory, see [Complete Repository File Reference](repository-reference.md).

## Package entry points

`src/docmergeforge/__init__.py` exposes package metadata, while `src/docmergeforge/__main__.py` provides the `python -m docmergeforge` path. `src/docmergeforge/py.typed` marks the installed distribution as typed under PEP 561. The executable entry points declared in `pyproject.toml` are `docmergeforge` for the CLI and `docmergeforge-gui` for the desktop UI.

## Architectural dependency direction

The intended dependency flow is broadly:

1. UI and CLI collect user intent.
2. Application services coordinate workflows.
3. Discovery, ordering, validation, project persistence, and settings provide domain services.
4. PDF/DOCX engines perform format-specific work.
5. Utility modules provide filesystem, hashing, naming, locking, and transactional publication primitives.
6. Reports and diagnostics turn operation state into reviewable evidence.

Low-level utility modules should not depend on the desktop UI. Engine code should not require a GUI. CLI/desktop layers may depend on application services, but core merge safety should remain independently testable.

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

Loads, validates, migrates, and saves versioned JSON project files. Persistence is designed to fail closed for invalid schema/range/path conditions and to use maintained atomic text-save semantics.

### `project/selection.py`

Normalizes selected source paths, validates containment/identity, prevents aliases/duplicates, and preserves platform-aware case behavior.

### `project/recovery.py`

Stores durable recovery checkpoints/snapshots. Checkpoint state should only advance after persistence succeeds.

### `project/discovery.py`

Discovers the current raw source tree for synchronization planning without first constraining discovery to the already-persisted `selected_files` list.

### `project/sync.py`

Builds a typed preview plan containing current/proposed/added/removed/reordered selections and applies reviewed changes through guarded persistence. Removals require a second explicit approval and changed writes create versioned backups.

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

Builds the maintained PyInstaller command/configuration used by the desktop build helper.

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

## `ui` — PySide6 desktop application

### `ui/main.py`

Creates the main desktop window and connects user actions to application workflows, workers, dialogs, progress state, recent projects, and output/report presentation.

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

Provides packaged-application startup behavior and diagnostics that differ from normal source execution.

## Change checklist for runtime modules

When changing runtime code, review all of the following before claiming the change complete:

1. matching unit/integration/regression tests;
2. public CLI or desktop behavior;
3. failure/rollback behavior;
4. logging and privacy implications;
5. docs for the affected subsystem;
6. `docs/repository-reference.md` if files are added/renamed/deleted;
7. `what_changed.md` for the current development pass;
8. release-evidence documents only when real acceptance evidence exists.
