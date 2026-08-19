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
- Project publication uses an outer transaction so mixed PDF/DOCX outputs and generated reports/checksums/checklists are promoted as one bundle.

## v0.2.x — Project workflow and ordering — substantially implemented
- Graphical file-order review/editor before merge.
- Reusable project files, recent-project tracking, crash-recovery checkpoints, and resume UI.
- Filename templates and cross-platform-safe output naming.
- Dry-run/preflight evidence and storage planning.
- Output comparison workflow and manuscript audit/preview support.
- Explicit keyboard shortcuts, screen-reader names/descriptions, and search-label buddy navigation are implemented for the order editor.
- Explicit project selection uses platform-aware path normalization rather than unconditional case folding, so case-distinct POSIX inputs remain individually selectable while duplicate aliases of the same path are rejected.
- Project checkpoint state is updated in memory only after its recovery snapshot has been persisted successfully.
- Expected-part ranges use one shared bounded contract across project loading, project saving, CLI parsing, and validation: six-digit maximum part numbers and at most 10,000 expected parts per range.
- Remaining gate: complete keyboard-only and assistive-technology acceptance of reorder behavior on all supported desktop platforms.

## v0.3.x — Publication tooling — substantially implemented
- PDF front-matter generation.
- PDF bookmark/TOC-related publication helpers and page-number/header/footer overlays.
- DOCX heading/section/style inventory and collision analysis.
- Repeated-front-matter detection and publication audit UI.
- Merge profiles and publication-oriented output naming/settings.
- Windows device-name output protection covers reserved prefixes before the first dot, including names such as `CON.txt` and `COM1.release`.
- Remaining gate: broad real-world manuscript fidelity regression coverage before stable-release claims.

## v0.4.x — Fidelity adapters — implementation advanced / production certification pending
- Interactive encrypted-PDF password-in-memory flow is implemented for desktop and CLI use.
- Portable OOXML fidelity mode remains the production merge path.
- Native-office execution has a shared fail-closed boundary with timeout, captured diagnostics, DOCX package validation, and source-hash verification.
- Native-office final promotion now validates temporary output and sources before promotion, validates them again immediately afterward, and removes the newly created destination if final verification fails.
- LibreOffice has a source-preserving one-document round-trip adapter using detected `libreoffice`/`soffice` executables plus a real Ubuntu Writer round-trip workflow.
- LibreOffice also has one authoritative supervised POSIX Writer/UNO multi-document **acceptance prototype** using a unique profile, unique UNO pipe, copied writable master, ordered `insertDocumentFromURL(...)`, a separate UNO-capable Python worker, source-revision checks, and isolated process-group supervision.
- Supervised LibreOffice process cleanup polls/reaps the launcher while tracking the entire process group, escalates from `SIGTERM` to `SIGKILL` only for that isolated group, and has real POSIX subprocess regression coverage in an independent cleanup workflow.
- The first native LibreOffice multi-document evidence gate measures body paragraph/table/inline-shape/heading structure, privacy-safe ordered body/table-cell text, source hashes, and risky OOXML categories. Section/page-layout/header/footer/page-number certification remains separate.
- An explicit ordered LibreOffice UNO acceptance command supports private multi-document manuscript testing without enabling the production engine.
- Microsoft Word has a source-preserving Windows PowerShell/COM round-trip adapter.
- Microsoft Word also has a separate native multi-document **acceptance prototype** using ordered `Range.InsertFile(...)`, explicit next-page/continuous section boundaries, validated temporary output, source-revision checks, and exact Word process identity cleanup.
- Word native acceptance measures aggregate structure, privacy-safe body/table/header/footer text, section layout/linkage, page-number section semantics (`w:start`, `w:fmt`, `w:chapStyle`, `w:chapSep`), source hashes, and risky OOXML categories.
- Word process cleanup is guarded by PID + `WINWORD` process name + process start-time fingerprint, includes a natural-exit grace period, refuses PID-reuse/mismatched identities, and rejects nominal merge success if forced Word termination was still required.
- A controlled Word timeout-cleanup harness independently verifies the timeout/failure boundary using the same exact-process cleanup identity.
- Capability reporting separates local availability, automation readiness, and production readiness.
- `docmergeforge fidelity-capabilities`, one-document `fidelity-roundtrip`, and private `fidelity-corpus` acceptance paths expose evidence without promoting external adapters to production.
- The normal DOCX merge engine still rejects non-production external modes instead of silently falling back or enabling them.
- `.github/workflows/fidelity-acceptance.yml` executes the general external-office regression/one-document LibreOffice lane.
- `.github/workflows/libreoffice-uno-acceptance.yml` is the maintained real Writer multi-document lane; `.github/workflows/libreoffice-uno-process-cleanup.yml` independently verifies POSIX process supervision.
- `.github/workflows/word-native-acceptance.yml` is manual-only on a controlled self-hosted Windows runner and enforces Word capability policy plus clean pre/post `WINWORD` state.
- Superseded duplicate LibreOffice native prototype code/workflow/tests have been removed so there is one maintained native Writer acceptance surface.
- Remaining LibreOffice gate: execute/review current supervised UNO and cleanup workflows; expand section/page-layout/advanced-OOXML evidence; run representative target-version corpora; complete application integration and human interoperability review.
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

