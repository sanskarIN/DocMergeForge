# Testing and CI

DocMergeForge uses layered automated checks because document merging, filesystem publication, desktop UI behavior, packaging, documentation, supply-chain evidence, external-office automation, and security fail in different ways. A green unit-test suite alone is not sufficient release evidence.

## Local quality commands

```bash
pre-commit validate-config
ruff check .
black --check --diff .
mypy src/docmergeforge
python scripts/check_docs_links.py
pytest --cov=docmergeforge --cov-report=term-missing
```

## Test categories

### Unit tests

Focused coverage includes part detection/natural sorting, output naming, settings/project serialization, storage/writeability, transaction recovery, cross-process locking, PDF/DOCX helpers, native DOCX command safety, external-office round-trip adapters, fidelity capability gates/evidence, OOXML risk scanning, Microsoft Word native-merge boundaries, page-number section evidence, exact Word process cleanup, cleanup-failure escalation, packaging arguments, build provenance, and documentation-link resolution.

### Integration tests

Marked `integration`. They exercise multiple components together, including real PDF/DOCX fixtures, merge flows, CLI behavior, fidelity evidence generation, Word merge/timeout acceptance harness behavior through mocked external-process boundaries, UI metadata, provenance command execution, packaged-entry smoke behavior, abrupt child-process recovery, and privacy-safe resource evidence.

```bash
pytest -m integration
```

### Regression tests

Marked `regression`. They protect larger previously working scenarios, including generated multi-part publications.

```bash
pytest -m regression
pytest -m "regression or integration" tests/regression tests/integration
```

## Quality workflow

`.github/workflows/quality.yml` runs on `main` pushes and pull requests using Python 3.12 and 3.13 on Ubuntu. Per-workflow/ref concurrency cancels stale runs.

It runs pre-commit configuration validation, Ruff, Black check, strict mypy, repository-local Markdown link integrity, and full pytest with coverage.

Historical source checkpoint evidence:

```text
Quality run: 32033541420
Head:        dc624e23d07e0ce94ef345245630d153ee60091a
Python 3.12: PASS
Python 3.13: PASS
```

That checkpoint predates the current Word-native/page-number/process-cleanup/timeout-harness work and must not be reused as proof for the current head. Record a new run only after it actually passes.

## Documentation link integrity

Implementation:

```text
src/docmergeforge/diagnostics/docs_links.py
scripts/check_docs_links.py
tests/unit/test_docs_links.py
```

The scanner walks repository Markdown while ignoring generated/cache directories, checks relative Markdown links/images, strips URL fragments, decodes URL-encoded local paths, ignores external schemes/anchor-only links, rejects paths escaping the repository root, and fails on missing local targets.

Initial fully green link-check Quality evidence: `32030103104`.

## 120-Part Regression

`.github/workflows/regression.yml` generates the deterministic SQL Parts 1–120 fixture, runs regression/integration tests, and validates Parts 1–120 through the CLI. This is numbered-part regression evidence, not multi-gigabyte proof.

## Build Smoke

`.github/workflows/build-smoke.yml` runs on Ubuntu, Windows, and macOS and verifies source compilation, CLI availability, automated accessibility metadata/preference smoke, and packaging preflight. It does not perform the full PyInstaller build.

Historical accessibility preference evidence:

```text
Build Smoke run: 32033541402
Windows: PASS
macOS:   PASS
Ubuntu:  PASS
```

Human screen-reader/high-contrast acceptance remains separate.

## Recovery Acceptance

`.github/workflows/recovery-acceptance.yml` uses a real child process and `os._exit()` to interrupt output promotion at three phases on Windows, macOS, and Ubuntu. Run `32022863454` passed all three crash phases on all three platforms.

This is controlled process-termination evidence, not physical power-loss/device-removal/network-filesystem proof.

## Disk Full Acceptance

`.github/workflows/disk-full-acceptance.yml` mounts an isolated 32 MiB Ubuntu tmpfs and writes/fsyncs through the real `atomic_output()` path until the kernel returns `ENOSPC`. Corrected run `32023666826` passed while preserving the previous target and cleaning atomic `.part` residue.

Other filesystems/platforms remain separate acceptance if claimed.

## DOCX Fidelity Acceptance

`.github/workflows/fidelity-acceptance.yml` runs automatically on relevant `main` changes and is also manually dispatchable.

The Ubuntu lane:

1. installs LibreOffice Writer;
2. installs DocMergeForge development dependencies;
3. reports `fidelity-capabilities` so availability/automation/production states stay distinct;
4. runs native-command, LibreOffice, Word round-trip, Word native-merge, exact-process-cleanup, cleanup-failure, section/page-number, source-revision, timeout-harness, corpus, workflow-policy, environment/process-script, CLI, and OOXML-risk tests;
5. executes a **real LibreOffice Writer** synthetic DOCX round trip;
6. prints measured JSON evidence; and
7. uploads source/output/evidence artifacts.

