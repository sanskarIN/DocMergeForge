# Changelog

All notable changes follow semantic versioning.

## [Unreleased]

### Documentation
- Added a dedicated `docs/build/` executable-build manual with a central portal, shared environment/build procedure, complete Windows/macOS/Linux native build guides, CI packaging reference, signing/notarization requirements, packaged-app verification matrix, build troubleshooting, and release go/no-go checklist.
- Converted `docs/building-executables.md` into the canonical entry point for the complete executable manual and linked all build guides from `docs/README.md`.
- Added a canonical `docs/README.md` documentation portal covering the complete user, operator, contributor, architecture, engine, safety, packaging, and release documentation set.
- Added complete installation, getting-started, desktop-user, CLI-reference, project-file, discovery/ordering, validation/preflight, output-artifact, publication-recovery, companion-code, audit/compare, settings, diagnostics, security, accessibility, development, testing/CI, executable-building, release-process, operator-runbook, FAQ, glossary, support, and known-limitations guides.
- Added `docs/release-evidence.md` as the canonical verification ledger for source-CI, recovery, storage, executable, provenance, stress, and remaining production-gate evidence.
- Expanded the existing architecture, PDF engine, DOCX engine, privacy, release-packaging, SQL Full Mastery preset, troubleshooting, and stress-testing documentation to match the current implementation.
- Expanded the root README with the complete documentation portal, recovery/build/release-status guidance, and corrected high-fidelity wording so unfinished external office-suite adapters are not represented as production-ready.
- Expanded `CONTRIBUTING.md` with development/test/documentation/accessibility/recovery contribution requirements and linked it to the full developer documentation.
- Expanded `SECURITY.md` with privacy-safe vulnerability-reporting guidance and links to the security/privacy/diagnostics documentation.
- Documentation now distinguishes implemented behavior, automatically verified behavior, downloaded-artifact verification, and human/production acceptance; unsigned builds, unfinished high-fidelity adapters, measured multi-gigabyte stress, clean-machine acceptance, and human accessibility remain explicit release gates until verified.
- Expanded publication-recovery documentation with the persistent lock filename, OS-owned lock semantics, concurrent recovery protection, crash-release behavior, and network-filesystem caveat.
- Expanded CI packaging documentation with packaging-relevant `main` triggers, real packaged PDF/DOCX publication smoke, native `.app` handling, archive SHA-256 sidecars, archive-bound provenance, and per-platform fresh-runner evidence requirements.
- Expanded testing/development-phase documentation with cross-platform abrupt-process recovery acceptance and real Linux tmpfs `ENOSPC` acceptance.
- Updated stress documentation with the first measured automated 120-part baseline, exact source/output byte evidence, and the explicit distinction between the verified ~9.9 MB baseline and still-unverified multi-gigabyte scale.
- Expanded the Microsoft Word native-merge acceptance guide, testing/CI guide, known-limitations guide, and root README with measured section/page-number fidelity, source-revision binding, exact-process cleanup, controlled-runner policy, and explicit remaining external acceptance gates.

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
- Scalable synthetic stress-fixture generation plus Stress Acceptance automation with validation, preflight, merge, comparison, measured byte evidence, job-summary reporting, and artifact upload.
- Explicit accessibility metadata and keyboard controls across project setup, source selection, file ordering, settings, reports, recent projects, and merge progress, with headless automated accessibility smoke coverage.
- Cross-process output-directory publication locking shared by normal publication and interrupted-output recovery.
- A PyInstaller-only packaged desktop entry with deterministic `--packaged-smoke` initialization for CI acceptance.
- Packaged smoke now creates and merges a real one-part PDF and DOCX, validating manuscript artifacts, manifest, and checksum generation inside the PyInstaller binary.
- `Recovery Acceptance` workflow that kills a real child process with `os._exit()` at three promotion phases on Windows, macOS, and Ubuntu and verifies deterministic rollback/re-locking.
- `Disk Full Acceptance` workflow and safety-guarded helper that fill an isolated 32 MiB Linux tmpfs until the kernel returns real `ENOSPC`, then verify the previous target and atomic cleanup.
- SHA-256 sidecar generation and upload for each unsigned Windows/macOS/Linux Package Desktop archive.
- Privacy-safe archive-bound build provenance plus fresh-runner source/build/archive digest verification for onedir and onefile packages.
- Repository-local Markdown link integrity checking in Quality CI, backed by unit tests and a thin command wrapper.
- Weekly Dependabot update PRs for GitHub Actions and Python dependencies, without automatic merging.
- GitHub Artifact Attestations support for default onedir archives using `actions/attest@v4`; final acceptance remains recorded only after the complete attestation/fresh-runner workflow passes.
- Unit/integration coverage for output locking, transaction/recovery exclusion, packaging-entry selection, packaged desktop smoke initialization/publication, provenance, documentation links, and forced-process recovery.
- Microsoft Word native multi-document acceptance prototype using ordered `Range.InsertFile(...)`, real next-page/continuous section boundaries, validated temporary output, source hash protection, and a manual controlled self-hosted Windows acceptance workflow.
- Privacy-safe Word native acceptance evidence for visible text, section layout/linkage, page-number section semantics, OOXML risk categories, and source revision identity.
- Exact Word process identity cleanup using PID, `WINWORD` name, and start-time fingerprint, with natural-exit grace handling and PID-reuse protection.
- Deterministic Word smoke fixtures with portrait/landscape geometry, distinct margins/header/footer distances, and decimal/upper-Roman page-number restart semantics.

