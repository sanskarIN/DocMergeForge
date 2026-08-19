# Complete Repository File Reference

This page is the repository-wide inventory for DocMergeForge. It documents the role of every tracked file in the project, including source modules, tests, automation, documentation, configuration, and branding assets. The companion coverage check in `scripts/check_repository_reference.py` is intended to keep this inventory synchronized with future tracked files.

## Reading this reference

- **Runtime** files under `src/docmergeforge/` implement application behavior.
- **Automation** files under `scripts/` and `.github/workflows/` provide repeatable checks, acceptance harnesses, builds, and release evidence.
- **Tests** under `tests/` define unit, integration, and regression contracts.
- **Documentation** under `docs/` explains supported behavior, limitations, operations, development, packaging, and release gates.
- **Repository metadata** at the root and under `.github/` controls packaging, contribution, CI, security, and project governance.
- **Branding** under `assets/branding/` contains reusable project artwork.

## Repository root

- `.editorconfig` — shared editor defaults for consistent text formatting across IDEs.
- `.gitattributes` — Git text/binary and line-ending behavior.
- `.gitignore` — excludes local environments, caches, build outputs, temporary artifacts, and other generated files.
- `.pre-commit-config.yaml` — local pre-commit hook configuration used before changes are committed.
- `CHANGELOG.md` — chronological user/developer-facing record of notable repository changes.
- `CODE_OF_CONDUCT.md` — community participation expectations and enforcement guidance.
- `CONTRIBUTING.md` — contributor setup, coding, testing, documentation, and pull-request expectations.
- `LICENSE` — MIT license text for the repository.
- `PROJECT_STATE.md` — compact continuation checkpoint describing current implementation and remaining release gates.
- `README.md` — primary public project overview, install/use entry points, feature boundaries, and documentation links.
- `SECURITY.md` — vulnerability reporting policy, supported scope, and security-response guidance.
- `THIRD_PARTY_NOTICES.md` — dependency attribution and third-party licensing notes.
- `pyproject.toml` — Python package metadata, dependencies, console entry points, build backend, pytest settings, Ruff, Black, and strict mypy configuration.
- `what_changed.md` — current development-pass ledger and verification caveats.

## GitHub repository metadata

- `.github/CODEOWNERS` — default ownership/review routing for repository paths.
- `.github/FUNDING.yml` — funding metadata for GitHub's sponsor/funding surface.
- `.github/ISSUE_TEMPLATE/bug_report.yml` — structured bug report form.
- `.github/ISSUE_TEMPLATE/config.yml` — issue-template chooser configuration and support links.
- `.github/ISSUE_TEMPLATE/feature_request.yml` — structured feature request form.
- `.github/PULL_REQUEST_TEMPLATE.md` — pull-request checklist covering scope, tests, docs, and safety evidence.
- `.github/SUPPORT.md` — GitHub-facing support-routing note.
- `.github/dependabot.yml` — automated dependency-update configuration.

## GitHub Actions workflows

- `.github/workflows/build-smoke.yml` — verifies desktop build tooling can produce expected development artifacts.
- `.github/workflows/disk-full-acceptance.yml` — exercises disk-full/output failure behavior and recovery expectations.
- `.github/workflows/fidelity-acceptance.yml` — runs maintained DOCX fidelity acceptance checks.
- `.github/workflows/libreoffice-uno-acceptance.yml` — supervised LibreOffice UNO native multi-document acceptance lane.
- `.github/workflows/libreoffice-uno-process-cleanup.yml` — validates supervised LibreOffice process-group cleanup behavior.
- `.github/workflows/onefile-acceptance.yml` — builds and tests PyInstaller one-file application behavior.
- `.github/workflows/package.yml` — desktop packaging, artifact metadata, SBOM/provenance, and packaging verification workflow.
- `.github/workflows/project-sync-safety.yml` — cross-platform project-synchronization safety regression lane.
- `.github/workflows/quality.yml` — primary lint, format, type, documentation, and pytest quality matrix.
- `.github/workflows/recovery-acceptance.yml` — recovery and interrupted-publication acceptance checks.
- `.github/workflows/regression.yml` — larger regression coverage, including 120-part publication scenarios.
- `.github/workflows/security.yml` — security-oriented automated analysis.
- `.github/workflows/stress.yml` — manually controlled stress-testing workflow with resource evidence.
- `.github/workflows/word-native-acceptance.yml` — controlled self-hosted Microsoft Word native merge and timeout-cleanup acceptance lane.

