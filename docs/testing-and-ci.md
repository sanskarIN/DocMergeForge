# Testing and CI

DocMergeForge uses layered automated checks because document merging, desktop UI behavior, filesystem transactions, packaging, and security each fail in different ways. A green unit-test suite alone is not sufficient evidence for a release.

## Local quality commands

```bash
ruff check .
black --check --diff .
mypy src/docmergeforge
pytest --cov=docmergeforge --cov-report=term-missing
```

## Test categories

### Unit tests

Focused examples include:

- part detection/natural sorting;
- output naming;
- settings/project serialization;
- storage/writeability handling;
- transaction journal validation/recovery;
- cross-process output locking;
- PDF/DOCX helper behavior;
- packaging argument generation.

### Integration tests

Marked `integration`. They exercise multiple components/document libraries together, including real PDF/DOCX fixtures, merge flows, UI metadata, CLI behavior, packaging smoke behavior, and abrupt child-process recovery.

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

`.github/workflows/quality.yml` runs on pushes to `main` and pull requests using Python 3.12 and 3.13 on Ubuntu.

It runs:

1. checkout;
2. Python/pip cache setup;
3. Linux `libegl1` installation;
4. developer dependency install;
5. Ruff;
6. Black check;
7. strict mypy;
8. full pytest with coverage.

## 120-Part Regression

`.github/workflows/regression.yml` runs on `main`, pull requests, and manual dispatch. It generates the deterministic 120-part SQL fixture, runs regression/integration tests, and validates Parts 1–120 through the CLI.

This is strong numbered-part regression evidence, but a normal generated fixture is not automatically multi-gigabyte acceptance.

## Build Smoke

`.github/workflows/build-smoke.yml` runs on Ubuntu, Windows, and macOS with Python 3.12. It checks:

- source compilation;
- CLI availability;
- desktop accessibility metadata smoke;
- desktop packaging preflight.

Build Smoke does not invoke the complete PyInstaller package build.

## Recovery Acceptance

`.github/workflows/recovery-acceptance.yml` is a dedicated cross-platform filesystem/recovery gate.

It runs on Windows, macOS, and Ubuntu when transaction/recovery/lock acceptance files change, plus manual dispatch.

The acceptance test starts a real child Python process that owns an `OutputTransaction`, writes a durable `promoting` journal, mutates real final paths, and then terminates abruptly with `os._exit()` so ordinary Python context-manager cleanup cannot run.

Current crash phases are:

1. **after first backup** — the first previous publication has been moved into rollback storage;
2. **after first promotion** — one new output is visible at its final path while another output is not yet promoted;
3. **after last promotion** — every new final file is visible, but the journal has not yet been changed to `committed`.

For every crash case, the parent test verifies:

- the child exited at the intended abrupt boundary;
- one pending transaction journal remains;
- the public recovery API acquires the output-directory lock after the crashed process releases it;
- the previous PDF/report bundle is restored;
- pending transaction evidence is cleaned after successful recovery;
- the output lock can be acquired again.

Recovery Acceptance run `32022863454` passed all three crash phases on Windows, macOS, and Ubuntu.

This is real controlled process-termination acceptance on GitHub-hosted local filesystems. It does not simulate physical power loss, storage-device removal, or multi-host network-filesystem lock semantics.

## Security workflow

`.github/workflows/security.yml` runs CodeQL. Dependency review is pull-request-oriented and is expected to skip on ordinary pushes.

## Package Desktop

`.github/workflows/package.yml` is the real PyInstaller packaging workflow.

It runs on:

- manual dispatch;
- `v*` tags;
- packaging/UI-related changes on `main`.

Matrix:

- Windows;
- macOS;
- Ubuntu;
- Python 3.12.

Each platform now:

1. installs build dependencies;
2. validates packaging configuration;
3. builds the native PyInstaller application;
4. launches the actual packaged executable with `--packaged-smoke`;
5. initializes the Qt desktop stack offscreen;
6. creates a temporary one-part PDF and DOCX;
7. runs a real mixed project merge through the packaged application libraries;
8. verifies validated PDF/DOCX outputs, merge manifest, and checksums;
9. archives the native package;
10. generates a SHA-256 sidecar for the archive;
11. uploads the archive plus sidecar as an explicitly unsigned artifact.

This exercises bundled `pypdf`, `python-docx`, `docxcompose`, ReportLab publication helpers, transaction locking/promotion, and evidence generation—not merely executable startup.

See [CI Packaging](build/ci-packaging.md).

## Stress Acceptance

`.github/workflows/stress.yml` is manually dispatchable with configurable synthetic fixture scale. It generates fixtures, validates them, runs preflight/merge, compares outputs, records sizes, and uploads the result bundle.

See [Stress Testing](stress-testing.md).

## Accessibility smoke

```bash
python scripts/check_accessibility.py
```

This checks representative accessible names/descriptions, label buddies, and keyboard metadata offscreen. Human assistive-technology acceptance remains separate.

## Recovery testing strategy

Recovery coverage now includes:

- successful multi-output promotion;
- second-format failure before promotion;
- report-generation failure;
- cancellation before promotion;
- failure during promotion with successful rollback;
- rollback failure preserving evidence;
- simulated journal states;
- fingerprint conflict fail-closed behavior;
- unsafe journal paths;
- concurrent transaction/recovery lock exclusion;
- injected `ENOSPC` cleanup;
- real abrupt process exit at multiple promotion phases on Windows/macOS/Linux.

Remaining environmental acceptance includes real filled-filesystem behavior, power/storage-disconnect scenarios where practical, and network/shared-filesystem locking semantics if those environments are claimed.

## Document-fidelity testing

PDF tests cover ordering, page evidence, encryption, publication helpers, validation, cancellation, and source immutability. DOCX tests cover package structure, paragraphs/headings, tables, media, sections, styles/numbering, headers/footers, relationships, fields/TOC behavior, and collision diagnostics where practical.

Portable tests cannot prove every Microsoft Word rendering behavior. Representative real-world fidelity acceptance remains separate.

## Test-data policy

Use synthetic fixtures whenever possible. Never commit private manuscripts, passwords, tokens, or confidential diagnostics. Reduce private-document regressions to the smallest synthetic structure that reproduces the defect.

## CI debugging workflow

When a gate fails:

1. read the exact failed step/log;
2. distinguish environment failure from application failure;
3. fix the root cause in a focused commit;
4. do not disable the gate merely to make CI green;
5. rerun because later steps may have been skipped;
6. record evidence only after the relevant checkpoint actually passes.

## Release CI acceptance matrix

Before a stable release candidate, obtain current/relevant evidence for:

- Quality green on supported Python matrix;
- 120-Part Regression green;
- Build Smoke green on Windows/macOS/Linux;
- Recovery Acceptance green when publication/recovery semantics changed;
- Security/CodeQL green;
- appropriate measured Stress acceptance;
- Package Desktop native build + packaged publication smoke + archive checksum on all target platforms;
- clean-machine interactive acceptance;
- representative real-world fidelity acceptance;
- human accessibility acceptance;
- signing/notarization verification where production distribution requires it.

Do not reuse old run IDs as proof for materially changed behavior.

## Documentation evidence

Record significant verified checkpoints in:

```text
CHANGELOG.md
what_changed.md
```

Keep implemented, automatically verified, and human/production accepted states distinct.
