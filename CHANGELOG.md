# Changelog

All notable changes follow semantic versioning.

## [Unreleased]

### Documentation
- Added a dedicated `docs/build/` executable-build manual with a central portal, shared environment/build procedure, complete Windows/macOS/Linux native build guides, CI packaging reference, signing/notarization requirements, packaged-app verification matrix, build troubleshooting, and release go/no-go checklist.
- Converted `docs/building-executables.md` into the canonical entry point for the complete executable manual and linked all build guides from `docs/README.md`.
- Added a canonical `docs/README.md` documentation portal covering the complete user, operator, contributor, architecture, engine, safety, packaging, and release documentation set.
- Added complete installation, getting-started, desktop-user, CLI-reference, project-file, discovery/ordering, validation/preflight, output-artifact, publication-recovery, companion-code, audit/compare, settings, diagnostics, security, accessibility, development, testing/CI, executable-building, release-process, operator-runbook, FAQ, glossary, support, and known-limitations guides.
- Expanded the existing architecture, PDF engine, DOCX engine, privacy, release-packaging, SQL Full Mastery preset, troubleshooting, and stress-testing documentation to match the current implementation.
- Expanded the root README with the complete documentation portal, recovery/build/release-status guidance, and corrected high-fidelity wording so unfinished external office-suite adapters are not represented as production-ready.
- Expanded `CONTRIBUTING.md` with development/test/documentation/accessibility/recovery contribution requirements and linked it to the full developer documentation.
- Expanded `SECURITY.md` with privacy-safe vulnerability-reporting guidance and links to the security/privacy/diagnostics documentation.
- Documentation now distinguishes implemented behavior, automatically verified behavior, and production/manual acceptance; unsigned builds, unfinished high-fidelity adapters, multi-gigabyte stress, real forced-process recovery, and human accessibility remain explicit release gates until verified.

### Added
- First-run onboarding, project ordering, recent-project history, recovery checkpoints, and guided SQL preset desktop workflow.
- Desktop validation, publication audit, output comparison, settings, help, support, and About experiences.
- In-memory encrypted-PDF password handling for CLI and desktop workflows.
- Preflight evidence, PDF publication helpers, DOCX inventory/conflict analysis, and privacy-aware rotating diagnostics.
- Reproducible PyInstaller packaging helpers and unsigned cross-platform packaging workflow scaffolding.
- Desktop packaging root validation and a `scripts/build_desktop.py --check` preflight that verifies required repository inputs without invoking PyInstaller.
- Unit and integration coverage for desktop packaging preflight behavior, including execution of the real build script check path.
- Transactional publication-bundle staging and rollback across mixed PDF/DOCX outputs, reports, manifests, checksums, companion indexes, and publishing checklists.
- Durable publication-promotion journals containing staged fingerprints and rollback metadata, plus `docmergeforge recover-output` for explicit fail-closed recovery of interrupted promotion transactions.
- Repeated cancellation/recovery regression coverage, simulated interrupted-promotion recovery coverage, and injected disk-exhaustion cleanup coverage.
- Output-destination writeability probing before expensive project merge work.
- Scalable synthetic stress-fixture generation plus a manually dispatchable stress-acceptance workflow with validation, preflight, merge, output comparison, size evidence, and artifact upload.
- Explicit accessibility metadata and keyboard controls across project setup, source selection, file ordering, settings, reports, recent projects, and merge progress, with headless automated accessibility smoke coverage.

### Changed
- Centralized desktop packaging argument generation inside the installable `docmergeforge.packaging` package so builds and tests share the same configuration.
- Strengthened ordering, source-integrity, formatting, strict typing, and CI validation paths.
- PDF and DOCX engines now check cancellation through later finalization stages instead of only between source documents.
- Project merge completion now has one publication boundary: document outputs and generated evidence are promoted only after all staged work succeeds and source integrity is revalidated.
- Publication promotion now writes a `promoting` journal before final-path mutation and a `committed` marker only after the complete batch succeeds; incomplete rollback evidence is preserved instead of silently deleted.
- New journaled output transactions refuse to start while interrupted recovery evidence is pending.
- Build Smoke now runs on `main` pushes as well as pull requests/manual dispatch and validates desktop packaging configuration on Ubuntu, Windows, and macOS runners.
- Build Smoke also runs the headless desktop accessibility smoke check on each configured desktop runner.
- The 120-Part Regression workflow now runs on `main` pushes in addition to pull requests/manual dispatch.
- Package Desktop installs the declared `build` extra and validates packaging configuration before invoking PyInstaller.

### Fixed
- CLI lint/type issues found by Ruff and mypy.
- Black formatting drift across desktop, PDF, DOCX, diagnostics, and tests.
- Packaging-test import failure caused by importing repository-only script modules from the installed test environment.
- Ruff import-layout failure introduced by the new packaging preflight integration test.
- Mixed-format partial-publication risk where a completed PDF could previously be published before a later DOCX failure or cancellation.
- Publication-evidence skew where document outputs could previously be replaced before report generation failed.
- Cancellation gaps during PDF page finalization and DOCX post-merge finalization.
- Recovery-evidence loss risk when an automatic promotion rollback itself fails.
- Late output-permission failures that could previously occur after expensive validation/merge preparation despite sufficient free-space estimates.

### Validation
- Commit `8cc96d714c43922b0effcbb16400fb2952f056b1` passed Quality run `31948936694` on Python 3.12 and Python 3.13, including Ruff, Black, strict mypy, and full pytest with coverage.
- The same commit passed 120-Part Regression run `31948936615`.
- The same commit passed cross-platform Build Smoke run `31948936667` on the configured Ubuntu, Windows, and macOS matrix.
- The same commit passed Security run `31948936651`.
- Recovery checkpoint `3a38ae64d5a96f76f8557f4443e372c9a4e35871` passed Quality run `32012033604`, 120-Part Regression run `32012033657`, and Security run `32012033644`.
- Hardening checkpoint `82fe37725a2ae4e71678903c4d67fdff40d819e4` passed Quality run `32014319266` on Python 3.12 and Python 3.13, including Ruff, Black, strict mypy, and full pytest with coverage.
- The same hardening checkpoint passed 120-Part Regression run `32014319264`, cross-platform Build Smoke run `32014319394` on Ubuntu/Windows/macOS including the headless accessibility smoke and packaging preflight, and Security/CodeQL run `32014319291`.
- The scalable manual stress workflow has been added but an actual multi-gigabyte acceptance run is not claimed until such a workflow run succeeds and its measured evidence is recorded.
- These checks do not claim signed installers, notarization, production package acceptance, full human accessibility acceptance, real forced-process-termination acceptance, or `v1.0.0` readiness.

## [0.1.0] - 2026-08-16

### Added
- Initial local-first architecture.
- Natural part discovery and validation.
- Safe PDF and DOCX merge engines.
- SQL Full Mastery 120-part preset.
- Companion-code indexing without code merging.
- Checksums, manifest, HTML/Markdown reporting, and publishing checklist.
- CLI and PySide6 desktop shell.
- Recovery, diagnostics, storage estimation, audit primitives, CI, tests, and branding.
