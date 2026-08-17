# Development Guide

This guide is for contributors working on DocMergeForge source code, tests, documentation, packaging, or release automation.

## Development principles

Changes should preserve the project's core invariants:

1. PDF and DOCX pipelines remain separate.
2. Companion/source code is never merged into manuscripts.
3. Original source files are not rewritten by normal merge workflows.
4. Numbered-part validation blocks incomplete/duplicate sets.
5. Source-integrity changes during a run block publication.
6. Output generation uses staging/validation before final promotion.
7. Full project publication is a transaction across manuscripts and evidence.
8. Recovery fails closed rather than guessing when filesystem state conflicts.
9. Passwords and manuscript body text are not written into diagnostics/project files.
10. Unsupported high-fidelity modes must not silently pretend to be production-ready.

## Environment setup

```bash
git clone https://github.com/sanskarIN/DocMergeForge.git
cd DocMergeForge
python -m venv .venv
```

Activate the environment, then:

```bash
python -m pip install --upgrade pip
pip install -e ".[dev]"
pre-commit install
```

For packaging work:

```bash
pip install -e ".[build]"
```

## Repository layout

```text
.github/
  ISSUE_TEMPLATE/        GitHub issue forms
  workflows/             CI, security, packaging, stress automation
assets/branding/         project SVG branding

docs/                    user/operator/developer documentation
fixtures/                regression fixture area where applicable
scripts/                 build, fixture, stress, accessibility utilities
src/docmergeforge/       installable application package
tests/                   unit/integration/regression tests
```

Major application packages include:

```text
app/          orchestration, preflight, service layer
audit/        publication text audit
cli/          command-line entry point
companion/    companion-code handling
core/         models, exceptions, shared primitives
diagnostics/  logging/diagnostics
discovery/    scanning/classification/part detection
docx/         DOCX composition/validation/fidelity
ordering/     ordering-related logic
packaging/    desktop build configuration
pdf/          PDF merge/publication/password handling
presets/      guided project presets
profiles/     merge profiles
project/      project persistence/selection/recovery
reports/      reports, manifest, checksums, checklists
settings/     application settings
ui/           PySide6 desktop application
utilities/    hashing, storage, atomic/transaction helpers
validation/   part/output comparison and validation services
```

## Entry points

Declared console scripts:

```text
docmergeforge     -> docmergeforge.cli.main:main
docmergeforge-gui -> docmergeforge.ui.main:main
```

## Standard quality checks

Run before committing/pushing code:

```bash
ruff check .
black --check .
mypy src/docmergeforge
pytest
```

To apply Black formatting:

```bash
black .
```

Do not weaken Ruff/Black/mypy settings to make a new change pass unless the project intentionally changes its quality policy and documents why.

## Type checking

`mypy` runs in strict mode for `docmergeforge`.

New code should:

- annotate public/internal functions meaningfully;
- avoid untyped escape hatches where possible;
- narrow `object`/JSON values explicitly;
- use typed callables for callbacks/password providers;
- avoid suppressions unless the reason is real and documented.

## Formatting and linting

Repository policy:

- Python target: 3.12;
- line length: 100;
- Ruff rule groups: `E`, `F`, `I`, `B`, `UP`, `SIM`, `C4`;
- Black target: Python 3.12.

If CI reports an exact Black diff, apply formatter output rather than hand-tuning an alternative style.

## Tests

Pytest test roots:

```text
tests/
```

Markers:

- `integration` — tests requiring document libraries/workflows;
- `regression` — larger synthetic regression tests.

Examples:

```bash
pytest
pytest tests/unit
pytest -m integration
pytest -m regression
pytest -m "regression or integration" tests/regression tests/integration
```

See [Testing and CI](testing-and-ci.md).

## Synthetic fixtures

Do not commit confidential manuscripts as tests.

Use generated/synthetic fixtures for:

- numbered-part detection;
- PDF/DOCX merge correctness;
- 120-part workflows;
- companion archives;
- cancellation/recovery;
- storage failures;
- malformed/edge-case packages where licensing/privacy permits.

The 120-part fixture generator is:

```bash
python scripts/generate_120_fixture.py fixtures/generated/sql-120
```

## UI development

When adding/changing a desktop control:

- set accessible names;
- add descriptions for non-obvious/safety-sensitive behavior;
- create label buddies where applicable;
- ensure keyboard reachability;
- add shortcuts for important repeated actions;
- extend `scripts/check_accessibility.py` for release-critical controls;
- run the smoke script locally when Qt runtime is available.

```bash
python scripts/check_accessibility.py
```

See [Accessibility](accessibility.md).

## Document-engine changes

### PDF

New PDF features must preserve:

- input order;
- encrypted-PDF safety/password handling;
- output reopen validation;
- expected page evidence;
- cancellation responsiveness;
- source immutability.

### DOCX

DOCX changes must preserve/validate OOXML package integrity and should include conflict/fidelity tests for styles, numbering, sections, relationships, media, headers/footers, and generated publication elements where relevant.

Do not represent an external office-suite adapter as production-ready until real integration and acceptance tests exist.

## Transaction changes

`OutputTransaction` is release-critical code.

Any change to promotion/recovery should consider crash points before and after every filesystem mutation:

- journal write;
- existing-final backup;
- staged-final replacement;
- commit marker;
- backup cleanup;
- staging cleanup.

Add tests for normal success, graceful failure, cancellation, rollback failure, abrupt-interruption simulation, fingerprint mismatch, unsafe paths, and stale committed/rolled-back cleanup as relevant.

## Storage changes

Preflight storage logic must continue to:

- create missing output folders safely;
- verify destination writeability;
- clean write-probe files;
- report a safe estimate;
- raise a dedicated error on access/storage failure.

Never “fix” a storage failure by silently disabling the preflight.

## Diagnostics

Do not log:

- encrypted-PDF passwords;
- full manuscript body text;
- authentication tokens;
- unnecessary sensitive filesystem contents.

Use redaction helpers and privacy-safe summaries.

## Documentation changes

Behavioral code changes should update the relevant file under `docs/` and, when development status materially changes, update:

```text
CHANGELOG.md
what_changed.md
```

Do not mark a release gate complete in documentation until verified evidence exists.

## Building desktop packages

Preflight:

```bash
python scripts/build_desktop.py --check
```

Onedir development package:

```bash
python scripts/build_desktop.py
```

One-file development executable:

```bash
python scripts/build_desktop.py --one-file
```

See [Building Executables](building-executables.md).

## Git/commit style

Prefer focused commits whose message describes one coherent change, for example:

```text
fix: preserve recovery evidence after rollback failure
test: cover cancellation before publication promotion
docs: document journaled output recovery
ci: run accessibility smoke on desktop matrix
```

Avoid combining unrelated refactors, behavior changes, formatter churn, and documentation into one giant commit when they can be reviewed independently.

## Pull request expectations

A good PR should explain:

- problem/goal;
- behavioral changes;
- safety implications;
- test coverage;
- documentation changes;
- release-gate impact;
- any remaining limitations.

Use the repository pull-request template and never attach confidential user manuscripts to public PRs.

## Definition of done

A code change is not complete merely because it compiles. Depending on scope, completion can require:

- Ruff green;
- Black green;
- strict mypy green;
- pytest green;
- 120-part regression green;
- cross-platform Build Smoke green;
- CodeQL/security checks green;
- updated docs/changelog;
- platform packaging acceptance;
- human accessibility/fidelity/stress acceptance.

Choose the acceptance level appropriate to the change and do not overclaim unrun gates.
