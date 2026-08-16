# What Changed

This file records meaningful DocMergeForge development changes, validation evidence, and known limitations. An item is not treated as finished merely because code was pushed; CI, packaging, and acceptance evidence remain part of the completion gate.

## 2026-08-16 — Desktop workflow, packaging foundation, encrypted-PDF support, and CI recovery

### Added
- First-run desktop onboarding and persisted first-run completion state.
- Graphical project setup, project save/load, recent projects, crash-recovery checkpoints, and resume support.
- Graphical document order review/editor before project merging, with explicit separation of PDF/DOCX manuscripts from companion-code packages.
- Guided SQL Full Mastery 120-part desktop workflow and reusable SQL preset project support.
- Desktop Validate, Publication Audit, Compare Output, Settings, Help, Support, About, Recent Projects, and Resume entry points.
- In-memory encrypted-PDF password collection for GUI and CLI workflows. Passwords are verified locally and cleared from the working password map after use.
- Filename-pattern filtering and natural-sort controls in CLI discovery workflows.
- Preflight evidence containing discovered order, missing/duplicate parts, expected outputs, storage estimates, and DOCX conflict counts.
- PDF publication helpers for front matter, bookmarks, metadata, optional page overlays, and output validation.
- DOCX inventory/conflict analysis and fidelity capability reporting.
- Privacy-aware rotating diagnostics logging with sensitive-token/password redaction.
- Reproducible PyInstaller desktop build helper and an unsigned cross-platform packaging workflow foundation.
- Packaging argument tests, legacy DOC conversion safeguard tests, output naming tests, and additional workflow coverage.
- Root-level `what_changed.md` as the development/verification record.

### Changed
- CLI project execution now uses a typed password-provider function rather than an assigned lambda so strict linting/type checks can analyze it cleanly.
- CLI filename filtering was shortened without changing matching behavior so Black and Ruff line-length policies can coexist.
- Logging, DOCX fidelity checks, encrypted-PDF validation, encrypted-PDF UI helpers, and output-naming tests were normalized to the repository Black formatting policy.
- Desktop project execution performs preflight before merge and only proceeds when the available document kinds and storage checks are ready.
- Project workflows preserve selected document ordering instead of silently replacing it with a different order at merge time.
- Source-integrity verification remains part of output promotion: source changes detected during merge cause validation failure instead of silently publishing output.

### Fixed
- Ruff failures in CLI pattern filtering and assigned-lambda usage.
- Black formatting failures in diagnostics logging, DOCX fidelity validation, encrypted-PDF handling, password dialog code, output naming tests, and related publication modules.
- Earlier strict `mypy` failures in CLI result typing and DOCX engine integration.
- Earlier source-integrity verification timing so final output is not promoted after a detected input mutation.
- Earlier OOXML relationship/duplicate-ID validation and companion-package integrity issues found by CI-driven development.

### Packaging
- `scripts/build_desktop.py` provides the reproducible PyInstaller build entry point used by the packaging workflow.
- `.github/workflows/package.yml` provides an unsigned desktop packaging pipeline foundation for supported runner platforms.
- Packaging work must not be interpreted as code signing. No signed Windows, macOS, or Linux binary is claimed.
- Installer/bundle usability, signing/notarization, long-run stress coverage, and release-artifact acceptance still require final verification before a stable release claim.

### Current CI Evidence
- Quality checks run against Python 3.12 and Python 3.13 and include Ruff, Black, strict `mypy`, and pytest with coverage reporting.
- Security workflow continues to run independently and has passed on recent development commits.
- Commit `906e91fb49cd2f5e82dbf66bfd93d4f0b2219ae7` exposed two CLI Ruff violations; subsequent focused commits corrected those issues.
- A later Quality run exposed Black formatting drift in seven files. Focused commits have been applied to the reported modules/tests.
- Commit `506231325a8914ad2ea983dddddefe7b58b771f5` is the current CI-recovery checkpoint for the CLI pattern-filter line-length issue. Its final Quality/Security conclusions must be read from GitHub Actions before treating the complete gate as green.
- The project remains intentionally conservative: no pending workflow is recorded here as passed until GitHub reports a completed success conclusion.

### Development Status
- Core PDF/DOCX discovery, validation, merging, source hashing, atomic output handling, project persistence, dry-run/preflight, reports, SQL preset behavior, companion-code separation, desktop onboarding, ordering, encrypted-PDF password collection, diagnostics, and packaging scaffolding are implemented in the repository.
- Desktop screens required by the current roadmap have implementation entry points in `src/docmergeforge/ui/`; usability/accessibility acceptance is still a separate verification task.
- LibreOffice and Microsoft Word fidelity modes are capability-detected but deliberately rejected as production-ready when the high-fidelity adapter is not complete. Portable OOXML mode remains the production path.

### Known Limitations / Remaining Acceptance Work
- DocMergeForge is not yet eligible for a `v1.0.0` stable claim until the full acceptance matrix is green and release artifacts are verified.
- High-fidelity LibreOffice automation and the Windows Microsoft Word adapter are not production-ready and must not silently replace portable mode.
- Cross-platform packaging exists as an unsigned pipeline foundation; signed installers, notarization, platform-specific installer polish, and signature verification are not complete claims.
- Multi-gigabyte stress testing, disk-full behavior, repeated cancellation/recovery testing, large real-world manuscript fidelity testing, and full accessibility verification remain release-gate work.
- GUI accessibility features require final keyboard-only, screen-reader, high-contrast, scaling, and reduced-motion acceptance testing even where labels/settings are already implemented.
- The project continues to enforce the core safety rule: PDF manuscripts may merge with PDF manuscripts and DOCX manuscripts may merge with DOCX manuscripts, while companion/source code remains separate and is never merged into a manuscript.

### Repository / Commit Identity
- Repository: `https://github.com/sanskarIN/DocMergeForge`
- Development commits made through the connected repository use `Sanskar <sanskarin@outlook.in>`.