### Changed
- Centralized desktop packaging argument generation inside the installable `docmergeforge.packaging` package so builds and tests share the same configuration.
- Strengthened ordering, source-integrity, formatting, strict typing, documentation-link integrity, provenance, and CI validation paths.
- PDF and DOCX engines now check cancellation through later finalization stages instead of only between source documents.
- Project merge completion now has one publication boundary: document outputs and generated evidence are promoted only after all staged work succeeds and source integrity is revalidated.
- Publication promotion now writes a `promoting` journal before final-path mutation and a `committed` marker only after the complete batch succeeds; incomplete rollback evidence is preserved instead of silently deleted.
- New journaled output transactions refuse to start while interrupted recovery evidence is pending.
- Publication and recovery now hold the same OS-level non-blocking output-directory lock for the complete critical section.
- Build Smoke now runs on `main` pushes as well as pull requests/manual dispatch and validates desktop packaging configuration on Ubuntu, Windows, and macOS runners.
- Build Smoke also runs the headless desktop accessibility smoke check on each configured desktop runner.
- The 120-Part Regression workflow now runs on `main` pushes in addition to pull requests/manual dispatch.
- Package Desktop installs the declared `build` extra and validates packaging configuration before invoking PyInstaller.
- Package Desktop now launch-tests the freshly built native application, executes a tiny mixed PDF+DOCX publication, archives it, records checksum/provenance, and independently re-verifies the downloaded artifact on a fresh native runner.
- Onefile Acceptance now independently applies the same build-host plus fresh-runner verification model to `--one-file` packages.
- Package Desktop runs on packaging/UI changes to `main`, while retaining manual and `v*` tag triggers.
- Linux package jobs install the required Qt/EGL runtime and macOS archiving handles the native `DocMergeForge.app` layout.
- The shared PyInstaller entry now uses `src/docmergeforge/ui/packaged_entry.py` while normal `docmergeforge-gui` behavior continues to use the existing desktop main entry point.
- GitHub Actions workflows were migrated to the current Node 24-era major generations: checkout/setup-python v7, upload-artifact v7, download-artifact v8, dependency-review v5, and CodeQL v4.
- Stress Acceptance now automatically exercises the default 120-part profile when stress infrastructure changes on `main` while retaining configurable manual dispatch for larger workloads.
- Word native merge acceptance now binds expected/output evidence to one global section sequence, compares section/page-number fingerprints, rechecks source hashes across evidence construction and native execution, and rejects a nominal success when Word required forced process termination.
- The Linux fidelity workflow now executes the complete Word boundary regression surface without claiming Word execution; the manual Word workflow now requires capability-policy evidence plus clean pre/post Word process state.

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
- Concurrent independent DocMergeForge processes racing publication or recovery in the same output directory.
- The macOS package workflow assumption that the output always used the Windows/Linux `dist/DocMergeForge` directory instead of a native `.app` bundle.
- Linux-only mypy incompatibility with direct Windows `msvcrt.locking` references by introducing a typed platform adapter.
- Strict Ruff `SIM117`, line-length, and python-docx path typing issues found while adding new acceptance harnesses, without weakening repository rules.
- Two Ruff E501 failures in the Markdown-link checker that previously prevented Quality from reaching Black, mypy, link validation, and pytest.
- Word native multi-document insertion no longer uses a plain page-break constant; later sources now receive explicit Word section boundaries so section-specific properties have a preservation boundary.
- Page-number evidence no longer encodes source-document indices that cannot exist in the single merged output; it uses global section order instead.
- Word process cleanup now accepts Windows PowerShell UTF-8 BOM identity files, rechecks exact identity after a natural-exit grace period, and never broad-kills unrelated Word sessions.
- A broken acceptance-test contract where page-number regression tests referenced section/page-number evidence fields that the implementation did not yet provide.

