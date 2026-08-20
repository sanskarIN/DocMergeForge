# Test Suite Reference

This document maps the complete maintained test suite to the production behavior it protects. It complements [Testing and CI](testing-and-ci.md), which explains how to run tests and how CI is structured, and [Complete Repository File Reference](repository-reference.md), which inventories every tracked file.

## Test philosophy

DocMergeForge uses several evidence layers because document publication, filesystem durability, office automation, packaging, browser access, and desktop behavior have different failure modes.

- **Unit tests** isolate deterministic functions, models, validation rules, filesystem safety primitives, and workflow decisions.
- **Integration tests** exercise multiple production components or executable/script surfaces together.
- **Regression tests** preserve known high-value scenarios that are larger or specifically tied to previous risk areas.
- **Acceptance scripts/workflows** cover environment-dependent behavior such as real office processes, packaging, storage failures, and stress measurements.
- **Human acceptance** remains required where automation cannot prove visual fidelity, accessibility, clean-machine usability, signing/notarization experience, browser/device interoperability, or real-world office compatibility.

A test file existing in the repository is not the same as a passing result for the current commit. Release evidence must refer to actual runs.

## Shared test helper

### `tests/helpers/crash_during_promotion.py`

A subprocess helper that intentionally interrupts a publication transaction during promotion. Recovery tests use a separate process because an abrupt process exit cannot be modeled faithfully by simply raising a normal Python exception inside the same test process.

## Integration suite

### Build and packaging integration

- `tests/integration/test_build_desktop_script.py` — verifies the maintained desktop build script entry point and its interaction with packaging helpers.
- `tests/integration/test_build_provenance_cli.py` — exercises build-provenance generation through its command/script surface.
- `tests/integration/test_packaged_entry_smoke.py` — checks packaged GUI entry behavior and packaged-runtime resource/startup assumptions. The packaged smoke now instantiates the synchronization-enabled desktop window before running the existing real temporary PDF/DOCX publication smoke.

### Companion and publication integration

- `tests/integration/test_companion_archive.py` — verifies companion/source-code material is archived separately from manuscript outputs.
- `tests/integration/test_docx_merge.py` — end-to-end portable DOCX merge behavior with real generated DOCX fixtures.
- `tests/integration/test_docx_publication_features.py` — verifies publication-level DOCX additions through the integrated engine path.
- `tests/integration/test_pdf_merge.py` — end-to-end PDF merge behavior with real generated PDF fixtures.
- `tests/integration/test_pdf_publication_features.py` — verifies publication-level PDF behavior through the integrated engine path.

### Responsive web integration

- `tests/integration/test_web_app.py` — exercises the FastAPI/browser merge surface with generated PDF/DOCX fixtures. It covers safe cross-platform upload/output names, browser-shell security headers, fragment-based token bootstrap, platform/health endpoints, successful PDF and DOCX merge/download behavior, configured-token enforcement, generic remote failure details, upload-size fail-closed behavior, and mixed-format rejection.

This integration suite proves the Python host/API behavior in the test environment. It does not replace manual acceptance in representative Android, iOS/iPadOS, ChromeOS, and desktop browsers, nor does it prove confidentiality on an untrusted network.

### Recovery and stress integration

- `tests/integration/test_forced_process_recovery.py` — exercises interruption in another process and validates recovery behavior after abnormal termination.
- `tests/integration/test_resource_evidence_runner.py` — verifies the resource-evidence wrapper captures command execution evidence correctly.
- `tests/integration/test_stress_fixture_script.py` — validates stress fixture generation through the maintained script surface.

### DOCX fidelity and LibreOffice integration

- `tests/integration/test_fidelity_acceptance_script.py` — exercises the DOCX fidelity acceptance script as a command surface.
- `tests/integration/test_lo_uno_acceptance_command.py` — verifies LibreOffice UNO acceptance command orchestration and result handling.
- `tests/integration/test_lo_uno_process_group.py` — protects process-group supervision semantics required by LibreOffice timeout/failure cleanup.
- `tests/integration/test_lo_uno_supervised_smoke.py` — integration coverage for the supervised LibreOffice smoke path.

These tests can verify orchestration without automatically proving every external-office fidelity requirement. Real workflow runs and broader acceptance remain distinct evidence.

### Microsoft Word integration

- `tests/integration/test_word_native_merge_acceptance_script.py` — exercises the Word native acceptance script interface.
- `tests/integration/test_word_native_merge_smoke_script.py` — exercises the smaller Word smoke harness interface.
- `tests/integration/test_word_timeout_cleanup_acceptance_script.py` — validates the timeout-cleanup acceptance script contract.

Actual Word automation still requires the controlled Windows/Word environment described in the acceptance documentation.

