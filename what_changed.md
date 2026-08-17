# What Changed

This file records meaningful DocMergeForge development changes, validation evidence, and known limitations. An item is not treated as finished merely because code was pushed; CI, packaging, and acceptance evidence remain part of the completion gate.

## 2026-08-17 — Complete executable build documentation

### Added
- `docs/build/README.md` as the dedicated executable-build documentation portal and canonical navigation for local builds, native platform builds, CI packaging, signing/notarization, verification, troubleshooting, and release acceptance.
- `docs/build/common.md` with the shared end-to-end build procedure: commit identity, Python 3.12 parity, isolated environment setup, `.[build]` installation, dependency/environment capture, quality checks, packaging preflight, exact shared PyInstaller intent, onedir/onefile behavior, clean rebuilds, clean-machine testing, archive creation, hashes, metadata retention, and explicit installer-vs-executable boundaries.
- `docs/build/windows.md` with complete Windows PowerShell build steps, onedir/onefile acceptance, clean-machine testing, path/Unicode coverage, ZIP creation, SHA-256, Authenticode inspection, production SignTool command shapes, SmartScreen/reputation considerations, architecture evidence, DLL/runtime troubleshooting, optional installer requirements, and a Windows release checklist.
- `docs/build/macos.md` with complete native macOS build steps, actual `dist`/bundle inspection, Apple Silicon/Intel architecture rules, Finder/Terminal launch acceptance, Developer ID signing principles, `codesign`/`spctl` verification, `notarytool` notarization flow, stapling validation, DMG/PKG boundaries, final hashing rules, Gatekeeper acceptance, and a macOS release checklist.
- `docs/build/linux.md` with complete Linux build steps, Python 3.12 and `libegl1` prerequisites matching CI, distro/glibc baseline recording, onedir/onefile testing, X11/Wayland checks, `ldd` runtime inspection, Qt/EGL troubleshooting, filesystem/permission acceptance, tar.gz/hash generation, distro compatibility strategy, optional AppImage/DEB/RPM boundaries, and a Linux release checklist.
- `docs/build/ci-packaging.md` documenting the current `Package Desktop` triggers, matrix, permissions, exact workflow stages/archive commands, current unsigned artifact names, relationship to Build Smoke/Quality/Regression/Security, secure future signing architecture, artifact verification, failure triage, and CI packaging acceptance-record template.
- `docs/build/signing-and-notarization.md` documenting the production trust boundary: credential safety, build/sign/verify order, Windows Authenticode/timestamp verification, macOS Developer ID signing/notarization/stapling, Linux hash/package trust, post-signing hash rules, protected CI signing architecture, supply-chain digest checks, credential rotation, failure handling, and platform trust checklists.
- `docs/build/verification.md` defining four executable-verification levels and full packaged-app acceptance covering artifact inspection, launch outside the repository, UI smoke, PDF/DOCX/mixed-format merges, encrypted PDF flow, cancellation/recovery, filesystem/path/resource checks, one-file extraction, clean-machine acceptance, platform trust checks, final hashes, archive extraction, privacy inspection, and a reusable acceptance-record template.
- `docs/build/troubleshooting.md` covering packaging-preflight/Python/editable-install problems, PyInstaller launch failures, Qt plugin/EGL/runtime issues, missing assets/dependencies, onedir/onefile differences, Windows SmartScreen/antivirus, macOS Gatekeeper/notarization, Linux glibc/permissions, archive-layout failures, stale build state, CI-vs-local differences, signature/hash failures, and privacy-safe diagnostic reporting.
- `docs/build/release-checklist.md` as the complete executable release go/no-go checklist spanning source identity, automated gates, build environment, Windows/macOS/Linux acceptance, Package Desktop artifacts, packaged application functionality, data safety, fidelity, accessibility, stress/recovery, security/privacy, signing/notarization, final hashes, installers/distribution containers, release notes, and final platform decision recording.

### Expanded / Integrated
- Replaced the former single-page `docs/building-executables.md` with a canonical executable-build entry point that links the complete build manual, records exact repository-supported PyInstaller modes/arguments, native-build rules, CI artifact names, production trust boundaries, installer/package non-claims, clean-build/hash commands, release evidence, and current pre-stable packaging status.
- Expanded `docs/README.md` with a dedicated **Building executables** section linking every executable-build manual directly.
- Updated `CHANGELOG.md` to record the dedicated executable-build documentation subsystem and its conservative trust/release boundaries.

