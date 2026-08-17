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

Focused examples include part detection/natural sorting, output naming, settings/project serialization, storage/writeability, transaction journal recovery, cross-process locking, PDF/DOCX helpers, and packaging arguments.

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

`.github/workflows/quality.yml` runs on pushes to `main` and pull requests using Python 3.12 and 3.13 on Ubuntu. It installs the Linux Qt runtime, installs developer dependencies, and runs Ruff, Black, strict mypy, and full pytest with coverage.

## 120-Part Regression

`.github/workflows/regression.yml` runs on `main`, pull requests, and manual dispatch. It generates the deterministic 120-part SQL fixture, runs regression/integration tests, and validates Parts 1–120 through the CLI.

This is strong numbered-part regression evidence, but a normal generated fixture is not automatically multi-gigabyte acceptance.

## Build Smoke

`.github/workflows/build-smoke.yml` runs on Ubuntu, Windows, and macOS with Python 3.12. It checks source compilation, CLI availability, desktop accessibility metadata, and packaging preflight. It does not invoke the complete PyInstaller package build.

## Recovery Acceptance

`.github/workflows/recovery-acceptance.yml` is a dedicated cross-platform filesystem/recovery gate. It runs on Windows, macOS, and Ubuntu when transaction/recovery/lock acceptance files change, plus manual dispatch.

The acceptance test starts a real child Python process that owns an `OutputTransaction`, writes a durable `promoting` journal, mutates real final paths, and then terminates abruptly with `os._exit()` so ordinary Python cleanup cannot run.

Current crash phases are:

1. **after first backup** — the first previous publication has been moved into rollback storage;
2. **after first promotion** — one new output is visible at its final path while another output is not yet promoted;
3. **after last promotion** — every new final file is visible, but the journal has not yet been changed to `committed`.

For every case the parent verifies the pending journal, safe recovery, restoration of the previous PDF/report bundle, staging cleanup, and lock reacquisition.

Recovery Acceptance run `32022863454` passed all three crash phases on Windows, macOS, and Ubuntu.

This is real controlled process-termination acceptance on GitHub-hosted local filesystems. It does not simulate physical power loss, storage-device removal, or multi-host network-filesystem lock semantics.

## Disk Full Acceptance

`.github/workflows/disk-full-acceptance.yml` provides real filesystem-exhaustion evidence on Ubuntu.

The workflow mounts an isolated **32 MiB tmpfs** under the GitHub runner temporary directory, then runs:

```bash
python scripts/check_disk_full_recovery.py --output-dir <mounted-tmpfs>
```

The helper has a safety guard and refuses to intentionally fill a filesystem with more than 128 MiB free. Inside the intentionally small filesystem it:

1. creates a previously published target;
2. enters the real `atomic_output()` path;
3. writes/fsyncs 1 MiB chunks until the kernel returns `ENOSPC`;
4. confirms the exception was a real `errno.ENOSPC`;
5. confirms the previous published target is byte-for-byte unchanged;
6. confirms no atomic `.part` residue remains.

Disk Full Acceptance run `32023429920` passed on Ubuntu with a real tmpfs `ENOSPC`.

This upgrades the earlier injected-`ENOSPC` unit evidence. It does not by itself prove identical behavior on every Windows/macOS filesystem or removable/network storage target.

## Security workflow

`.github/workflows/security.yml` runs CodeQL. Dependency review is pull-request-oriented and is expected to skip on ordinary pushes.

## Package Desktop

`.github/workflows/package.yml` is the real PyInstaller packaging workflow. It runs on manual dispatch, `v*` tags, and packaging/UI-related changes on `main`.

Matrix: Windows, macOS, Ubuntu, Python 3.12.

Each platform:

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

## Recovery and storage testing strategy

Coverage now includes successful multi-output promotion; second-format/report failures; cancellation; rollback and rollback-failure preservation; simulated journal states; fingerprint/path fail-closed behavior; cross-process lock exclusion; injected `ENOSPC`; real abrupt process exit at multiple promotion phases on Windows/macOS/Linux; and a real Linux tmpfs `ENOSPC`.

Remaining environmental acceptance includes physical power/storage-disconnect scenarios where practical, additional filesystem/platform exhaustion if claimed, and network/shared-filesystem locking semantics if those environments are claimed.

## Document-fidelity testing

PDF tests cover ordering, page evidence, encryption, publication helpers, validation, cancellation, and source immutability. DOCX tests cover package structure, paragraphs/headings, tables, media, sections, styles/numbering, headers/footers, relationships, fields/TOC behavior, and collision diagnostics where practical.

Portable tests cannot prove every Microsoft Word rendering behavior. Representative real-world fidelity acceptance remains separate.

## Test-data policy

Use synthetic fixtures whenever possible. Never commit private manuscripts, passwords, tokens, or confidential diagnostics. Reduce private-document regressions to the smallest synthetic structure that reproduces the defect.

## CI debugging workflow

When a gate fails: read the exact step/log, distinguish environment from application failure, fix the root cause in a focused commit, do not disable the gate merely to make CI green, rerun because later steps may have been skipped, and record evidence only after the relevant checkpoint actually passes.

## Release CI acceptance matrix

Before a stable release candidate, obtain relevant evidence for:

- Quality green on supported Python matrix;
- 120-Part Regression green;
- Build Smoke green on Windows/macOS/Linux;
- Recovery Acceptance green when publication/recovery semantics changed;
- Disk Full Acceptance and any additional filesystem/platform exhaustion relevant to the support claim;
- Security/CodeQL green;
- appropriate measured Stress acceptance;
- Package Desktop native build + packaged publication smoke + archive checksum on all target platforms;
- clean-machine interactive acceptance;
- representative real-world fidelity acceptance;
- human accessibility acceptance;
- signing/notarization verification where production distribution requires it.

Do not reuse old run IDs as proof for materially changed behavior.

## Documentation evidence

Record significant verified checkpoints in `CHANGELOG.md` and `what_changed.md`, keeping implemented, automatically verified, and human/production accepted states distinct.