### Desktop integration and accessibility

- `tests/integration/test_order_dialog_accessibility.py` — checks important accessible/keyboard-facing properties of the ordering dialog using the real Qt widget layer, and protects **Resume Project** persistence ordering so the exact-revision guarded project save occurs before a new recovery checkpoint is written.
- `tests/integration/test_project_sync_desktop.py` — covers the synchronization-enabled desktop action and preview with real offscreen Qt widgets plus controlled workflow doubles. It verifies the accessible home action, complete review preview, disabled apply for ambiguous duplicate parts, separate removal confirmation before persistence, exact project-revision propagation into apply, cancellation without project writes, and stale-write failure surfacing.

Automated widget/workflow assertions do not replace human screen-reader/high-contrast/display-scaling acceptance.

## Regression suite

### `tests/regression/test_120_part_detection.py`

Protects the large numbered-source scenario that motivated the publication workflow. It ensures 120-part discovery/detection behavior remains stable and numerically ordered rather than lexicographically misordered.

### `tests/regression/test_repeated_transaction_recovery.py`

Protects repeated interruption/recovery behavior so recovery itself remains idempotent and does not progressively corrupt transaction state or final outputs.

## Unit suite — filesystem and output safety

### `tests/unit/test_atomic.py`

Protects atomic text/binary publication helpers, including temporary-file cleanup, replace behavior, and write/flush failure handling.

### `tests/unit/test_output_lock.py`

Validates output-directory locking, contention behavior, cleanup, and symlink defenses around the lock path.

### `tests/unit/test_output_naming.py`

Covers generated output names, existing-file version suffixes, invalid/reserved names, and Windows device-name protections.

### `tests/unit/test_output_transaction.py`

Core transaction tests for staging, journaling, backup/promotion, successful commit, failure rollback, and pending transaction discovery.

### `tests/unit/test_output_transaction_hardening.py`

Covers fail-closed transaction journal parsing and recovery validation: unsafe child paths, invalid field types, malformed hashes, duplicate targets, invalid output-folder targets, durability failure paths, and recovery checkpoint ordering.

### `tests/unit/test_output_transaction_locking.py`

Verifies transaction execution cooperates with the output lock so concurrent publication attempts do not silently interleave.

### `tests/unit/test_output_transaction_symlinks.py`

Protects staging/journal/backup/final path handling from unsafe symlink substitution and related path-identity attacks.

### `tests/unit/test_storage.py`

Covers free-space and output-writeability checks, including the maintained real flushed-write probe rather than empty-file creation alone.

### `tests/unit/test_filename_template.py`

Protects filename-template validation and rendering behavior used to construct publication names safely.

## Unit suite — discovery, parts, and ordering

### `tests/unit/test_part_detection.py`

Covers supported filename part/chapter detection, numeric extraction, invalid patterns, and upper boundaries.

### `tests/unit/test_scanner_deduplication.py`

Protects scanner path deduplication so the same source identity is not included multiple times through aliases.

### `tests/unit/test_scanner_exclusions.py`

Covers recursive exclusion pruning, nested output-folder avoidance, non-regular/broken-symlink filtering, supported-extension filtering, and source-tree safety.

### `tests/unit/test_ordering.py`

Protects order-list operations, deterministic ordering behavior, moves, invalid indices, and preservation of selected entries.

### `tests/unit/test_cli_part_ranges.py`

Ensures CLI expected-range parsing uses the shared bounded part-range contract and rejects malformed/unbounded input.

## Unit suite — project persistence and synchronization

### `tests/unit/test_project_selection.py`

Covers explicit selected-file normalization, source containment, duplicate aliases, extension eligibility, and selection validation.

### `tests/unit/test_project_selection_paths.py`

Protects platform-aware path identity, especially case-distinct POSIX paths versus case-normalized platforms.

### `tests/unit/test_project_store.py`

Covers JSON project serialization/deserialization, schema validation, migrations/version handling, range validation, and normal persistence.

### `tests/unit/test_project_store_persistence_guard.py`

Protects failure paths where invalid state or write errors must leave the prior project file intact rather than partially replacing it. It also covers same-snapshot project revision tokens, successful guarded saves, stale exact-content rejection without overwrite, and symbolic-link destination refusal.

### `tests/unit/test_recovery_store.py`

Covers project recovery checkpoint snapshots and the rule that in-memory checkpoint state advances only after durable persistence succeeds.

### `tests/unit/test_project_sync.py`

Covers synchronization proposal ordering, current/proposed/added/removed/reordered evidence, output-folder exclusion, backups, no-op behavior, removal approval, stale-plan rejection, symlink refusal, semantic on-disk drift, and persistence failures.

