# Changelog

All notable changes follow semantic versioning.

## [Unreleased]

### Added
- First-run onboarding, project ordering, recent-project history, recovery checkpoints, and guided SQL preset desktop workflow.
- Desktop validation, publication audit, output comparison, settings, help, support, and About experiences.
- In-memory encrypted-PDF password handling for CLI and desktop workflows.
- Preflight evidence, PDF publication helpers, DOCX inventory/conflict analysis, and privacy-aware rotating diagnostics.
- Reproducible PyInstaller packaging helpers and unsigned cross-platform packaging workflow scaffolding.

### Changed
- Centralized desktop packaging argument generation inside the installable `docmergeforge.packaging` package so builds and tests share the same configuration.
- Strengthened ordering, source-integrity, formatting, strict typing, and CI validation paths.

### Fixed
- CLI lint/type issues found by Ruff and mypy.
- Black formatting drift across desktop, PDF, DOCX, diagnostics, and tests.
- Packaging-test import failure caused by importing repository-only script modules from the installed test environment.

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
