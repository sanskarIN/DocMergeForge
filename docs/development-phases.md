# Development Phases and Version Plan

The master specification is larger than a single safe implementation step. Work is divided into independently testable versions so incomplete features are never presented as finished. Status labels below describe repository implementation, not a stable-release guarantee.

## v0.1.x — Safe core foundation — implemented / under continuous verification
- Typed domain model and merge state machine.
- Natural discovery, classification, hashing, missing/duplicate detection.
- Atomic PDF/DOCX merge engines.
- OOXML validation and source-integrity verification.
- SQL Full Mastery 120-part preset.
- Companion-code indexing/copy organization only; no code merging.
- Reports, checksums, manifest, publishing checklist.
- CLI, desktop application, branding, CI, and unit/integration/regression coverage.

## v0.2.x — Project workflow and ordering — substantially implemented
- Graphical file-order review/editor before merge.
- Reusable project files, recent-project tracking, crash-recovery checkpoints, and resume UI.
- Filename templates and cross-platform-safe output naming.
- Dry-run/preflight evidence and storage planning.
- Output comparison workflow and manuscript audit/preview support.
- Remaining gate: complete UX/accessibility acceptance of reorder behavior on all supported desktop platforms.

## v0.3.x — Publication tooling — substantially implemented
- PDF front-matter generation.
- PDF bookmark/TOC-related publication helpers and page-number/header/footer overlays.
- DOCX heading/section/style inventory and collision analysis.
- Repeated-front-matter detection and publication audit UI.
- Merge profiles and publication-oriented output naming/settings.
- Remaining gate: broad real-world manuscript fidelity regression coverage before stable-release claims.

## v0.4.x — Fidelity adapters — partially implemented
- Interactive encrypted-PDF password-in-memory flow is implemented for desktop and CLI use.
- Portable OOXML fidelity mode is the production path.
- LibreOffice availability is detected, but high-fidelity automation is not production-ready.
- Microsoft Word capability is detected on Windows, but the high-fidelity adapter is not production-ready.
- Non-production fidelity modes are rejected explicitly instead of silently falling back.
- Remaining gate: complete LibreOffice/Word adapters plus risky-construct review and platform fidelity testing.

## v0.5.x — Desktop completeness and accessibility — substantially implemented / acceptance pending
- Settings, Help, Recent Projects, Validate, Audit, Compare, Resume, Support, and About entry points are implemented.
- First-run onboarding is implemented and persisted.
- Accessible names, text scaling/theme controls, and keyboard-oriented application behavior are present in the desktop codebase.
- Light/dark/system theme infrastructure is implemented.
- Remaining gate: keyboard-only, screen-reader, high-contrast, reduced-motion, scaling, and localization-readiness acceptance testing across supported platforms.

## v0.6.x+ — Packaging and hardening — in progress
- Reproducible PyInstaller desktop build helper is implemented.
- Unsigned cross-platform GitHub Actions packaging workflow foundation is implemented.
- Build/package argument tests are present.
- Remaining gate: platform-specific installer/bundle polish, artifact verification, disk-full tests, repeated cancellation/crash recovery, multi-gigabyte stress tests, accessibility stress tests, and release checksum/signing automation.
- Signed or notarized binaries are not claimed.

## v1.0.0 quality gate — not yet reached
No stable release until the full master-specification acceptance matrix is verified. At minimum, the Quality and Security workflows must be green at the release candidate, packaging artifacts must be exercised on their target platforms, large-file/cancellation/recovery tests must pass, fidelity limitations must be documented, and accessibility checks must be completed. Signed binaries must never be claimed unless actual signing and signature verification are completed.