### `tests/unit/test_project_sync_drift.py`

Protects reusable drift-evaluation logic used by the standalone checker/CI surface.

### `tests/unit/test_cli_project_sync.py`

Covers the CLI's preview/apply semantics, second removal approval, JSON errors, successful synchronization operation, and exact byte-level project drift rejection between the initial snapshot and apply.

### `tests/unit/test_recent_projects.py`

Covers recent-project persistence and retrieval used by the desktop UI.

## Unit suite — application orchestration and state

### `tests/unit/test_service_discovery_safety.py`

Protects application-level source discovery from accidentally including its nested configured output tree or otherwise bypassing scanner safety.

### `tests/unit/test_service_output_transaction.py`

Verifies the application service publishes merge artifacts through the maintained transaction path and handles success/failure evidence correctly.

### `tests/unit/test_state_machine.py`

Covers allowed and rejected merge lifecycle transitions.

### `tests/unit/test_cli_workflow.py`

Tests representative CLI workflow dispatch, arguments, structured results, and exit-code behavior across normal/failure paths. It also protects fail-closed `project-create` persistence errors so a failed save is returned as structured JSON with exit code `2` instead of escaping as an unhandled save exception.

## Unit suite — platform and web host

### `tests/unit/test_platforms.py`

Protects the maintained support matrix and runtime capability serialization so Windows/macOS/Linux native support is not confused with browser-delivered Android/iOS/web access.

### `tests/unit/test_web_main.py`

Covers loopback-host detection and safe `docmergeforge-web` parser defaults, including the loopback bind, port, and upload-size defaults used by the browser host.

## Unit suite — PDF

### `tests/unit/test_encrypted_pdf_validation.py`

Covers encrypted PDF validation and password-provider behavior, including failure when a usable password is unavailable.

PDF end-to-end merge behavior is additionally covered in `tests/integration/test_pdf_merge.py` and publication features in `tests/integration/test_pdf_publication_features.py`.

## Unit suite — DOCX portable engine and analysis

### `tests/unit/test_docx_analysis.py`

Covers DOCX structural/content analysis helpers used by validation and fidelity evidence.

### `tests/unit/test_docx_native.py`

Protects portable OOXML merge primitives and their supported preservation behavior.

### `tests/unit/test_docx_section_evidence.py`

Covers extraction/comparison of sections, page properties, headers/footers-related evidence, and other layout-sensitive facts used by native acceptance.

### `tests/unit/test_legacy_doc.py`

Protects legacy `.doc` detection/conversion boundaries and ensures binary Word input is not silently treated as equivalent to DOCX.

## Unit suite — DOCX fidelity profiles and corpus

### `tests/unit/test_docx_fidelity.py`

Covers fidelity profile/capability metadata and adapter-selection distinctions.

### `tests/unit/test_docx_fidelity_acceptance.py`

Tests acceptance evaluation and evidence decisions for the maintained DOCX fidelity model.

### `tests/unit/test_docx_fidelity_corpus.py`

Covers private corpus manifest parsing, evidence recording, and fixture-selection behavior without committing private corpora.

### `tests/unit/test_profiles.py`

Protects the built-in profile catalog and profile lookup behavior.

### `tests/unit/test_cli_fidelity.py`

Verifies fidelity-related CLI arguments, profile selection, and acceptance command behavior.

## Unit suite — LibreOffice adapters

### `tests/unit/test_docx_libreoffice.py`

Covers LibreOffice discovery/adapter behavior and one-document round-trip boundaries.

### `tests/unit/test_lo_uno_supervised_merge.py`

Protects supervised UNO merge orchestration, isolated profile handling, command/process supervision, failure mapping, and cleanup logic using controlled substitutes where appropriate.

### `tests/unit/test_lo_uno_supervised_acceptance.py`

Covers structural/revision/risk/process evidence evaluation for the supervised UNO acceptance prototype.

### `tests/unit/test_lo_uno_acceptance_workflow.py`

Inspects the maintained GitHub workflow definition so critical acceptance steps/guards are not accidentally removed without a test change.

Real LibreOffice workflow results remain the authoritative evidence for actual UNO execution.

## Unit suite — Microsoft Word adapters

### `tests/unit/test_docx_word.py`

Covers Word adapter discovery/round-trip behavior and availability boundaries.

### `tests/unit/test_docx_word_merge.py`

Protects native Word merge automation logic, document sequencing, timeout/failure behavior, and controlled COM/application integration through test doubles where required.

### `tests/unit/test_docx_word_merge_acceptance.py`

Covers Word acceptance evidence evaluation and maintained readiness gates.

### `tests/unit/test_docx_word_merge_cleanup_failure.py`