## Branding assets

- `assets/branding/bmc-support-card.svg` — Buy Me a Coffee support card artwork.
- `assets/branding/logo.svg` — reusable DocMergeForge logo artwork.
- `assets/branding/readme-banner.svg` — wide README/header banner.
- `assets/branding/social-preview.svg` — social/repository preview artwork.
- `assets/branding/splash.svg` — splash-screen artwork for packaged desktop presentation.

## Documentation entry points and concepts

- `docs/README.md` — canonical documentation portal and accuracy policy.
- `docs/accessibility.md` — accessibility goals, implemented keyboard/UI behavior, automated checks, and remaining human acceptance.
- `docs/architecture.md` — system layers, data flow, safety boundaries, and component responsibilities.
- `docs/audit-and-compare.md` — source/output audit behavior, repetition checks, and comparison workflows.
- `docs/building-executables.md` — executable-building overview and pointers to platform-specific build material.
- `docs/cli-reference.md` — complete command-line interface reference.
- `docs/companion-code.md` — companion/source-code archive handling and the rule that code archives are not merged into manuscripts.
- `docs/desktop-guide.md` — end-user desktop workflow guide.
- `docs/development-phases.md` — implemented phases, outstanding work, and release-gate progression.
- `docs/development.md` — developer setup, project structure, coding standards, and common development commands.
- `docs/diagnostics.md` — logs, diagnostic export, redaction, and support evidence.
- `docs/discovery-and-ordering.md` — file discovery, numbered-part detection, exclusions, deduplication, and ordering behavior.
- `docs/docx-engine.md` — DOCX merge engine behavior, adapter selection, preservation boundaries, and validation.
- `docs/docx-fidelity-acceptance.md` — adapter fidelity model and acceptance requirements.
- `docs/docx-fidelity-corpus.md` — private/representative corpus acceptance process.
- `docs/faq.md` — frequently asked operational and capability questions.
- `docs/getting-started.md` — first successful merge walkthrough.
- `docs/glossary.md` — project-specific terminology.
- `docs/installation.md` — source installation, runtime requirements, and environment preparation.
- `docs/known-limitations.md` — explicit unsupported, conditional, and not-yet-verified behavior.
- `docs/libreoffice-native-merge-acceptance.md` — LibreOffice UNO prototype acceptance details and production-readiness boundaries.
- `docs/merge-pipeline.md` — end-to-end merge stages from discovery through transactional publication and verification.
- `docs/operator-runbook.md` — operational checklist for reliable runs, incident handling, and evidence capture.
- `docs/output-artifacts.md` — generated publication, report, archive, temporary, backup, and evidence artifacts.
- `docs/pdf-engine.md` — PDF merge, encryption/password handling, metadata/page validation, and rendering checks.
- `docs/privacy.md` — local-first data handling, sensitive-data boundaries, and diagnostic privacy.
- `docs/project-files.md` — reusable JSON project schema, persistence rules, validation, and safety boundaries.
- `docs/project-sync-check-script.md` — standalone project-sync drift-check script operation.
- `docs/project-sync-ci.md` — CI strategy for detecting project synchronization drift.
- `docs/project-sync.md` — preview/apply project synchronization workflow and removal approvals.
- `docs/recovery.md` — interrupted transaction detection, journals, backups, rollback, and recovery semantics.
- `docs/release-evidence.md` — evidence ledger for acceptance and release claims.
- `docs/release-packaging.md` — packaging artifacts and release-bundle composition.
- `docs/release-process.md` — release preparation, verification, tagging, and distribution process.
- `docs/security.md` — technical security model, trust boundaries, filesystem safeguards, and local-processing assumptions.
- `docs/settings-reference.md` — persisted/runtime settings reference.
- `docs/sql-full-mastery-preset.md` — SQL Full Mastery 120-part guided preset behavior.
- `docs/stress-testing.md` — large-input and resource-stress methodology and evidence requirements.
- `docs/support.md` — user support routes, useful diagnostics, and issue-reporting guidance.
- `docs/testing-and-ci.md` — test layers, CI workflows, markers, coverage expectations, and acceptance distinctions.
- `docs/troubleshooting.md` — symptom-based troubleshooting and safe corrective actions.
- `docs/validation-and-preflight.md` — input/output validation and preflight checks.
- `docs/word-native-merge-acceptance.md` — Microsoft Word native merge acceptance harness and evidence requirements.
- `docs/word-timeout-cleanup-acceptance.md` — controlled Word timeout/process cleanup acceptance details.
- `docs/repository-reference.md` — this complete tracked-file inventory.
- `docs/documentation-catalog.md` — audience/task-oriented map of the documentation set.
- `docs/source-code-reference.md` — runtime package/module reference.
- `docs/automation-reference.md` — scripts and CI/workflow reference.
- `docs/test-suite-reference.md` — test-suite file-by-file coverage reference.
- `docs/configuration-reference.md` — repository configuration, governance metadata, and branding reference.