## v0.6.x+ — Packaging, open-source maintenance, and hardening — in progress
- Reproducible PyInstaller desktop build helper is implemented.
- Unsigned cross-platform GitHub Actions packaging is implemented for Windows, macOS, and Ubuntu runners.
- Build/package argument tests are present.
- The packaged PyInstaller entry supports deterministic `--packaged-smoke` initialization without first-run/recovery dialogs and runs a tiny mixed PDF+DOCX publication to exercise bundled document engines and generated evidence.
- Package Desktop launch-tests the built application before archiving it and runs automatically on `main` when packaging/UI configuration changes, as well as on manual dispatch and `v*` tags.
- Package Desktop creates a SHA-256 sidecar for each unsigned archive; final production hashes still need to be generated after later signing/notarization/repackaging.
- Linux package jobs install the same required Qt/EGL runtime prerequisite used by desktop smoke CI.
- macOS packaging handles the native `.app` bundle layout when present instead of assuming the Linux/Windows onedir path.
- Mixed-format document outputs and publication evidence are staged and batch-promoted transactionally, including rollback of earlier replacements when a later promotion fails.
- Completed binary staging artifacts are explicitly flushed with `fsync` before atomic single-file or batch promotion; the output-destination preflight probe writes, flushes, and `fsync`s a byte rather than only creating an empty file.
- Promotion is journaled before final-path mutation. Interrupted `promoting` journals have fail-closed recovery and an explicit `docmergeforge recover-output` CLI path; new transactions refuse to start while journaled recovery is pending.
- Recovery journal parsing is strict about JSON types, positive sizes, hexadecimal SHA-256 values, safe child/final paths, duplicate targets, reused child names, and journal self-reference.
- Recovery refuses symlinked journal files and symlinked/non-file staging or backup children, and pending-transaction discovery ignores symlinked staging directories.
- Publication and recovery share a non-blocking OS-level output-directory lock, preventing two independent DocMergeForge processes from concurrently staging/promoting/recovering the same destination.
- The output lock file is opened fail-closed against pre-existing symlinks and uses `O_NOFOLLOW` where the platform exposes it.
- Recovery Acceptance performs real abrupt child-process termination with `os._exit()` on Windows, macOS, and Ubuntu at multiple promotion boundaries. Run `32022863454` passed all configured phases on all three platforms.
- Destination writeability is probed before expensive project work, fault-injected `ENOSPC` coverage verifies atomic cleanup, and Disk Full Acceptance uses a real 32 MiB Linux tmpfs to verify kernel `ENOSPC` behavior.
- A scalable synthetic stress-fixture generator and manually dispatchable stress workflow are implemented for measured large-run acceptance.
- DOCX fidelity acceptance includes real LibreOffice one-document and supervised multi-document surfaces plus Word boundary regressions; real Word execution remains in its separate controlled Windows workflow.
- PyPI/project metadata now exposes canonical repository/documentation/issues/funding links and the installable package carries a `py.typed` marker for its declared typed-package status.
- GitHub Funding metadata points to the existing Buy Me a Coffee page.
- Bug/feature/PR templates now enforce privacy, source separation, production-readiness, documentation, fidelity, recovery, packaging, and evidence-review expectations.
- Common private fidelity evidence directories and transaction artifacts are ignored by default to reduce accidental commits.
- Remaining gate: additional filesystem/platform exhaustion where claimed, physical power-loss/device-disconnect/network semantics where claimed, an actually executed multi-gigabyte stress run, representative real-world fidelity, human accessibility, clean-machine interactive packaged-app acceptance, platform-specific installer/bundle polish, final signed-release checksum publication, signing, and macOS notarization.
- Signed or notarized binaries are not claimed.

## v1.0.0 quality gate — not yet reached
No stable release until the full master-specification acceptance matrix is verified. At minimum, current Quality/Security evidence must be green for the release candidate, packaging artifacts must be exercised on target platforms, large-file/cancellation/recovery tests must pass, external-office claims must have their own real acceptance evidence, fidelity limitations must remain documented, accessibility acceptance must be completed, and any claimed signed binaries must actually be signed and signature-verified.
