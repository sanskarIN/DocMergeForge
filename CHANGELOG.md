# Changelog

All notable changes follow semantic versioning.

## [Unreleased]

### Added
- First-run onboarding, project ordering, recent-project history, recovery checkpoints, and guided SQL preset desktop workflow.
- Desktop validation, publication audit, output comparison, settings, help, support, and About experiences.
- In-memory encrypted-PDF password handling for CLI and desktop workflows.
- Preflight evidence, PDF publication helpers, DOCX inventory/conflict analysis, and privacy-aware rotating diagnostics.
- Reproducible PyInstaller packaging helpers and unsigned cross-platform packaging workflow scaffolding.
- Desktop packaging root validation and a `scripts/build_desktop.py --check` preflight that verifies required repository inputs without invoking PyInstaller.
- Unit and integration coverage for desktop packaging preflight behavior, including execution of the real build script check path.

### Changed
- Centralized desktop packaging argument generation inside the installable `docmergeforge.packaging` package so builds and tests share the same configuration.
- Strengthened ordering, source-integrity, formatting, strict typing, and CI validation paths.
- Build Smoke now runs on `main` pushes as well as pull requests/manual dispatch and validates desktop packaging configuration on Ubuntu, Windows, and macOS runners.
- The 120-Part Regression workflow now runs on `main` pushes in addition to pull requests/manual dispatch.
- Package Desktop installs the declared `build` extra and validates packaging configuration before invoking PyInstaller.

### Fixed
- CLI lint/type issues found by Ruff and mypy.
- Black formatting drift across desktop, PDF, DOCX, diagnostics, and tests.
- Packaging-test import failure caused by importing repository-only script modules from the installed test environment.
- Ruff import-layout failure introduced by the new packaging preflight integration test.

### Validation
- Commit `8cc96d714c43922b0effcbb16400fb2952f056b1` passed Quality run `31948936694` on Python 3.12 and Python 3.13, including Ruff, Black, strict mypy, and full pytest with coverage.
- The same commit passed 120-Part Regression run `31948936615`.
- The same commit passed cross-platform Build Smoke run `31948936667` on the configured Ubuntu, Windows, and macOS matrix.
- The same commit passed Security run `31948936651`.
- These checks do not claim signed installers, notarization, production package acceptance, or `v1.0.0` readiness.

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
