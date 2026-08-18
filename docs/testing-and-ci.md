# Testing and CI

DocMergeForge uses layered automated checks because document merging, filesystem publication, desktop UI behavior, packaging, documentation, supply-chain evidence, and security fail in different ways. A green unit-test suite alone is not sufficient release evidence.

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

Focused coverage includes part detection/natural sorting, output naming, settings/project serialization, storage/writeability, transaction recovery, cross-process locking, PDF/DOCX helpers, native DOCX command safety, external-office round-trip adapters, fidelity capability gates/evidence, OOXML risk scanning, packaging arguments, build provenance, and documentation-link resolution.

### Integration tests

Marked `integration`. They exercise multiple components together, including real PDF/DOCX fixtures, merge flows, CLI behavior, fidelity acceptance evidence generation, UI metadata, provenance command execution, packaged-entry smoke behavior, abrupt child-process recovery, and the privacy-safe resource-evidence command runner.

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

`.github/workflows/quality.yml` runs on `main` pushes and pull requests using Python 3.12 and 3.13 on Ubuntu. Per-workflow/ref concurrency cancels stale runs so newer commits do not leave obsolete Quality jobs consuming runner capacity.

It installs developer dependencies plus the Linux Qt runtime and runs:

1. `pre-commit validate-config`;
2. Ruff;
3. Black check;
4. strict mypy;
5. repository-local Markdown link integrity;
6. full pytest with coverage.

Current source checkpoint evidence:

```text
Quality run: 32033541420
Head:        dc624e23d07e0ce94ef345245630d153ee60091a
Python 3.12: PASS
Python 3.13: PASS
```

That recorded checkpoint predates later fidelity changes and must not be reused as proof for them. Record a new run only after the new checkpoint actually passes.

## Documentation link integrity

Implementation:

```text
src/docmergeforge/diagnostics/docs_links.py
scripts/check_docs_links.py
tests/unit/test_docs_links.py
```

The scanner walks repository Markdown while ignoring generated/cache directories, checks relative Markdown links/images, strips URL fragments, decodes URL-encoded local paths, ignores external schemes/anchor-only links, rejects paths escaping the repository root, and fails on missing local targets.

The same command is also exposed as a local pre-commit hook so contributors can catch broken repository-local Markdown links before pushing.

Initial fully green link-check Quality evidence: `32030103104`.

## 120-Part Regression

`.github/workflows/regression.yml` generates the deterministic SQL Parts 1–120 fixture, runs regression/integration tests, and validates Parts 1–120 through the CLI.

This is strong numbered-part regression evidence but not multi-gigabyte proof. Stale per-ref runs are cancelled automatically.

## Build Smoke

`.github/workflows/build-smoke.yml` runs on Ubuntu, Windows, and macOS and verifies source compilation, CLI availability, automated accessibility metadata/preference smoke, and packaging preflight. It does not perform the full PyInstaller build.

Expanded accessibility preference evidence:

```text
Build Smoke run: 32033541402
Windows: PASS
macOS:   PASS
Ubuntu:  PASS
```

The offscreen script now checks representative accessible metadata/shortcuts, real light/dark/system theme application, text-scale clamping/round-trip, and reduced-motion setting round-trip. This remains automated evidence rather than human screen-reader/high-contrast acceptance.

## Recovery Acceptance

`.github/workflows/recovery-acceptance.yml` uses a real child process and `os._exit()` to interrupt output promotion at three phases on Windows, macOS, and Ubuntu. The parent verifies pending journal evidence, restoration of the previous publication, cleanup, and output-lock reacquisition.

Run `32022863454` passed all three crash phases on all three platforms.

This is controlled process-termination evidence, not physical power-loss/device-removal/network-filesystem proof.

## Disk Full Acceptance

`.github/workflows/disk-full-acceptance.yml` mounts an isolated 32 MiB Ubuntu tmpfs and writes/fsyncs through the real `atomic_output()` path until the kernel returns `ENOSPC`.

Corrected run `32023666826` passed while preserving the previous target and cleaning atomic `.part` residue.

Other filesystems/platforms remain separate acceptance if claimed.

## DOCX Fidelity Acceptance

`.github/workflows/fidelity-acceptance.yml` is a dedicated external-office acceptance lane. It runs automatically on relevant `main` changes and can also be manually dispatched.

The current Ubuntu job:

1. installs LibreOffice Writer;
2. installs DocMergeForge plus development dependencies;
3. runs `docmergeforge fidelity-capabilities` so availability and production-readiness remain visibly separate;
4. runs focused native-command, LibreOffice, Word-boundary, capability, acceptance-evidence, and OOXML-risk tests;
5. executes `scripts/check_docx_fidelity_acceptance.py --mode libreoffice` against a generated DOCX fixture;
6. prints the measured JSON evidence;
7. uploads the source DOCX, LibreOffice round-trip DOCX, and evidence JSON.

The synthetic fixture includes a heading, formatted text, bullet paragraphs, a table, and section header/footer content.

A passing run demonstrates that the tested LibreOffice build on that Linux runner could open/re-save the fixture and preserve the measured structural snapshot without introducing a new risk category. It does **not** certify complete multi-document native merge behavior, visual identity, Windows/macOS LibreOffice behavior, or Microsoft Word.

Microsoft Word acceptance requires a controlled Windows host where Word is actually installed. PowerShell detection alone is not Word evidence.

See [DOCX Fidelity Adapters and Acceptance](docx-fidelity-acceptance.md).

## Security workflow

`.github/workflows/security.yml` uses `actions/dependency-review-action@v5` for pull requests and `github/codeql-action@v4` for CodeQL. Per-ref concurrency cancels stale runs.