## Build documentation

- `docs/build/README.md` — canonical executable-build portal.
- `docs/build/ci-packaging.md` — CI packaging workflow behavior and artifact expectations.
- `docs/build/common.md` — platform-neutral build prerequisites and process.
- `docs/build/linux.md` — Linux build instructions and caveats.
- `docs/build/macos.md` — macOS build instructions and signing/notarization boundaries.
- `docs/build/provenance.md` — provenance manifest contents and verification model.
- `docs/build/release-checklist.md` — executable release build checklist.
- `docs/build/signing-and-notarization.md` — platform signing/notarization procedures and unverified gates.
- `docs/build/troubleshooting.md` — build-specific troubleshooting.
- `docs/build/verification.md` — executable artifact verification procedures.
- `docs/build/windows.md` — Windows build instructions and production-signing boundaries.

## Documentation history

- `docs/history/what_changed-through-2026-08-18.md` — archived detailed development history through 2026-08-18.

## Automation scripts

- `scripts/__init__.py` — marks the scripts directory as an importable package for test reuse.
- `scripts/build_desktop.py` — invokes desktop executable building with the maintained PyInstaller configuration.
- `scripts/check_accessibility.py` — performs automated static accessibility checks against desktop UI code.
- `scripts/check_disk_full_recovery.py` — exercises publication behavior under simulated exhausted-storage conditions.
- `scripts/check_docs_links.py` — validates local Markdown links across repository documentation.
- `scripts/check_docx_fidelity_acceptance.py` — command-line driver for DOCX fidelity acceptance.
- `scripts/check_libreoffice_uno_merge_acceptance.py` — driver for supervised LibreOffice UNO merge acceptance.
- `scripts/check_libreoffice_uno_merge_smoke.py` — focused LibreOffice UNO supervised smoke harness.
- `scripts/check_project_sync.py` — standalone project synchronization drift checker.
- `scripts/check_word_native_merge_acceptance.py` — driver for controlled Word native merge acceptance.
- `scripts/check_word_native_merge_smoke.py` — focused Word native merge smoke harness.
- `scripts/check_word_process_state.ps1` — Windows PowerShell process-state evidence collector for Word acceptance.
- `scripts/check_word_timeout_cleanup_acceptance.py` — validates controlled timeout and cleanup behavior around Word automation.
- `scripts/generate_120_fixture.py` — generates deterministic 120-part synthetic publication fixtures.
- `scripts/generate_stress_fixture.py` — generates configurable stress-test fixture sets.
- `scripts/report_word_acceptance_environment.ps1` — records controlled Word acceptance environment metadata.
- `scripts/run_with_resource_evidence.py` — wraps a command while recording runtime/resource evidence.
- `scripts/write_build_provenance.py` — emits build-provenance metadata for packaged artifacts.
- `scripts/check_repository_reference.py` — verifies every tracked repository file is explicitly named in this reference.

## Runtime package root

- `src/docmergeforge/__init__.py` — package version/public package metadata.
- `src/docmergeforge/__main__.py` — `python -m docmergeforge` entry point.
- `src/docmergeforge/py.typed` — PEP 561 marker declaring the package as typed.

## Application orchestration

- `src/docmergeforge/app/__init__.py` — application-layer package marker.
- `src/docmergeforge/app/companion_archive.py` — builds companion-code archives separately from manuscript publication.
- `src/docmergeforge/app/preflight.py` — preflight validation orchestration and readiness checks.
- `src/docmergeforge/app/service.py` — primary merge application service coordinating discovery, validation, engines, transactional outputs, reports, and recovery-facing behavior.
- `src/docmergeforge/app/state_machine.py` — merge lifecycle/state-transition model.

## Audit subsystem

