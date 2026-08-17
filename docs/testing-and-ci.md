# Testing and CI

DocMergeForge uses layered automated checks because document merging, filesystem publication, desktop UI behavior, packaging, documentation, and security fail in different ways. A green unit-test suite alone is not sufficient release evidence.

## Local quality commands

```bash
ruff check .
black --check --diff .
mypy src/docmergeforge
python scripts/check_docs_links.py
pytest --cov=docmergeforge --cov-report=term-missing
```

## Test categories

### Unit tests

Focused coverage includes part detection/natural sorting, output naming, settings/project serialization, storage/writeability, transaction recovery, cross-process locking, PDF/DOCX helpers, packaging arguments, build provenance, and documentation-link resolution.

### Integration tests

Marked `integration`. They exercise multiple components together, including real PDF/DOCX fixtures, merge flows, CLI behavior, UI metadata, provenance command execution, packaged-entry smoke behavior, and abrupt child-process recovery.

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

`.github/workflows/quality.yml` runs on `main` pushes and pull requests using Python 3.12 and 3.13 on Ubuntu.

It installs developer dependencies plus the Linux Qt runtime and runs:

1. Ruff;
2. Black check;
3. strict mypy;
4. repository-local Markdown link integrity;
5. full pytest with coverage.

## Documentation link integrity

Implementation:

```text
src/docmergeforge/diagnostics/docs_links.py
scripts/check_docs_links.py
tests/unit/test_docs_links.py
```

The scanner walks repository Markdown while ignoring generated/cache directories, checks normal relative Markdown links/images, strips URL fragments, decodes URL-encoded local paths, ignores external schemes/anchor-only links, rejects paths escaping the repository root, and fails on missing local targets.

The logic lives in the installable package rather than being imported from `scripts.*`, so tests and the command wrapper share one implementation.

## 120-Part Regression

`.github/workflows/regression.yml` generates the deterministic SQL Parts 1–120 fixture, runs regression/integration tests, and validates Parts 1–120 through the CLI.

This is strong numbered-part regression evidence but not multi-gigabyte proof.

## Build Smoke

`.github/workflows/build-smoke.yml` runs on Ubuntu, Windows, and macOS and verifies source compilation, CLI availability, accessibility metadata smoke, and packaging preflight. It does not perform the full PyInstaller build.

## Recovery Acceptance

`.github/workflows/recovery-acceptance.yml` uses a real child process and `os._exit()` to interrupt output promotion at three phases on Windows, macOS, and Ubuntu. The parent verifies pending journal evidence, restoration of the previous publication, cleanup, and output-lock reacquisition.

Run `32022863454` passed all three crash phases on all three platforms.

This is controlled process-termination evidence, not physical power-loss/device-removal/network-filesystem proof.

## Disk Full Acceptance

`.github/workflows/disk-full-acceptance.yml` mounts an isolated 32 MiB Ubuntu tmpfs and writes/fsyncs through the real `atomic_output()` path until the kernel returns `ENOSPC`.

The helper verifies the previous published target remains byte-for-byte unchanged and no atomic `.part` residue remains. Corrected run `32023666826` passed.

Other filesystems/platforms remain separate acceptance if claimed.

## Security workflow

`.github/workflows/security.yml` runs CodeQL. Pull-request dependency review remains event-specific and can legitimately skip on ordinary pushes.

## Package Desktop — default onedir

`.github/workflows/package.yml` builds on Windows/macOS/Ubuntu with Python 3.12.

The build-host matrix validates packaging, builds the native onedir application, executes a real packaged PDF+DOCX smoke project, archives it, generates a `.sha256` sidecar, generates privacy-safe provenance bound to archive filename/size/SHA-256, and uploads archive/checksum/provenance.

A second fresh-runner matrix intentionally does not check out the repository or install DocMergeForge/Python project dependencies. It downloads only the uploaded artifact, verifies provenance source/mode/label/trust state/archive filename/size/SHA-256, verifies the checksum sidecar, extracts the archive, and executes packaged smoke again. Linux installs only the documented system `libegl1` runtime.

Archive-bound provenance run `32025126032` at `59107192d494d76a4112cdeaa9a55f01cfe37972` passed the complete build-host + fresh-runner sequence on Windows, macOS, and Ubuntu.

## Onefile Acceptance

`.github/workflows/onefile-acceptance.yml` treats `--one-file` as a separate distribution surface rather than inferring behavior from onedir.

It performs native Windows/macOS/Ubuntu onefile build, packaged PDF+DOCX smoke, archive/checksum/provenance upload, and separate fresh-runner download/provenance/checksum/extract/execute verification.

Archive-bound provenance run `32025167433` at `b8a181b7138a1bc617766dd3e86c9ab32aade75e` passed the complete six-job build-host + fresh-runner matrix on Windows, macOS, and Ubuntu.

## Build provenance tests

Implementation:

```text
src/docmergeforge/packaging/provenance.py
scripts/write_build_provenance.py
tests/unit/test_build_provenance.py
tests/integration/test_build_provenance_cli.py
```

Tests verify privacy allowlisting, invalid mode/label handling, missing-artifact failure, atomic provenance writes, exact archive filename/size/SHA-256 binding, and execution of the real command wrapper.

See [Build Provenance](build/provenance.md).

## Stress Acceptance

`.github/workflows/stress.yml` is manually dispatchable with configurable synthetic scale. It generates fixtures, validates, runs preflight/merge, compares outputs, records sizes, and uploads the result bundle.

No measured multi-gigabyte result is claimed until an actual dispatched run reports source bytes in that class and succeeds.

## Accessibility smoke

```bash
python scripts/check_accessibility.py
```

This checks representative accessible names/descriptions, label buddies, and keyboard metadata offscreen. Human assistive-technology acceptance remains separate.

## Fidelity testing

PDF/DOCX tests cover structural/package behavior, ordering, encryption, sections/styles/numbering/media/relationships/fields, cancellation, source immutability, and output validation where practical.

Portable automated tests cannot prove every Microsoft Word/PDF viewer rendering behavior. Representative real-world human fidelity review remains separate.

## Test-data policy

Use synthetic fixtures whenever possible. Never commit private manuscripts, passwords, tokens, signing keys, or confidential diagnostics. Reduce regressions discovered in private documents to the smallest privacy-safe synthetic structure that reproduces the defect.

## CI debugging policy

When a gate fails, inspect the exact failed step, distinguish environment from application failure, fix the root cause in a focused commit, do not disable the gate merely to make CI green, rerun because later steps may have been skipped, and record evidence only after the relevant checkpoint actually passes.

## Release CI acceptance matrix

Before a stable release candidate, obtain current evidence appropriate to the support statement for Quality, documentation-link integrity, 120-Part Regression, Build Smoke, Recovery Acceptance, filesystem exhaustion, Security/CodeQL, measured Stress, onedir Package Desktop, Onefile Acceptance if distributed, archive-bound provenance/checksum, downloaded-artifact fresh-runner execution, representative fidelity, human accessibility/interactive clean-machine QA, and signing/notarization where claimed.

Do not reuse older run IDs as proof after materially changing the behavior they validated.

## Evidence records

Record significant verified checkpoints in:

```text
CHANGELOG.md
what_changed.md
```

Keep **implemented**, **source-CI verified**, **downloaded-artifact verified**, and **human/production accepted** states distinct.
