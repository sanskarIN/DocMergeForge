# What Changed

This file records meaningful DocMergeForge development changes, validation evidence, and known limitations. It is intentionally explicit about incomplete work and CI failures; an item is not considered complete merely because code was pushed.

## 2026-08-16 — CI quality recovery and publication pipeline hardening

### Added
- Root-level `what_changed.md` development record required by the project specification.
- Ongoing validation notes for linting, formatting, type checking, tests, and security workflows.

### Changed
- Wrapped long DOCX validation messages so Ruff line-length checks can evaluate the publication pipeline cleanly.
- Wrapped project-setup guidance and main-window validation text without changing user-visible meaning.
- Reformatted light/dark theme stylesheet declarations for consistent source formatting.
- Applied Black-compatible formatting to publication-audit result construction.
- Removed obsolete `mypy` ignore comments from DOCX publication helpers now understood by the active type checker.
- Renamed the CLI comparison payload variable so strict `mypy` checking does not treat it as an incompatible redefinition.

### Fixed
- Ruff failures caused by line-length violations in DOCX, UI dialog, main-window, and theme modules.
- Black failure in the publication-audit UI path.
- Strict `mypy` failures caused by unused ignore comments in `docx/publication.py`.
- Strict `mypy` failure caused by reusing `payload` for different CLI branches.

### Tests
- Quality workflow runs on Python 3.12 and Python 3.13 remain the source of truth for final validation.
- Security workflow completed successfully for commit `e0e63b6cc5ea25a1c2a6f0aa154ac894c4fe830a`.
- The Quality workflow for that commit passed Ruff and Black, then exposed three strict `mypy` errors; follow-up commits `c9f6ed977c3adbe45c786e0dff3737801a1a706f` and `ce1de9e356e7b14110f8d111cee00dac743d90ca` address those errors.
- Full pytest status for the follow-up commits is pending remote workflow confirmation and must not be treated as passed until GitHub Actions reports success.

### Validation
- Main branch writes are being confirmed by GitHub after each meaningful commit.
- Commit author/committer identity used by the connected repository is `Sanskar <sanskarin@outlook.in>`.
- Source manuscripts and companion-code contents are not modified by these CI/code-quality fixes.

### Known Limitations
- DocMergeForge is not yet eligible for a v1.0 stable claim because the complete acceptance and packaging quality gate is not yet verified.
- Full graphical ordering/editing, first-run onboarding, guided SQL wizard, encrypted-PDF password workflow, high-fidelity Word/LibreOffice adapters, packaging/signing, and the remaining accessibility/hardening requirements still require completion or final verification.
- Signed binaries are not claimed.
- The project continues to enforce the rule that document manuscripts may be merged while companion code must remain separate.