- `src/docmergeforge/audit/__init__.py` — audit package marker.
- `src/docmergeforge/audit/document.py` — document-level audit extraction/summary logic.
- `src/docmergeforge/audit/publication.py` — publication-level audit composition.
- `src/docmergeforge/audit/repetition.py` — repeated-content detection and reporting support.

## CLI

- `src/docmergeforge/cli/__init__.py` — CLI package marker.
- `src/docmergeforge/cli/main.py` — argument parsing, command dispatch, structured output, project workflows, merge/audit/compare commands, and exit-code handling.

## Companion-code handling

- `src/docmergeforge/companion/__init__.py` — companion package exports.
- `src/docmergeforge/companion/organizer.py` — detects and organizes companion/source-code files without mixing them into PDF/DOCX manuscript merges.

## Core contracts

- `src/docmergeforge/core/__init__.py` — core package marker.
- `src/docmergeforge/core/exceptions.py` — project-specific exception hierarchy.
- `src/docmergeforge/core/models.py` — shared enums/dataclasses/value models used across the application.
- `src/docmergeforge/core/part_range.py` — bounded expected-part-range parsing and validation contract.

## Diagnostics

- `src/docmergeforge/diagnostics/__init__.py` — diagnostics package marker.
- `src/docmergeforge/diagnostics/docs_links.py` — local Markdown link discovery and validation logic.
- `src/docmergeforge/diagnostics/export.py` — diagnostic bundle/export creation.
- `src/docmergeforge/diagnostics/logging.py` — safe logging setup, redaction, and application log handling.

## Discovery

- `src/docmergeforge/discovery/__init__.py` — discovery package marker.
- `src/docmergeforge/discovery/part_detection.py` — numbered part/chapter detection from filenames.
- `src/docmergeforge/discovery/scanner.py` — recursive source scanning, filtering, exclusion pruning, deduplication, and candidate classification.

## DOCX subsystem

- `src/docmergeforge/docx/__init__.py` — DOCX package marker.
- `src/docmergeforge/docx/analysis.py` — DOCX structural/content analysis helpers.
- `src/docmergeforge/docx/engine.py` — portable DOCX merge engine and adapter coordination.
- `src/docmergeforge/docx/fidelity.py` — fidelity profiles/capability metadata and adapter selection contracts.
- `src/docmergeforge/docx/fidelity_acceptance.py` — portable fidelity acceptance evaluation.
- `src/docmergeforge/docx/fidelity_corpus.py` — corpus manifest/evidence handling for representative DOCX acceptance.
- `src/docmergeforge/docx/legacy.py` — legacy `.doc` conversion/integration support boundaries.
- `src/docmergeforge/docx/libreoffice.py` — LibreOffice adapter discovery/round-trip support.
- `src/docmergeforge/docx/libreoffice_uno_acceptance.py` — LibreOffice UNO acceptance evidence model and orchestration.
- `src/docmergeforge/docx/libreoffice_uno_merge.py` — supervised LibreOffice UNO native multi-document merge prototype, isolated profile handling, process supervision, and cleanup.
- `src/docmergeforge/docx/native.py` — portable native OOXML merge primitives.
- `src/docmergeforge/docx/publication.py` — publication-specific DOCX enhancements such as title/closing/page-number behavior.
- `src/docmergeforge/docx/section_evidence.py` — section/page-layout evidence extraction and comparison.
- `src/docmergeforge/docx/word.py` — Microsoft Word adapter availability and round-trip support.
- `src/docmergeforge/docx/word_merge.py` — controlled Microsoft Word native multi-document merge automation.
- `src/docmergeforge/docx/word_merge_acceptance.py` — Word native merge acceptance/evidence orchestration.
- `src/docmergeforge/docx/word_process.py` — Word process supervision, timeout, and cleanup helpers.

## Ordering

- `src/docmergeforge/ordering/__init__.py` — ordering package exports.
- `src/docmergeforge/ordering/editor.py` — source ordering model and safe manual reorder operations.

## Packaging

- `src/docmergeforge/packaging/__init__.py` — packaging package exports.
- `src/docmergeforge/packaging/desktop.py` — maintained desktop-build command construction and packaging helpers.
- `src/docmergeforge/packaging/provenance.py` — build provenance manifest model, hashing, serialization, and verification helpers.

## PDF subsystem