Action-generation migration evidence: Security run `32030403035` passed CodeQL v4; dependency review correctly skipped on its push event.

## Package Desktop — default onedir

`.github/workflows/package.yml` builds on Windows/macOS/Ubuntu with Python 3.12.

The current build-host matrix:

- validates packaging configuration;
- builds the native onedir application;
- executes a real packaged PDF+DOCX smoke project;
- archives it and creates `.sha256`;
- creates archive-bound privacy-safe JSON provenance;
- generates a validated CycloneDX 1.6 build-environment dependency SBOM;
- creates signed GitHub/Sigstore build-provenance and CycloneDX SBOM attestations;
- uploads archive/checksum/provenance/SBOM.

The fresh-runner matrix downloads only the uploaded artifact and independently verifies:

1. default GitHub build provenance;
2. predicate type `https://cyclonedx.org/bom`;
3. archive-bound JSON provenance;
4. `.sha256` sidecar;
5. extraction;
6. packaged mixed PDF+DOCX smoke.

Current CycloneDX evidence:

```text
Package Desktop run: 32033135355
Checkpoint:          59dc14bbf1d4301177e475ac350694bdd9d90ada
All 6 jobs:          PASS
```

## Onefile Acceptance

`.github/workflows/onefile-acceptance.yml` treats `--one-file` as a separate distribution surface and applies the same archive/checksum/provenance/CycloneDX/two-attestation/fresh-runner verification model.

Current CycloneDX evidence:

```text
Onefile Acceptance run: 32033541414
Checkpoint:              dc624e23d07e0ce94ef345245630d153ee60091a
All 6 jobs:              PASS
```

The CycloneDX file describes the Python build environment used by PyInstaller. It is not represented as a byte-perfect post-bundling component inventory.

## Build provenance and SBOM tooling

DocMergeForge provenance implementation:

```text
src/docmergeforge/packaging/provenance.py
scripts/write_build_provenance.py
tests/unit/test_build_provenance.py
tests/integration/test_build_provenance_cli.py
```

CycloneDX build tooling is pinned in the build extra as `cyclonedx-bom==7.3.1` and generates CycloneDX 1.6 JSON through `cyclonedx-py environment`.

See [Build Provenance](build/provenance.md) and [Release Evidence Ledger](release-evidence.md).

## Stress Acceptance

`.github/workflows/stress.yml` supports automatic default-baseline execution when stress infrastructure changes and configurable manual scaling.

The workflow generates fixtures, validates Parts 1–N, creates a project, runs preflight, wraps the real merge with `scripts/run_with_resource_evidence.py`, compares outputs, writes JSON/Markdown evidence, records sizes, and uploads the result bundle.

Verified formatter-clean telemetry run:

```text
Run:        32032403859
Checkpoint: 73a79a763ef7c363964b1808ddb9e3156785e2f9
Source:     9,881,006 bytes
Elapsed:    16.744248664 s
Peak RSS:   169,193,472 bytes
```

See [Stress Testing](stress-testing.md) for the full resource counters. This ~9.9 MB source baseline is not multi-gigabyte acceptance.

## Accessibility smoke

```bash
python scripts/check_accessibility.py
```

It verifies representative accessible names/descriptions, label buddies, keyboard metadata, theme application, text-scale behavior, and reduced-motion preference round-trip offscreen. Human assistive-technology and real OS high-contrast acceptance remain separate.

## GitHub Actions maintenance

Current workflow generations include:

- checkout/setup-python v7;
- upload-artifact v7;
- download-artifact v8;
- dependency-review v5;
- CodeQL v4;
- `actions/attest@v4`.

Weekly Dependabot PRs are enabled for GitHub Actions and pip dependencies. They are reviewable update proposals, not auto-merges.

## Fidelity testing

PDF/DOCX tests cover structural/package behavior, ordering, encryption, sections/styles/numbering/media/relationships/fields, cancellation, source immutability, output validation, native command failures/timeouts, external-office source preservation, capability gating, measured round-trip evidence, and risky OOXML construct detection where practical.

Portable and external-office automated tests still cannot prove every Microsoft Word/LibreOffice/PDF viewer rendering behavior. Representative real-world human fidelity review remains separate.

## Test-data and evidence privacy

Use synthetic fixtures whenever possible. Never commit private manuscripts, passwords, tokens, signing keys, or confidential diagnostics. Resource telemetry intentionally avoids serializing full command arguments/environment. Reduce regressions discovered in private documents to the smallest privacy-safe synthetic structure that reproduces the defect.

## CI debugging policy

When a gate fails, inspect the exact failed step, distinguish environment from application failure, fix the root cause in a focused commit, do not disable the gate merely to make CI green, rerun because later steps may have been skipped, and record evidence only after the relevant checkpoint actually passes.

## Release CI acceptance matrix

Before a stable release candidate, obtain current evidence appropriate to the support statement for Quality, pre-commit configuration, documentation-link integrity, 120-Part Regression, Build Smoke, Recovery Acceptance, filesystem exhaustion, Security/CodeQL, measured Stress, DOCX external-office fidelity where claimed, onedir Package Desktop, Onefile Acceptance if distributed, archive checksum/provenance, both signed attestation predicates, downloaded-artifact fresh-runner execution, representative fidelity, human accessibility/interactive clean-machine QA, and signing/notarization where claimed.

Do not reuse older run IDs as proof after materially changing the behavior they validated.

## Evidence records

Record significant verified checkpoints in:

```text
CHANGELOG.md
what_changed.md
docs/release-evidence.md
```

Keep **implemented**, **source-CI verified**, **external-application measured**, **downloaded-artifact verified**, and **human/production accepted** states distinct.