### Current Implementation Boundary
- Repository-supported executable creation remains PyInstaller onedir by default and optional onefile through `scripts/build_desktop.py --one-file`.
- Shared build configuration remains centralized in `src/docmergeforge/packaging/desktop.py`.
- `.github/workflows/package.yml` remains an unsigned Windows/macOS/Linux packaging foundation using Python 3.12.
- The documentation intentionally does **not** claim automated Windows MSI/MSIX/Inno/NSIS, macOS DMG/PKG, Linux AppImage/DEB/RPM/Flatpak/Snap, production Windows signing, macOS notarization, or stable packaged-app acceptance until those capabilities are actually implemented and verified.
- Executable documentation checkpoint before this development-record commit: `c718b82a2c9e5bb303261c5048396ab28ef4a6dc`.

## 2026-08-17 — Complete documentation suite

### Added
- A canonical `docs/README.md` documentation portal that organizes end-user, operator, contributor, architecture, engine, configuration, safety, testing, packaging, and release references.
- `docs/installation.md` with Windows/macOS/Linux source installation, virtual environments, developer/build extras, Linux Qt prerequisites, storage/permissions guidance, updates, and uninstallation.
- `docs/getting-started.md` with a complete first publication from source organization and numbered validation through project dry-run, merge, evidence review, comparison, audit, and interrupted-output recovery.
- `docs/cli-reference.md` documenting every current command (`validate`, `pdf`, `docx`, `sql-preset`, `project-create`, `merge`, `recover-output`, `audit`, `compare`), exact part-range/pattern/natural-sort behavior, encrypted-PDF interaction, exit behavior, JSON evidence, and automation guidance.
- `docs/desktop-guide.md` covering first-run onboarding, project/source setup, ordering, preflight, PDF/DOCX settings, encrypted PDFs, progress/cancellation, transactional publication, reports, audit/compare, recent projects, recovery, settings, accessibility, and SQL preset operation.
- `docs/project-files.md` documenting the saved JSON schema, merge/PDF/DOCX defaults, lifecycle states/checkpoints, atomic saving, portability, compatibility, manual-edit risks, and privacy/version-control guidance.
- `docs/discovery-and-ordering.md` documenting recursive scanning, exact document/archive classification, `.doc` safeguard behavior, supported part-number naming patterns, natural ordering, filtering, selected-file order, PDF inspection, and source hashing.
- `docs/validation-and-preflight.md` documenting numbered-set validation, project dry-run evidence, expected output calculation, DOCX conflict analysis, the current storage estimate formula, output writeability probe, encrypted-PDF readiness, source-integrity validation, and post-output validation distinctions.
- `docs/output-artifacts.md` documenting generic and SQL-preset manuscript/evidence filenames, manifest/checksum/report/index/checklist roles, transaction staging, overwrite/versioned behavior, and release archiving.
- `docs/recovery.md` as a full publication-recovery runbook covering transaction folders/journal phases, automatic/incomplete rollback, abrupt termination, `recover-output`, fingerprint checks, backup restoration, fail-closed conflicts, corrupt/unsafe journals, cancellation vs crash behavior, and operator procedures.
- `docs/companion-code.md` documenting companion archive classification, non-extraction/non-merge policy, companion indexes/hashes, recommended layouts, release handling, and unsupported build/refactor behavior.
- `docs/audit-and-compare.md` documenting the current targeted audit patterns, encrypted-PDF audit limitation, PDF page evidence comparison, DOCX structural count comparison, interpretation limits, and post-publication QA sequence.
- `docs/security.md` documenting trust boundaries, local-first security model, password/source-integrity handling, companion archive safety, transaction path/fingerprint safety, diagnostics, parser/external-suite risks, CodeQL, and package-authenticity requirements.
- `docs/accessibility.md` documenting the exact automated accessibility-smoke coverage plus the human keyboard/screen-reader/high-contrast/scaling/reduced-motion acceptance matrix that remains before a stable claim.
- `docs/development.md` documenting development principles, repository/package structure, quality/type/style rules, fixtures, UI/document-engine/transaction/storage/diagnostics development requirements, packaging, commit style, and definition of done.
- `docs/testing-and-ci.md` documenting unit/integration/regression testing, Quality, 120-Part Regression, Build Smoke, Security, Package Desktop, Stress Acceptance, accessibility/packaging/recovery/fidelity tests, and release CI evidence requirements.
- `docs/building-executables.md` with a complete native Windows/macOS/Linux PyInstaller build guide, build-root preflight, onedir/one-file variants, platform acceptance checklists, CI package workflow, debugging, reproducibility notes, and production signing/notarization gates.
- `docs/release-process.md` defining implementation/automatic-verification/production-acceptance as separate states and providing the full stable-release sequence through source CI, regression, security, recovery, stress, fidelity, accessibility, packaging, signing, hashing, tagging, and post-release verification.
- `docs/operator-runbook.md` providing a production merge procedure plus incident playbooks for cancellation, crash recovery, recovery conflicts, storage/access failures, missing/duplicate parts, encryption, legacy `.doc`, and SQL Full Mastery publication.
- `docs/faq.md`, `docs/glossary.md`, and `docs/support.md` covering common user questions, terminology, support contacts, privacy-safe bug reports, diagnostics, accessibility/fidelity reporting, and recovery-related support.
- `docs/known-limitations.md` explicitly documenting the current pre-stable limitations and open release gates rather than allowing the documentation to imply universal DOCX fidelity, unlimited scale, full accessibility certification, or signed production packages.
- `docs/settings-reference.md` documenting every current `AppSettings` field/default, persistence/loading behavior, privacy implications, and the distinction between application defaults and saved project settings.
- `docs/diagnostics.md` documenting rotating-log size/backups/format, sensitive-text/Bearer redaction, diagnostic JSON export contents/atomic write, privacy limitations, and safe support procedures.