- `src/docmergeforge/pdf/__init__.py` — PDF package marker.
- `src/docmergeforge/pdf/engine.py` — PDF merge engine, encrypted-input handling, metadata/page validation, and output creation.
- `src/docmergeforge/pdf/passwords.py` — in-memory PDF password provider/cache behavior.
- `src/docmergeforge/pdf/rendering.py` — PDF rendering/sampling helpers used for visual/readability validation evidence.

## Presets and profiles

- `src/docmergeforge/presets/__init__.py` — preset package marker.
- `src/docmergeforge/presets/sql_full_mastery.py` — SQL Full Mastery 120-part preset definition and defaults.
- `src/docmergeforge/profiles/__init__.py` — fidelity profile exports.
- `src/docmergeforge/profiles/catalog.py` — built-in fidelity profile catalog and lookup behavior.

## Project persistence and synchronization

- `src/docmergeforge/project/__init__.py` — project package marker.
- `src/docmergeforge/project/discovery.py` — raw current-source discovery used by synchronization planning.
- `src/docmergeforge/project/drift.py` — reusable project-sync drift evaluation.
- `src/docmergeforge/project/recovery.py` — durable project checkpoint/recovery snapshot store.
- `src/docmergeforge/project/selection.py` — explicit selected-file normalization, path validation, duplicate prevention, and selection rules.
- `src/docmergeforge/project/store.py` — versioned JSON project load/save/migration/persistence validation.
- `src/docmergeforge/project/sync.py` — preview-first synchronization planning, diff evidence, approvals, backups, and guarded apply.

## Reports

- `src/docmergeforge/reports/__init__.py` — reports package marker.
- `src/docmergeforge/reports/generator.py` — machine/human-readable merge report generation.

## Settings

- `src/docmergeforge/settings/__init__.py` — settings package marker.
- `src/docmergeforge/settings/config.py` — application settings model, defaults, load/save behavior, and validation.

## Desktop UI

- `src/docmergeforge/ui/__init__.py` — UI package marker.
- `src/docmergeforge/ui/about_dialog.py` — About dialog and project attribution.
- `src/docmergeforge/ui/dialogs.py` — shared desktop dialogs for settings, results, errors, and supporting workflows.
- `src/docmergeforge/ui/dry_run_dialog.py` — dry-run/preflight review dialog.
- `src/docmergeforge/ui/first_run.py` — first-run onboarding/notice flow.
- `src/docmergeforge/ui/main.py` — main PySide6 desktop window, command wiring, workflow state, and application startup.
- `src/docmergeforge/ui/order_dialog.py` — reorder/selection dialog with accessibility-aware controls.
- `src/docmergeforge/ui/packaged_entry.py` — packaged GUI entry wrapper and packaged-runtime startup diagnostics.
- `src/docmergeforge/ui/paths.py` — desktop data/config/log path resolution.
- `src/docmergeforge/ui/pdf_passwords.py` — password prompting bridge for encrypted PDFs.
- `src/docmergeforge/ui/recent.py` — recent-project persistence and menu support.
- `src/docmergeforge/ui/resources.py` — branding/resource location helpers for source and packaged execution.
- `src/docmergeforge/ui/source_picker.py` — source-folder/file selection UI.
- `src/docmergeforge/ui/sql_wizard.py` — guided SQL Full Mastery preset/project creation UI.
- `src/docmergeforge/ui/support_dialog.py` — support/diagnostic guidance dialog.
- `src/docmergeforge/ui/theme.py` — desktop theme/palette/application styling helpers.
- `src/docmergeforge/ui/workers.py` — background worker abstractions for responsive long-running UI operations.

## Utility infrastructure

- `src/docmergeforge/utilities/__init__.py` — utilities package marker.
- `src/docmergeforge/utilities/atomic.py` — atomic text/binary output helpers with durability-oriented flush/replace semantics.
- `src/docmergeforge/utilities/filename_template.py` — filename-template validation/rendering.
- `src/docmergeforge/utilities/hashing.py` — file hashing helpers.
- `src/docmergeforge/utilities/output_lock.py` — output-directory lock acquisition/release and symlink-hardening logic.
- `src/docmergeforge/utilities/output_naming.py` — safe output filename construction, version suffixing, and Windows reserved-name handling.
- `src/docmergeforge/utilities/output_transaction.py` — staged multi-artifact publication, journals, promotion, rollback, and interrupted-transaction recovery.
- `src/docmergeforge/utilities/storage.py` — storage/free-space/writeability helpers.

