# Testing and CI

DocMergeForge uses layered automated checks because document merging, desktop UI behavior, filesystem transactions, packaging, and security each fail in different ways. A green unit-test suite alone is not sufficient evidence for a release.

## Local quality commands

From a developer environment:

```bash
ruff check .
black --check --diff .
mypy src/docmergeforge
pytest --cov=docmergeforge --cov-report=term-missing
```

The CI Quality workflow uses the same major gates.

## Test categories

### Unit tests

Unit tests should isolate focused behavior such as:

- part detection/natural sorting;
- output naming;
- settings/project serialization;
- storage estimates/writeability handling;
- transaction journal validation/recovery;
- PDF/DOCX helper behavior;
- packaging argument generation.

### Integration tests

Marked with:

```text
integration
```

These exercise multiple components/document libraries together. Examples include real PDF/DOCX fixture generation, merge flows, UI metadata, CLI behavior, and packaging-script preflight.

Run:

```bash
pytest -m integration
```

### Regression tests

Marked with:

```text
regression
```

These protect larger previously working scenarios, including generated multi-part publications.

Run:

```bash
pytest -m regression
```

Combined release-relevant subset:

```bash
pytest -m "regression or integration" tests/regression tests/integration
```

## Quality workflow

`.github/workflows/quality.yml` runs on pushes to `main` and pull requests.

Matrix:

- Python 3.12;
- Python 3.13;
- Ubuntu runner.

Current steps include:

1. checkout;
2. Python setup/pip cache;
3. Linux Qt runtime installation (`libegl1`);
4. pip upgrade;
5. `pip install -e ".[dev]"`;
6. `ruff check .`;
7. `black --check --diff .`;
8. `mypy src/docmergeforge`;
9. pytest with coverage.

The Linux Qt runtime is required because accessibility/UI integration tests import PySide6 even when Qt is used offscreen.

## 120-Part Regression workflow

`.github/workflows/regression.yml` runs on:

- pushes to `main`;
- pull requests;
- manual dispatch.

It uses Python 3.12 on Ubuntu and currently:

1. installs the Linux Qt runtime;
2. installs developer dependencies;
3. generates the 120-part SQL fixture;
4. runs regression/integration tests;
5. runs CLI validation against Parts 1–120.

Core commands include:

```bash
python scripts/generate_120_fixture.py fixtures/generated/sql-120
pytest -m "regression or integration" tests/regression tests/integration
docmergeforge validate --input fixtures/generated/sql-120 --parts 1-120
```

This workflow provides continuously exercised evidence for the numbered 120-part path, but a small generated fixture is not equivalent to a multi-gigabyte real manuscript.

## Build Smoke workflow

`.github/workflows/build-smoke.yml` runs on:

- pushes to `main`;
- pull requests;
- manual dispatch.

Matrix:

- Ubuntu;
- Windows;
- macOS.

It uses Python 3.12 and checks:

- source compilation;
- CLI entry-point availability;
- desktop accessibility metadata;
- desktop packaging configuration.

Representative commands:

```bash
python -m compileall -q src
docmergeforge --help
python scripts/check_accessibility.py
python scripts/build_desktop.py --check
```

On Ubuntu the workflow installs `libegl1` before importing Qt.

Build Smoke does **not** build/sign/notarize final production installers. It verifies that the configured source/entry points/packaging metadata can be exercised on each runner.

## Security workflow

`.github/workflows/security.yml` includes GitHub CodeQL analysis.

Dependency review is applicable to pull-request dependency diffs and can be skipped on ordinary push events.

Security CI is one layer of evidence. It does not replace dependency updates, threat modeling, manual review, or secure release signing.

## Package Desktop workflow

`.github/workflows/package.yml` is separate from Build Smoke.

Triggers:

- manual dispatch;
- tags matching `v*`.

Matrix:

- Windows;
- macOS;
- Ubuntu;
- Python 3.12.

It installs `.[build]`, validates packaging configuration, builds with PyInstaller, archives the artifact, and uploads an explicitly unsigned development artifact.

Use this workflow to test package creation, not to claim production signing acceptance.

## Stress Acceptance workflow

`.github/workflows/stress.yml` is manually dispatchable so large synthetic runs do not make every PR excessively expensive.

It supports configurable synthetic fixture scale and performs steps such as:

- fixture generation;
- validation;
- project/preflight execution;
- merge;
- source/output comparison;
- artifact-size evidence;
- artifact upload.

See [Stress Testing](stress-testing.md).

## Accessibility smoke

Run locally:

```bash
python scripts/check_accessibility.py
```

This builds representative dialogs offscreen and checks accessible names/descriptions, label buddies, and keyboard metadata.

It is intentionally deterministic and automation-friendly, but does not replace real screen-reader testing.

## Packaging preflight integration

Run:

```bash
python scripts/build_desktop.py --check
```

The check validates that the selected repository root contains required inputs such as:

```text
pyproject.toml
src/docmergeforge/ui/main.py
```

Unit/integration tests should keep this preflight aligned with the actual packaging entry point.

## Recovery testing strategy

Publication recovery should be tested at multiple levels:

- successful multi-output promotion;
- second-format failure before promotion;
- report-generation failure;
- cancellation before promotion;
- failure during promotion with successful rollback;
- rollback failure preserving evidence;
- simulated process interruption with `promoting` journal;
- stale `committed`/`rolled-back` cleanup;
- fingerprint mismatch fail-closed behavior;
- unsafe journal paths;
- disk-exhaustion cleanup behavior.

Do not test only the happy path; most transaction defects live between filesystem mutations.

## Document-fidelity testing

### PDF

Tests should verify:

- correct source order;
- page counts;
- encrypted-PDF behavior;
- bookmarks/front matter as applicable;
- validation/reopen;
- cancellation;
- source immutability.

### DOCX

Tests should cover representative:

- paragraphs/headings;
- tables;
- inline images/media;
- sections;
- styles;
- numbering;
- headers/footers;
- relationships;
- TOC/field behavior;
- complex-package conflict warnings.

Portable library tests cannot prove all Word-rendering fidelity. Maintain real-world acceptance documents separately where licensing/privacy permits.

## Test-data policy

Prefer synthetic fixtures. Never add private user manuscripts, passwords, tokens, or confidential diagnostics to the repository.

For a regression discovered in a private document, reduce it to the smallest synthetic structure that reproduces the bug.

## CI debugging workflow

When a gate fails:

1. read the exact failed step/log;
2. distinguish environment failure from application failure;
3. reproduce locally when possible;
4. fix the root cause in a focused commit;
5. do not disable the gate just to make CI green;
6. rerun the full workflow because later stages may have been skipped;
7. update `what_changed.md` only after the relevant final-head evidence is known.

Example: a Qt `libEGL.so.1` import failure on Ubuntu is an environment prerequisite issue; installing the required runtime library is preferable to deleting accessibility tests.

## Release CI acceptance matrix

Before a stable release candidate, obtain current-head evidence for:

- Quality green on supported Python matrix;
- 120-Part Regression green;
- Build Smoke green on Windows/macOS/Linux;
- Security/CodeQL green;
- relevant manual Stress runs green;
- Package Desktop artifacts built;
- human launch/fidelity/accessibility acceptance;
- signing/notarization verification where production distribution requires it.

Do not reuse old run IDs as proof for a materially changed release head.

## Documentation evidence

Record significant verified checkpoints in:

```text
CHANGELOG.md
what_changed.md
```

Separate three states clearly:

- implemented;
- automatically verified;
- manually/platform accepted.

This prevents green source CI from being misrepresented as complete production release acceptance.