### Expanded / Corrected
- Expanded `docs/architecture.md` from a short layer sketch into the full package map, core data flow, domain states, discovery/validation/engine boundaries, source-integrity/companion/transaction/storage/reporting/UI/CLI/packaging/testing architecture, and extension rules.
- Expanded `docs/pdf-engine.md` to match implemented ordering, atomic output, front matter, encrypted-password provider, bookmarks, overlays, optimization, metadata, cancellation, page validation, source integrity, direct/project behavior, compare/audit, and fidelity acceptance.
- Expanded `docs/docx-engine.md` to match production-fidelity gating, package validation/conflict policies, master-document composition, headings/TOC/page breaks/sections/page numbering/headers/footers, cancellation, output validation, project transactions, comparison, and known OOXML fidelity risks.
- Expanded `docs/privacy.md` with local-first boundaries, project/source metadata, passwords, hashes, generated evidence, diagnostics/audit output, staging/recovery privacy, telemetry policy, backups, and public-sharing checklist.
- Expanded `docs/release-packaging.md` with shared PyInstaller configuration, native platform build status, current unsigned artifact names, signing credential policy, artifact hashing, packaged-app testing, onedir/one-file differences, and production definition of done.
- Expanded `docs/sql-full-mastery-preset.md` with exact preset identity, Parts 1–120 readiness, fixed filenames, exact PDF/DOCX defaults, dry-run evidence, companion behavior, transactional publication, encrypted PDFs, regression fixture, post-publication checks, and human QA checklist.
- Expanded `docs/troubleshooting.md` into a detailed diagnostic reference spanning installation/GUI, part detection/order/filtering, encrypted PDFs, PDF/DOCX validation/fidelity, storage/writeability, transaction recovery, source integrity, reports/compare/audit, accessibility, packaging, OS trust behavior, and CI failures.
- Expanded `docs/stress-testing.md` with scalable workload methodology, measured-source-size requirements, manual workflow environment/inputs, cancellation/disk-full/real-process-termination/network-filesystem plans, resource evidence, pass criteria, and explicit distinctions between synthetic regression, synthetic stress, real fidelity, and real recovery acceptance.
- Expanded the root `README.md` with a prominent documentation portal, current project guarantees, safe interrupted-output recovery, CLI/GUI/build guidance, corrected high-fidelity wording, privacy/security/accessibility/release-status guidance, and links to all major manuals.
- Expanded `CONTRIBUTING.md` with development/test/documentation/accessibility/fidelity/recovery contribution requirements and linked it to the full developer documentation.
- Expanded `SECURITY.md` with privacy-safe vulnerability-reporting procedures, recovery/diagnostic considerations, coordinated disclosure guidance, and links to the security/privacy/diagnostics documentation.
- Added a `Documentation` section to `CHANGELOG.md` recording the completed documentation system and its conservative release-claim policy.