## Validation

- `src/docmergeforge/validation/__init__.py` — validation package marker.
- `src/docmergeforge/validation/compare.py` — source/output comparison helpers.
- `src/docmergeforge/validation/ooxml.py` — OOXML package/risk inspection and structural validation.
- `src/docmergeforge/validation/service.py` — high-level input/output validation service.

## Test helper

- `tests/helpers/crash_during_promotion.py` — subprocess helper that intentionally interrupts transaction promotion for recovery tests.

## Integration tests

- `tests/integration/test_build_desktop_script.py` — verifies the desktop build script can be invoked as expected.
- `tests/integration/test_build_provenance_cli.py` — integration coverage for build-provenance command behavior.
- `tests/integration/test_companion_archive.py` — companion archive creation integration coverage.
- `tests/integration/test_docx_merge.py` — end-to-end portable DOCX merge integration coverage.
- `tests/integration/test_docx_publication_features.py` — DOCX publication embellishment integration coverage.
- `tests/integration/test_fidelity_acceptance_script.py` — fidelity acceptance script integration coverage.
- `tests/integration/test_forced_process_recovery.py` — interrupted publication/recovery process integration coverage.
- `tests/integration/test_lo_uno_acceptance_command.py` — LibreOffice UNO acceptance command integration coverage.
- `tests/integration/test_lo_uno_process_group.py` — LibreOffice process-group supervision coverage.
- `tests/integration/test_lo_uno_supervised_smoke.py` — supervised LibreOffice smoke integration coverage.
- `tests/integration/test_order_dialog_accessibility.py` — desktop ordering dialog accessibility integration checks.
- `tests/integration/test_packaged_entry_smoke.py` — packaged desktop entry smoke coverage.
- `tests/integration/test_pdf_merge.py` — end-to-end PDF merge integration coverage.
- `tests/integration/test_pdf_publication_features.py` — PDF publication feature integration coverage.
- `tests/integration/test_resource_evidence_runner.py` — resource-evidence wrapper integration coverage.
- `tests/integration/test_stress_fixture_script.py` — stress-fixture generator integration coverage.
- `tests/integration/test_word_native_merge_acceptance_script.py` — Word native merge acceptance script integration coverage.
- `tests/integration/test_word_native_merge_smoke_script.py` — Word native smoke script integration coverage.
- `tests/integration/test_word_timeout_cleanup_acceptance_script.py` — controlled Word timeout-cleanup acceptance script coverage.

## Regression tests

- `tests/regression/test_120_part_detection.py` — protects 120-part discovery/ordering behavior.
- `tests/regression/test_repeated_transaction_recovery.py` — protects repeated interrupted-transaction recovery behavior.

## Unit tests