The Word-related tests in this Linux lane validate Python, OOXML parsing, generated PowerShell, process policy, timeout-harness behavior, and acceptance logic with mocked external execution. They do **not** claim Microsoft Word ran on Linux.

A passing LibreOffice lane still does not certify complete native multi-document LibreOffice behavior or universal visual equivalence.

See [DOCX Fidelity Adapters and Acceptance](docx-fidelity-acceptance.md).

## Microsoft Word Native Acceptance

`.github/workflows/word-native-acceptance.yml` is a separate **manual-only** workflow requiring a controlled self-hosted Windows x64 runner with the custom label:

```text
docmergeforge-word
```

Runner selector:

```yaml
runs-on: [self-hosted, Windows, X64, docmergeforge-word]
```

The host must have Microsoft Word actually installed/licensed/configured for the controlled test and must not contain confidential test content unless the repository/artifact-retention policy explicitly permits it.

### Capability policy

The workflow writes `fidelity-capabilities.json` and requires:

```text
word.automation_ready = true
word.production_ready = false
```

It deliberately fails if Word has been marked production-ready before certification.

### Clean host/process policy

Before acceptance, `scripts/check_word_process_state.ps1` writes `word-process-before.json` and rejects any pre-existing `WINWORD` process. This prevents acceptance automation from being confused with an operator's unrelated Word session.

After the normal merge and timeout-cleanup stages, it writes `word-process-after.json` and rejects leftover `WINWORD` state. The broad process-state guard is detection-only and never kills unknown Word processes.

The native merge and timeout harness separately record their own Word PID, `WINWORD` name, and process start-time fingerprint. `src/docmergeforge/docx/word_process.py` permits forced cleanup only when all three still match. PID reuse/mismatches fail closed.

### Measured Word merge evidence

The deterministic normal merge smoke uses two distinct sources. It measures aggregate structure, privacy-safe body/table/header/footer text, section layout/linkage, page-number section semantics, source hashes, and OOXML risk categories.

The second source deliberately differs from the first in orientation, margins, header/footer distances, and numbering. Numbering uses:

```text
Source 1: start=1, format=decimal
Source 2: start=7, format=upperRoman
```

The page-number parser currently measures `w:start`, `w:fmt`, `w:chapStyle`, and `w:chapSep` for every section. Source-document boundaries are normalized into one global section sequence so multiple source DOCX files can compare meaningfully with one merged output DOCX.

Source hashes are captured before expected snapshots and checked after expected evidence, after Word execution, and again after output evidence. Mixed-revision evidence therefore fails closed.

### Controlled timeout-cleanup evidence

After the normal Word smoke passes, the controlled workflow executes:

```text
scripts/check_word_timeout_cleanup_acceptance.py
```

The harness intentionally holds an invisible Word COM session longer than `timeout_cleanup_seconds`, requires the native command to time out, requires exact Word identity to have been captured before timeout, invokes exact-instance cleanup, and writes:

```text
word-timeout-process-identity.json
word-timeout-cleanup-evidence.json
```

Evidence distinguishes natural Word exit from exact-process forced termination. Either can be a valid cleanup outcome as long as exact identity is verified and cleanup succeeds. A non-timeout Word error, missing identity, identity mismatch, or cleanup failure is rejected.

See [Microsoft Word Timeout Cleanup Acceptance](word-timeout-cleanup-acceptance.md).

### Controlled workflow sequence

The workflow records Windows/Word environment metadata, records/verifies capability policy, requires clean pre-Word state, runs Word boundary/evidence/process/timeout-harness tests, executes the real COM merge smoke, executes the real timeout-cleanup harness, requires clean post-Word state, displays available normal/timeout evidence, uploads it even after measured failure, and finally fails unless pre-state, merge smoke, timeout cleanup, and post-state all passed.

Defining the workflow is not proof it ran. Do not cite Word normal or timeout acceptance until a real self-hosted run ID and its evidence have been reviewed.

See [Microsoft Word Native Merge Acceptance](word-native-merge-acceptance.md).

## Security workflow

`.github/workflows/security.yml` uses `actions/dependency-review-action@v5` for pull requests and `github/codeql-action@v4` for CodeQL. Historical action-generation migration evidence: Security run `32030403035` passed CodeQL v4; dependency review skipped on its push event.

## Package Desktop — default onedir

`.github/workflows/package.yml` builds on Windows/macOS/Ubuntu with Python 3.12. The build-host matrix validates packaging, builds the application, executes a real packaged PDF+DOCX smoke, archives it, writes `.sha256`, creates archive-bound JSON provenance and a CycloneDX build-environment SBOM, creates signed GitHub/Sigstore attestations, and uploads evidence.