### Documentation Integrity / Status
- The complete documentation directory was verified on `main` after creation/expansion, including the central index and all newly linked reference files.
- Documentation implementation checkpoint before this development-record commit: `79df8741269e4011dd17c7249e896db74c83a76b`.
- The documentation changes are intentionally documentation-only and do not replace the previously verified source hardening checkpoint `82fe37725a2ae4e71678903c4d67fdff40d819e4`.
- The source hardening checkpoint remains verified by Quality run `32014319266` (Python 3.12/3.13), 120-Part Regression run `32014319264`, Build Smoke run `32014319394` (Ubuntu/Windows/macOS including accessibility smoke and packaging preflight), and Security/CodeQL run `32014319291`.
- The documentation explicitly keeps unresolved production gates open: actual measured multi-gigabyte stress, real filesystem exhaustion, real forced-process interruption, representative real-world fidelity, human accessibility, clean-machine packaged-app acceptance, Windows signing, macOS signing/notarization, and other platform distribution verification required for a stable release claim.

## 2026-08-17 — Transaction recovery, stress tooling, accessibility, and output hardening

### Added
- A project-level publication transaction that stages PDF/DOCX outputs and the generated companion index, reports, manifest, optional checksums, and publishing checklist before one final publication boundary.
- Durable publication journals written before final-path mutation. Journals record staged-file size/SHA-256 evidence, previous-output state, and rollback-backup names.
- Explicit interrupted-output recovery through `docmergeforge recover-output --output-dir <path>`.
- Fail-closed recovery logic that restores known rollback backups, removes newly published files only when their fingerprint proves they belong to the interrupted transaction, and refuses destructive recovery when a final path changed after interruption.
- Transaction-state protection that blocks a new journaled publication while unresolved recovery evidence is present.
- Repeated cancellation/recovery regression coverage and simulated interrupted-promotion journal tests.
- Injected `ENOSPC` coverage for atomic output cleanup and preservation of the last published target.
- Output-folder writeability probing before expensive project merge work begins, with a dedicated `OutputAccessError` for destination-access failures.
- A scalable synthetic stress-fixture generator for valid numbered PDF, DOCX, and companion ZIP parts.
- A manually dispatchable stress-acceptance workflow that generates the selected fixture size, validates expected parts, performs project preflight and merge, compares output evidence, records artifact sizes, and uploads the result bundle.
- Explicit accessibility names/descriptions across project setup, source selection, order editing, settings, report viewing, recent projects, and merge progress.
- Keyboard controls for source selection and the order editor, including sorting, move commands, undo/redo, order locking, and restore-auto-order.
- A headless desktop accessibility smoke script exercised by Build Smoke on Ubuntu, Windows, and macOS.

### Changed
- PDF and DOCX cancellation checks now continue through later finalization work instead of occurring only between source documents.
- Mixed PDF/DOCX project runs no longer publish one document format before the other format and its reporting evidence are ready.
- Report-generation failure before publication now leaves the prior publication bundle untouched.
- Promotion writes a durable `promoting` journal before replacing final paths and marks it `committed` only after the whole batch succeeds.
- If automatic rollback itself fails, recovery evidence is deliberately preserved instead of being deleted by context cleanup.
- Build Smoke, Quality, and 120-Part Regression install the required Linux Qt runtime library before importing PySide6 accessibility tests.
- Build Smoke now verifies the accessibility smoke and desktop packaging preflight on its full Ubuntu/Windows/macOS matrix.

### Fixed
- A partial-publication bug where a PDF could already be replaced before a later DOCX failure or cancellation.
- A publication-evidence skew where merged documents could be replaced before report generation failed.
- Late cancellation gaps during PDF overlay/finalization and DOCX finalization.
- Transaction rollback cleanup paths that could otherwise lose recovery evidence after an incomplete rollback.
- A strict-`mypy` type error in journal backup lookup found by final-head Quality CI.
- Ubuntu CI failures caused by PySide6 requiring `libEGL.so.1`; the Linux workflows now install `libegl1` explicitly.
- Late output-permission failures that previously could occur despite a successful free-space estimate.

