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
- Project publication now uses an outer transaction so mixed PDF/DOCX outputs and their generated reports/checksums/checklists are promoted as one bundle.

## v0.2.x — Project workflow and ordering — substantially implemented
- Graphical file-order review/editor before merge.
- Reusable project files, recent-project tracking, crash-recovery checkpoints, and resume UI.
- Filename templates and cross-platform-safe output naming.
- Dry-run/preflight evidence and storage planning.
- Output comparison workflow and manuscript audit/preview support.
- Explicit keyboard shortcuts, screen-reader names/descriptions, and search-label buddy navigation are implemented for the order editor.
- Remaining gate: complete keyboard-only and assistive-technology acceptance of reorder behavior on all supported desktop platforms.

## v0.3.x — Publication tooling — substantially implemented
- PDF front-matter generation.
- PDF bookmark/TOC-related publication helpers and page-number/header/footer overlays.
- DOCX heading/section/style inventory and collision analysis.
- Repeated-front-matter detection and publication audit UI.
- Merge profiles and publication-oriented output naming/settings.
- Remaining gate: broad real-world manuscript fidelity regression coverage before stable-release claims.

## v0.4.x — Fidelity adapters — implementation advanced / production certification pending
- Interactive encrypted-PDF password-in-memory flow is implemented for desktop and CLI use.
- Portable OOXML fidelity mode remains the production merge path.
- Native office execution has a shared fail-closed boundary with timeout, captured diagnostics, DOCX output validation, and source-hash verification.
- LibreOffice has a source-preserving DOCX round-trip adapter using detected `libreoffice`/`soffice` executables plus a real Ubuntu Writer round-trip workflow.
- Microsoft Word has a source-preserving Windows PowerShell/COM round-trip adapter.
- Microsoft Word also has a separate native multi-document **acceptance prototype** using ordered `Range.InsertFile(...)`, explicit next-page/continuous section boundaries, validated temporary output, source-revision checks, and exact Word process identity cleanup.
- Word native acceptance measures aggregate structure, privacy-safe body/table/header/footer text, section layout/linkage, page-number section semantics (`w:start`, `w:fmt`, `w:chapStyle`, `w:chapSep`), source hashes, and risky OOXML categories.
- Word process cleanup is guarded by PID + `WINWORD` process name + process start-time fingerprint, includes a natural-exit grace period, refuses PID-reuse/mismatched identities, and rejects nominal merge success if forced Word termination was still required.
- The deterministic Word smoke uses portrait/landscape sources, distinct margins/header/footer distances, and decimal/upper-Roman page-number restart semantics.
- Capability reporting separates local availability, automation readiness, and production readiness.
- `docmergeforge fidelity-capabilities`, `fidelity-roundtrip`, and private `fidelity-corpus` acceptance paths expose evidence without promoting external adapters to production.
- The normal DOCX merge engine still rejects non-production external modes instead of silently falling back or enabling them.
- `.github/workflows/fidelity-acceptance.yml` runs the complete Word boundary regression surface on Linux while executing LibreOffice as the real external application there.
- `.github/workflows/word-native-acceptance.yml` is manual-only on a controlled self-hosted Windows runner and enforces Word capability policy plus clean pre/post `WINWORD` state.
- Remaining LibreOffice gate: implement/certify true native multi-document LibreOffice semantics and representative target-platform corpora.
- Remaining Word gate: execute/record real controlled normal and forced-timeout Word runs, representative private multi-document corpora, exact-version evidence, repair-prompt/manual rendering review, packaged integration where claimed, and regressions for discovered deviations.
- External `libreoffice` and `word` modes remain `production_ready=false`. A synthetic fixture, source-CI regression, or workflow definition alone is not production certification.

## v0.5.x — Desktop completeness and accessibility — substantially implemented / acceptance pending
- Settings, Help, Recent Projects, Validate, Audit, Compare, Resume, Support, and About entry points are implemented.
- First-run onboarding is implemented and persisted.
- Accessible names, text scaling/theme controls, and keyboard-oriented application behavior are present in the desktop codebase.
- Project setup, source selection, ordering, settings, reports, recent projects, and merge progress expose explicit accessibility metadata; the order/source editors include keyboard shortcuts for their major controls.
- Headless accessibility smoke coverage is included in the cross-platform Build Smoke workflow.
- Light/dark/system theme infrastructure is implemented.
- Remaining gate: human keyboard-only, screen-reader, high-contrast, reduced-motion, scaling, and localization-readiness acceptance testing across supported platforms. Automated metadata checks are supporting evidence, not a substitute for those tests.

## v0.6.x+ — Packaging and hardening — in progress
- Reproducible PyInstaller desktop build helper is implemented.
- Unsigned cross-platform GitHub Actions packaging is implemented for Windows, macOS, and Ubuntu runners.
- Build/package argument tests are present.
- The packaged PyInstaller entry supports deterministic `--packaged-smoke` initialization without first-run/recovery dialogs and runs a tiny mixed PDF+DOCX publication to exercise bundled document engines and generated evidence.
- Package Desktop launch-tests the built application before archiving it and runs automatically on `main` when packaging/UI configuration changes, as well as on manual dispatch and `v*` tags.
- Package Desktop creates a SHA-256 sidecar for each unsigned archive; final production hashes still need to be generated after later signing/notarization/repackaging.
- Linux package jobs install the same required Qt/EGL runtime prerequisite used by desktop smoke CI.
- macOS packaging handles the native `.app` bundle layout when present instead of assuming the Linux/Windows onedir path.
- Mixed-format document outputs and publication evidence are staged and batch-promoted transactionally, including rollback of earlier replacements when a later promotion fails.
- Promotion is journaled before final-path mutation. Interrupted `promoting` journals have fail-closed recovery and an explicit `docmergeforge recover-output` CLI path; new transactions refuse to start while journaled recovery is pending.
- Publication and recovery share a non-blocking OS-level output-directory lock, preventing two independent DocMergeForge processes from concurrently staging/promoting/recovering the same destination.
- Recovery Acceptance performs real abrupt child-process termination with `os._exit()` on Windows, macOS, and Ubuntu at multiple promotion boundaries. Run `32022863454` passed all configured phases on all three platforms.
- Destination writeability is probed before expensive project work, fault-injected `ENOSPC` coverage verifies atomic cleanup, and Disk Full Acceptance uses a real 32 MiB Linux tmpfs to verify kernel `ENOSPC` behavior.
- A scalable synthetic stress-fixture generator and manually dispatchable stress workflow are implemented for measured large-run acceptance.
- DOCX Fidelity Acceptance includes real LibreOffice Writer execution plus Word boundary regressions, while real Word execution is kept in its separate controlled Windows workflow.
- Remaining gate: additional filesystem/platform exhaustion where claimed, physical power-loss/device-disconnect/network semantics where claimed, an actually executed multi-gigabyte stress run, representative real-world fidelity, human accessibility, clean-machine interactive packaged-app acceptance, platform-specific installer/bundle polish, final signed-release checksum publication, signing, and macOS notarization.
- Signed or notarized binaries are not claimed.

## v1.0.0 quality gate — not yet reached
No stable release until the full master-specification acceptance matrix is verified. At minimum, current Quality/Security evidence must be green for the release candidate, packaging artifacts must be exercised on target platforms, large-file/cancellation/recovery tests must pass, external-office claims must have their own real acceptance evidence, fidelity limitations must remain documented, accessibility acceptance must be completed, and any claimed signed binaries must actually be signed and signature-verified.