### Validation
- Commit `8cc96d714c43922b0effcbb16400fb2952f056b1` passed Quality run `31948936694`, 120-Part Regression `31948936615`, Build Smoke `31948936667`, and Security `31948936651`.
- Recovery checkpoint `3a38ae64d5a96f76f8557f4443e372c9a4e35871` passed Quality `32012033604`, 120-Part Regression `32012033657`, and Security `32012033644`.
- Hardening checkpoint `82fe37725a2ae4e71678903c4d67fdff40d819e4` passed Quality `32014319266`, 120-Part Regression `32014319264`, Build Smoke `32014319394`, and Security/CodeQL `32014319291`.
- Cross-process lock checkpoint `4785dc8386b92921be2117e5eb5f0b7f9aadce2a` passed Quality `32022625007`, 120-Part Regression `32022625013`, Build Smoke `32022625036`, and Security/CodeQL `32022625128`.
- Recovery Acceptance run `32022863454` passed three real abrupt `os._exit()` promotion phases on Windows, macOS, and Ubuntu and restored the prior publication in every case.
- Package Desktop archive-bound provenance run `32025126032` passed all Windows/macOS/Ubuntu build-host and fresh-runner jobs.
- Onefile Acceptance archive-bound provenance run `32025167433` passed all Windows/macOS/Ubuntu build-host and fresh-runner jobs.
- Disk Full Acceptance corrected run `32023666826` passed on Ubuntu using an isolated 32 MiB tmpfs and a real kernel `ENOSPC`, preserving the previous target and cleaning atomic `.part` residue.
- Documentation-link Quality run `32030103104` passed Ruff, Black, strict mypy, Markdown link validation, and full pytest on Python 3.12 and 3.13.
- Node 24-era action migration Package Desktop run `32030446110` at checkpoint `29c6ed8a480731094bb5c629a22f889b9fd9cacd` passed all Windows/macOS/Ubuntu build-host and fresh-runner jobs.
- Node 24-era action migration Onefile Acceptance run `32030487166` at checkpoint `24674b776216e6da73c257b30149f46605eb1b77` passed all Windows/macOS/Ubuntu build-host and fresh-runner jobs.
- Measured Stress Acceptance run `32030895119` at checkpoint `ad5d8e354efefc745a454b799632359fafd29658` passed generation, Parts 1–120 validation, preflight, mixed merge, and compare using 120 PDF + 120 DOCX parts, 600 PDF pages, `9,881,006` measured source bytes, and `5,421,739` measured output bytes before evidence files. Artifact ID `9288923591`; container digest `sha256:f552c3007dc6121f77145e9335f4ca39a7a3809bb4a97eb98c4118f2f2529189`.
- The measured stress baseline is approximately 9.9 MB and is deliberately **not** represented as multi-gigabyte acceptance.
- No new passing Quality/Fidelity/controlled-Word run is recorded for the current Word-native hardening until such a run is actually observable. The controlled Word workflow exists, but a workflow definition is not acceptance evidence.
- These checks do not claim signed installers, macOS notarization, full human clean-machine interactive package acceptance, physical power-loss/device-removal recovery, network-filesystem locking semantics, full human accessibility acceptance, universal high-fidelity DOCX support, or `v1.0.0` readiness.

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