Ensures cleanup failures are not silently hidden after Word automation and produce actionable failure evidence.

### `tests/unit/test_docx_word_merge_page_number_acceptance.py`

Protects page-number/section acceptance rules that are easy to regress when using native Word insertion/section operations.

### `tests/unit/test_docx_word_process.py`

Covers process discovery, supervision, timeout, owned-process cleanup, and safeguards against indiscriminate process termination.

### `tests/unit/test_word_acceptance_environment_script.py`

Checks the PowerShell environment-report script retains required evidence fields/commands.

### `tests/unit/test_word_process_state_script.py`

Protects the PowerShell process-state evidence script contract.

### `tests/unit/test_word_native_acceptance_workflow.py`

Inspects the controlled Word GitHub workflow so expected normal-merge and timeout-cleanup safeguards remain present.

Real Word execution and human fidelity review remain separate acceptance evidence.

## Unit suite — validation and audit

### `tests/unit/test_validation.py`

Covers high-level validation behavior, expected parts, mixed/invalid inputs, generated outputs, and validation result composition.

### `tests/unit/test_ooxml_validation.py`

Covers DOCX/OOXML ZIP/package structural validation and malformed-package handling.

### `tests/unit/test_ooxml_risk.py`

Covers detection/classification of advanced OOXML features that may require stronger fidelity handling or warnings.

### `tests/unit/test_audit.py`

Provides baseline publication audit tests.

### `tests/unit/test_document_audit.py`

Covers document-level audit extraction/details.

### `tests/unit/test_repetition_audit.py`

Protects repeated-content detection and reporting behavior.

## Unit suite — diagnostics, documentation, and repository integrity

### `tests/unit/test_diagnostics_logging.py`

Covers logging initialization, redaction, safe path/content handling, and diagnostic behavior.

### `tests/unit/test_diagnostics_export.py`

Covers diagnostic bundle/export creation.

### `tests/unit/test_docs_links.py`

Tests local Markdown link extraction/resolution and broken-link detection used by the documentation link checker.

### `tests/unit/test_repository_reference.py`

Tests the repository-reference coverage checker, including exact backticked-path matching, missing-file reporting, and command exit behavior.

### `tests/unit/test_version_metadata.py`

Ensures package/runtime version metadata stays internally consistent and pins the maintained public CLI, desktop, and web console-script entry targets.

## Unit suite — settings, UI resources, and build metadata

### `tests/unit/test_settings.py`

Covers default settings, serialization/deserialization, validation, and persistence behavior.

### `tests/unit/test_ui_resources.py`

Protects resource lookup for both source-tree and packaged desktop execution.

### `tests/unit/test_build_desktop.py`

Covers packaging command construction and build-root validation without requiring every unit-test run to build an executable. The build-root tests require `main.py`, the synchronization-enabled desktop entry, the synchronization preview dialog, and the packaged entry so packaging preflight cannot accept an incomplete desktop source tree.

### `tests/unit/test_build_provenance.py`

Covers provenance manifest generation, hashing, serialization, and verification.

## Unit suite — companion-code separation

### `tests/unit/test_code_separation.py`

Protects the repository-level rule that source/companion code is not merged into manuscript PDF/DOCX output.

### `tests/unit/test_companion_organizer.py`

Covers companion-file classification and organization behavior.

## How to choose where a new test belongs

Use **unit** when the behavior can be proven deterministically inside one process with controlled filesystem/test doubles. Use **integration** when the important contract crosses production modules, HTTP surfaces, scripts, Qt widgets, subprocesses, or actual document libraries. Use **regression** when a larger/high-value scenario should remain permanently protected because its failure would recreate a known class of problem. Use an **acceptance workflow** when the property depends on an external office application, packaging runtime, OS process behavior, browser/device environment, storage conditions, or measured resources.

## Required coverage when adding behavior

A feature is not considered well-tested merely because one happy-path test exists. Review the relevant set:

1. normal success;
2. malformed/unsupported input;
3. boundary values;
4. filesystem/process failures where applicable;
5. rollback/recovery/cleanup behavior for writes and temporary resources;
6. platform-specific path behavior where relevant;
7. privacy/logging/authentication behavior for sensitive values;
8. CLI/UI/web error propagation;
9. documentation of limitations and trust boundaries;
10. environment-dependent acceptance when the feature relies on external applications or browser/device behavior.

## Running the suite

The normal development commands are documented in [Testing and CI](testing-and-ci.md). The primary Quality workflow runs the full pytest suite with coverage after lint, format, typing, and documentation-integrity checks. Environment-dependent acceptance workflows remain separately controlled so a portable unit-test pass is never confused with external-office, browser-device, or release readiness.
