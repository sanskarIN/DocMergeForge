# Contributing to DocMergeForge

Thank you for improving DocMergeForge. Contributions are welcome across application code, tests, documentation, accessibility, document fidelity, packaging, recovery, and release automation.

Start with the full [Development Guide](docs/development.md) and [Testing and CI Guide](docs/testing-and-ci.md).

## Core contribution rules

Every change must preserve the project's safety model:

1. PDF and DOCX manuscript pipelines remain separate.
2. Companion/source-code packages are never merged into manuscripts.
3. Original source files are read-only inputs to normal merge workflows.
4. Missing/duplicate numbered parts are not silently ignored.
5. Source-integrity changes during a run must block publication.
6. New final publication files must use validated staging/transaction behavior.
7. Recovery must fail closed when filesystem state cannot be proven safe.
8. Passwords, tokens, and manuscript body text must not be intentionally logged or persisted.
9. Unsupported fidelity modes must not silently downgrade or claim production readiness.
10. Documentation must describe verified behavior rather than aspirations.

## Development environment

Use Python 3.12+.

```bash
python -m venv .venv
```

Activate it, then:

```bash
python -m pip install --upgrade pip
pip install -e ".[dev]"
pre-commit install
```

For packaging work:

```bash
pip install -e ".[build]"
```

See [Installation](docs/installation.md) for platform-specific setup.

## Required local checks

Before opening a pull request:

```bash
ruff check .
black --check --diff .
mypy src/docmergeforge
pytest
```

For changes affecting larger workflows:

```bash
python scripts/generate_120_fixture.py fixtures/generated/sql-120
pytest -m "regression or integration" tests/regression tests/integration
docmergeforge validate --input fixtures/generated/sql-120 --parts 1-120
```

For desktop changes:

```bash
python scripts/check_accessibility.py
```

For packaging changes:

```bash
python scripts/build_desktop.py --check
```

Do not weaken quality gates merely to make a new change pass. Fix the underlying issue or propose a documented policy change.

## Tests

Add focused tests for changed behavior. Important areas include:

- discovery/part detection/order;
- validation and preflight;
- PDF/DOCX engine behavior;
- encrypted PDFs;
- source-integrity protection;
- cancellation;
- output transaction rollback/recovery;
- storage/writeability failures;
- reports/checksums/manifests;
- project persistence;
- CLI behavior;
- desktop accessibility metadata;
- packaging configuration.

Never commit confidential user manuscripts or real credentials as fixtures. Reduce private regressions to synthetic documents.

## Documentation

Meaningful behavior changes should update the relevant page under [`docs/`](docs/README.md).

The documentation portal includes user, operator, contributor, architecture, CLI, engine, recovery, packaging, security, accessibility, and release guides.

Also update as appropriate:

```text
CHANGELOG.md
what_changed.md
README.md
```

Do not mark a release gate complete until corresponding CI/manual/platform evidence exists.

## UI/accessibility contributions

For new interactive controls:

- provide a meaningful accessible name;
- add an accessible description for non-obvious/safety-sensitive behavior;
- connect labels to fields where appropriate;
- ensure keyboard reachability;
- add shortcuts for important repeated actions when appropriate;
- extend `scripts/check_accessibility.py` for release-critical controls;
- consider high contrast, text scaling, reduced motion, and long paths/lists.

See [Accessibility](docs/accessibility.md).

## PDF/DOCX fidelity contributions

Document-engine changes need both structural tests and realistic fidelity review.

Portable DOCX mode is the current production path. A LibreOffice or Microsoft Word adapter must not be marked production-ready until real automation, cleanup/error handling, tests, and platform acceptance exist.

See [PDF Engine](docs/pdf-engine.md), [DOCX Engine](docs/docx-engine.md), and [Known Limitations](docs/known-limitations.md).

## Transaction/recovery contributions

Publication transaction code is release-critical. Model failure/crash points around every final-path mutation and preserve rollback evidence when recovery cannot be proven complete.

See [Publication Recovery](docs/recovery.md) and [Merge Pipeline](docs/merge-pipeline.md).

## Commit style

Prefer focused commits with clear conventional messages, for example:

```text
fix: preserve transaction journal after rollback failure
test: cover PDF cancellation during finalization
docs: document output recovery procedure
ci: run accessibility smoke on Linux
```

Avoid a single giant commit for unrelated code, formatting, tests, and documentation when the work can be reviewed independently.

## Repository-local commit identity

If you are working as the repository owner and need the project-specific identity, configure it locally rather than changing another contributor's global Git settings:

```bash
git config user.name "Sanskar"
git config user.email "sanskarin@outlook.in"
```

Other contributors should use their own identity.

## Pull requests

A good pull request explains:

- the problem/goal;
- what behavior changed;
- safety/privacy/fidelity implications;
- tests added/run;
- documentation updated;
- release-gate impact;
- known remaining limitations.

Use the repository pull-request template.

## Security

Never post private manuscripts, passwords, tokens, signing credentials, or sensitive diagnostics in public issues/PRs.

See [`SECURITY.md`](SECURITY.md) and the [Security Model](docs/security.md).

## Code of conduct

Participation is governed by [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).

## License

Contributions are made to the project under the repository's [MIT License](LICENSE).