Fresh runners download only the artifact and independently verify provenance/attestation predicates, sidecar hash, extraction, and packaged mixed-document smoke.

Historical CycloneDX evidence:

```text
Package Desktop run: 32033135355
Checkpoint:          59dc14bbf1d4301177e475ac350694bdd9d90ada
All 6 jobs:          PASS
```

## Onefile Acceptance

`.github/workflows/onefile-acceptance.yml` treats `--one-file` as a separate distribution surface and applies the same archive/checksum/provenance/CycloneDX/two-attestation/fresh-runner model.

Historical evidence:

```text
Onefile Acceptance run: 32033541414
Checkpoint:              dc624e23d07e0ce94ef345245630d153ee60091a
All 6 jobs:              PASS
```

The CycloneDX file describes the Python build environment used by PyInstaller; it is not represented as a byte-perfect post-bundling component inventory.

## Build provenance and SBOM tooling

```text
src/docmergeforge/packaging/provenance.py
scripts/write_build_provenance.py
tests/unit/test_build_provenance.py
tests/integration/test_build_provenance_cli.py
```

CycloneDX build tooling is pinned in the build extra and generates CycloneDX 1.6 JSON. See [Build Provenance](build/provenance.md) and [Release Evidence Ledger](release-evidence.md).

## Stress Acceptance

`.github/workflows/stress.yml` supports automatic baseline execution when stress infrastructure changes and configurable manual scaling. It generates fixtures, validates parts, runs preflight/merge/compare, records resource evidence and sizes, and uploads results.

Historical formatter-clean telemetry:

```text
Run:        32032403859
Checkpoint: 73a79a763ef7c363964b1808ddb9e3156785e2f9
Source:     9,881,006 bytes
Elapsed:    16.744248664 s
Peak RSS:   169,193,472 bytes
```

This ~9.9 MB source baseline is not multi-gigabyte acceptance.

## Accessibility smoke

```bash
python scripts/check_accessibility.py
```

It verifies representative accessible metadata, label buddies, keyboard metadata, theme application, text-scale behavior, and reduced-motion preference round-trip offscreen. Human assistive-technology and real OS high-contrast acceptance remain separate.

## GitHub Actions maintenance

Current workflow generations include checkout/setup-python v7, upload-artifact v7, download-artifact v8, dependency-review v5, CodeQL v4, and `actions/attest@v4`. Weekly Dependabot PRs are enabled for Actions and pip dependencies without automatic merging.

## Fidelity testing

PDF/DOCX tests cover structural/package behavior, ordering, encryption, sections/styles/numbering/media/relationships/fields, cancellation, source immutability, output validation, external-office command failures/timeouts, capability gating, measured round-trip evidence, Word native-merge boundaries, section/linkage fingerprints, page-number section semantics, source-revision binding, exact-process cleanup, controlled timeout cleanup, cleanup-failure escalation, private-corpus behavior, and risky OOXML constructs where practical.

Automated tests still cannot prove every Microsoft Word/LibreOffice/PDF viewer rendering decision. Representative real-world human fidelity review remains separate.

## Test-data and evidence privacy

Use synthetic fixtures whenever possible. Never commit private manuscripts, passwords, tokens, signing keys, or confidential diagnostics. Reduce private-document regressions to the smallest privacy-safe synthetic structure that reproduces the defect.

The controlled Word workflow uploads generated synthetic DOCX/evidence/environment/capability/process-state/timeout-cleanup data. Exact Word process identity files contain process-control values, not manuscript text, but should still be treated as technical acceptance evidence rather than publication output.

## CI debugging policy

When a gate fails, inspect the exact failed step, distinguish environment from application failure, fix the root cause in a focused commit, do not disable a gate merely to make CI green, rerun because later steps may have been skipped, and record evidence only after the relevant checkpoint actually passes.

## Release CI acceptance matrix

Before a stable release candidate, obtain current evidence appropriate to each support statement for Quality, documentation-link integrity, 120-Part Regression, Build Smoke, Recovery Acceptance, filesystem exhaustion, Security/CodeQL, measured Stress, external-office fidelity, controlled Microsoft Word native merge acceptance where claimed, controlled Word timeout-cleanup acceptance where claimed, Package Desktop/Onefile where distributed, checksums/provenance/attestations, fresh-runner execution, representative fidelity, human accessibility/clean-machine QA, and signing/notarization where claimed.

Do not reuse older run IDs as proof after materially changing the behavior they validated.

## Evidence records

Record verified checkpoints in:

```text
CHANGELOG.md
what_changed.md
docs/release-evidence.md
```

Keep **implemented**, **source-CI verified**, **external-application measured**, **downloaded-artifact verified**, and **human/production accepted** states distinct.