### Verified CI Evidence
- Hardening checkpoint: `82fe37725a2ae4e71678903c4d67fdff40d819e4`.
- Quality run `32014319266` passed on Python 3.12 and Python 3.13. Ruff, Black, strict `mypy`, and full pytest with coverage all passed on both matrix jobs.
- 120-Part Regression run `32014319264` passed, including generated 120-part fixture creation, regression/integration tests, and CLI validation of Parts 1–120.
- Build Smoke run `32014319394` passed on Ubuntu, Windows, and macOS. Each configured platform completed source compilation, CLI smoke, headless accessibility smoke, and desktop packaging preflight.
- Security run `32014319291` completed CodeQL successfully. Dependency review was skipped because this was a push rather than a pull request.
- Earlier recovery checkpoint `3a38ae64d5a96f76f8557f4443e372c9a4e35871` also passed Quality run `32012033604`, 120-Part Regression run `32012033657`, and Security run `32012033644` before the later journal/accessibility/writeability work was added.

### Remaining Release-Gate Work
- Execute and record an actual multi-gigabyte stress run. The scalable workflow exists, but no multi-gigabyte acceptance claim is made yet.
- Perform a real filled-filesystem/disk-exhaustion acceptance run. Injected `ENOSPC` unit coverage is not the same as filling the destination filesystem.
- Perform real forced-process-termination testing at multiple promotion points and on supported filesystems. Simulated journal states prove recovery logic paths but do not replace killing a real process during promotion.
- Add cross-process single-writer locking if concurrent independent DocMergeForge processes must be prevented from staging/promoting into the same output directory at the same time. The current journal blocks an already-journaled pending transaction but is not represented as a complete multi-process lock.
- Complete production-ready LibreOffice and Microsoft Word high-fidelity DOCX adapters with representative fidelity acceptance. Capability detection alone remains intentionally insufficient.
- Run large real-world manuscript fidelity acceptance with complex styles, sections, tables, images, headers/footers, numbering, links, fields, and other PDF/OOXML structures.
- Complete human keyboard-only, screen-reader, high-contrast, reduced-motion, text-scaling, and localization-readiness acceptance. Automated accessibility metadata/smoke checks are supporting evidence only.
- Exercise real packaged desktop artifacts on their target platforms and complete installer/bundle polish, release-artifact verification, checksums, signing, and macOS notarization before any signed-production claim.
- `v1.0.0` remains gated on the full acceptance matrix; this work does not claim signed/notarized production binaries or stable-release completion.

## 2026-08-16 — Packaging preflight and continuously exercised release gates

### Added
- `validate_build_root()` in `src/docmergeforge/packaging/desktop.py` to fail early when the selected packaging root does not contain the required `pyproject.toml` and desktop entry point.
- `python scripts/build_desktop.py --check` as a packaging preflight command that validates repository layout without importing or running PyInstaller.
- Unit coverage for valid and invalid desktop build roots.
- An integration test that executes the real desktop build script preflight from the repository root and verifies its successful exit/result message.

### Changed
- Build Smoke now runs on pushes to `main`, pull requests, and manual dispatch instead of depending only on pull-request/manual execution.
- Build Smoke now executes the packaging preflight on Ubuntu, Windows, and macOS after installing the declared build dependencies and verifying the CLI/importable source tree.
- 120-Part Regression now runs automatically on pushes to `main` as well as pull requests/manual dispatch, continuously exercising the generated 120-part fixture and CLI validation path.
- Package Desktop now installs the repository-declared `.[build]` extra and runs the same packaging preflight before invoking PyInstaller.
- Packaging configuration remains centralized in the installable application package so tests, smoke checks, and the packaging script share one source of build arguments.

### Fixed
- Quality CI initially rejected the new packaging integration test because its import block did not exactly match Ruff's repository policy. The import layout was corrected without weakening or disabling the lint rule.

### Verified CI Evidence
- Source-code checkpoint: `8cc96d714c43922b0effcbb16400fb2952f056b1`.
- Quality run `31948936694` completed successfully on both Python 3.12 and Python 3.13. Ruff, Black, strict `mypy`, and full pytest with coverage all passed on both matrix jobs.
- 120-Part Regression run `31948936615` completed successfully for the same checkpoint.
- Build Smoke run `31948936667` completed successfully for the same checkpoint across the configured Ubuntu, Windows, and macOS runner matrix.
- Security run `31948936651` completed successfully for the same checkpoint.
- The Package Desktop workflow itself was not executed as part of this checkpoint. Its artifacts remain an unsigned pipeline foundation and are not represented here as production release binaries.