- `tests/unit/test_atomic.py` — atomic file publication behavior and failure safety.
- `tests/unit/test_audit.py` — baseline audit behavior.
- `tests/unit/test_build_desktop.py` — desktop build helper unit coverage.
- `tests/unit/test_build_provenance.py` — provenance creation/verification unit coverage.
- `tests/unit/test_cli_fidelity.py` — CLI fidelity-profile/acceptance behavior.
- `tests/unit/test_cli_part_ranges.py` — CLI expected-part-range parsing/bounds.
- `tests/unit/test_cli_project_sync.py` — project-sync CLI preview/apply/approval/error behavior.
- `tests/unit/test_cli_workflow.py` — general CLI workflow and exit-code behavior.
- `tests/unit/test_code_separation.py` — protects manuscript/companion-code separation.
- `tests/unit/test_companion_organizer.py` — companion file classification/organization.
- `tests/unit/test_diagnostics_export.py` — diagnostic export behavior.
- `tests/unit/test_diagnostics_logging.py` — logging/redaction behavior.
- `tests/unit/test_docs_links.py` — Markdown link-validation logic.
- `tests/unit/test_document_audit.py` — document audit detail coverage.
- `tests/unit/test_docx_analysis.py` — DOCX analysis helpers.
- `tests/unit/test_docx_fidelity.py` — fidelity profiles/capabilities.
- `tests/unit/test_docx_fidelity_acceptance.py` — fidelity acceptance evaluation.
- `tests/unit/test_docx_fidelity_corpus.py` — corpus manifest/evidence behavior.
- `tests/unit/test_docx_libreoffice.py` — LibreOffice adapter behavior.
- `tests/unit/test_docx_native.py` — portable OOXML merge primitives.
- `tests/unit/test_docx_section_evidence.py` — section/page-layout evidence extraction.
- `tests/unit/test_docx_word.py` — Word adapter behavior.
- `tests/unit/test_docx_word_merge.py` — Word native merge automation behavior.
- `tests/unit/test_docx_word_merge_acceptance.py` — Word acceptance evidence/orchestration.
- `tests/unit/test_docx_word_merge_cleanup_failure.py` — Word merge cleanup failure handling.
- `tests/unit/test_docx_word_merge_page_number_acceptance.py` — Word page-number acceptance safeguards.
- `tests/unit/test_docx_word_process.py` — Word process supervision and cleanup.
- `tests/unit/test_encrypted_pdf_validation.py` — encrypted PDF validation/password behavior.
- `tests/unit/test_filename_template.py` — filename-template validation/rendering.
- `tests/unit/test_legacy_doc.py` — legacy `.doc` behavior and conversion boundaries.
- `tests/unit/test_lo_uno_acceptance_workflow.py` — LibreOffice acceptance workflow definition safeguards.
- `tests/unit/test_lo_uno_supervised_acceptance.py` — supervised LibreOffice acceptance logic.
- `tests/unit/test_lo_uno_supervised_merge.py` — supervised LibreOffice merge/process behavior.
- `tests/unit/test_ooxml_risk.py` — OOXML risk detection.
- `tests/unit/test_ooxml_validation.py` — OOXML structural validation.
- `tests/unit/test_ordering.py` — ordering/reorder operations.
- `tests/unit/test_output_lock.py` — output-directory lock behavior.
- `tests/unit/test_output_naming.py` — safe output naming/versioning/reserved names.
- `tests/unit/test_output_transaction.py` — core staged output transaction behavior.
- `tests/unit/test_output_transaction_hardening.py` — malformed journal/path/recovery hardening.
- `tests/unit/test_output_transaction_locking.py` — transaction/lock interaction.
- `tests/unit/test_output_transaction_symlinks.py` — transaction symlink defenses.
- `tests/unit/test_part_detection.py` — numbered part detection boundaries.
- `tests/unit/test_profiles.py` — profile catalog behavior.
- `tests/unit/test_project_selection.py` — project selected-file validation/normalization.
- `tests/unit/test_project_selection_paths.py` — platform/path identity rules for selections.
- `tests/unit/test_project_store.py` — project JSON persistence/load/save/migration.
- `tests/unit/test_project_store_persistence_guard.py` — project write guards and failure behavior.
- `tests/unit/test_project_sync.py` — project synchronization planning/apply/backups/safety.
- `tests/unit/test_project_sync_drift.py` — reusable drift evaluation.
- `tests/unit/test_recent_projects.py` — recent-project persistence/UI support.
- `tests/unit/test_recovery_store.py` — durable recovery checkpoint store behavior.
- `tests/unit/test_repetition_audit.py` — repeated-content audit behavior.
- `tests/unit/test_scanner_deduplication.py` — scanner path deduplication.
- `tests/unit/test_scanner_exclusions.py` — recursive exclusion pruning and regular-file filtering.
- `tests/unit/test_service_discovery_safety.py` — application-service discovery safety.
- `tests/unit/test_service_output_transaction.py` — service integration with transactional outputs.
- `tests/unit/test_settings.py` — settings defaults/persistence/validation.
- `tests/unit/test_state_machine.py` — merge lifecycle transition rules.
- `tests/unit/test_storage.py` — storage/free-space/writeability behavior.
- `tests/unit/test_ui_resources.py` — packaged/source UI resource resolution.
- `tests/unit/test_validation.py` — high-level validation service behavior.
- `tests/unit/test_version_metadata.py` — package/version metadata consistency.
- `tests/unit/test_word_acceptance_environment_script.py` — Word environment-report script expectations.
- `tests/unit/test_word_native_acceptance_workflow.py` — Word native workflow definition safeguards.
- `tests/unit/test_word_process_state_script.py` — Word process-state PowerShell script expectations.
- `tests/unit/test_repository_reference.py` — repository-reference coverage checker behavior.

## Maintenance rule

When adding, renaming, or deleting a tracked repository file, update this reference in the same change. The quality workflow runs `scripts/check_repository_reference.py`; a tracked path that is not explicitly present here should be treated as a documentation regression rather than silently accepted.