### Release-Gate Status After This Work
- Packaging configuration errors can now be detected before a PyInstaller build begins.
- Cross-platform build-smoke configuration and the 120-part regression path are continuously exercised on `main` pushes.
- This does not satisfy production packaging acceptance by itself. Signed Windows distribution, macOS signing/notarization, installer/bundle acceptance, real packaged-app launch testing, and signature verification remain separate release gates.
- The project remains below `v1.0.0` until the remaining stress, recovery, fidelity, accessibility, and production-distribution acceptance work is verified.

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
- Installable `docmergeforge.packaging` helpers so packaging configuration is shared by scripts and tests.
- Packaging argument tests, legacy DOC conversion safeguard tests, output naming tests, and additional workflow coverage.
- Root-level `what_changed.md` as the development/verification record.

### Changed
- CLI project execution now uses a typed password-provider function rather than an assigned lambda so strict linting/type checks can analyze it cleanly.
- CLI filename filtering was shortened without changing matching behavior so Black and Ruff line-length policies can coexist.
- Logging, DOCX fidelity checks, encrypted-PDF validation, encrypted-PDF UI helpers, desktop workflow code, and output-naming tests were normalized to the repository Black formatting policy.
- Desktop project execution performs preflight before merge and only proceeds when the available document kinds and storage checks are ready.
- Project workflows preserve selected document ordering instead of silently replacing it with a different order at merge time.
- Source-integrity verification remains part of output promotion: source changes detected during merge cause validation failure instead of silently publishing output.
- `scripts/build_desktop.py` now delegates PyInstaller argument construction to `docmergeforge.packaging.desktop`, removing test dependence on repository-root script imports.

### Fixed
- Ruff failures in CLI pattern filtering and assigned-lambda usage.
- Black formatting failures in diagnostics logging, DOCX fidelity validation, encrypted-PDF handling, password dialog code, output naming tests, desktop UI code, and related publication modules.
- Earlier strict `mypy` failures in CLI result typing and DOCX engine integration.
- Pytest collection failure caused by `tests/unit/test_build_desktop.py` importing a repository-only `scripts` module that was not importable in the installed CI environment.
- Earlier source-integrity verification timing so final output is not promoted after a detected input mutation.
- Earlier OOXML relationship/duplicate-ID validation and companion-package integrity issues found by CI-driven development.

### Packaging
- `scripts/build_desktop.py` provides the reproducible PyInstaller build entry point used by the packaging workflow.
- `src/docmergeforge/packaging/desktop.py` is the shared source of PyInstaller build arguments used by packaging scripts and unit tests.
- `.github/workflows/package.yml` provides an unsigned desktop packaging pipeline foundation for supported runner platforms.
- Packaging work must not be interpreted as code signing. No signed Windows, macOS, or Linux binary is claimed.
- Installer/bundle usability, signing/notarization, long-run stress coverage, and release-artifact acceptance still require final verification before a stable release claim.

### Current CI Evidence
- Quality checks run against Python 3.12 and Python 3.13 and include Ruff, Black, strict `mypy`, and pytest with coverage reporting.
- Quality run `31947271551` for commit `e14603dcfa6ae47d3a54d67e32b9ec540cd1bd11` completed successfully on both Python 3.12 and Python 3.13. Ruff, Black, strict `mypy`, and pytest all passed on both matrix jobs.
- Security run `31947271542` for the same commit completed CodeQL successfully. The dependency-review job was skipped because the workflow was triggered by a push rather than a pull request.
- The previously observed pytest collection failure for desktop packaging tests was corrected by moving shared packaging argument generation into the installable application package and updating the test import.
- Earlier Ruff, Black, and mypy failures were fixed with focused commits rather than weakening repository quality settings.
- The project remains intentionally conservative: green source-code CI does not by itself satisfy the stable-release acceptance matrix.

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
- Build Smoke and 120-Part Regression now run automatically on `main` pushes and remain manually dispatchable; Package Desktop remains manually/tag-triggered. Successful smoke/regression runs do not constitute signed production-package acceptance.
- The project continues to enforce the core safety rule: PDF manuscripts may merge with PDF manuscripts and DOCX manuscripts may merge with DOCX manuscripts, while companion/source code remains separate and is never merged into a manuscript.

### Repository / Commit Identity
- Repository: `https://github.com/sanskarIN/DocMergeForge`
- Development commits made through the connected repository use `Sanskar <sanskarin@outlook.in>`.
