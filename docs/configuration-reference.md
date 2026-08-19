# Configuration, Governance, and Asset Reference

This document explains the repository-level configuration files, GitHub governance metadata, package/tool configuration, and branding assets used by DocMergeForge. It is intended for maintainers who need to understand why a file exists before changing it.

For a literal every-file inventory, see [Complete Repository File Reference](repository-reference.md). Runtime settings stored by the application are documented separately in [Application Settings Reference](settings-reference.md).

## `pyproject.toml`

`pyproject.toml` is the canonical Python packaging and development-tool configuration.

### Build system

The project uses Hatchling as its PEP 517 build backend:

```toml
[build-system]
requires = ["hatchling>=1.25"]
build-backend = "hatchling.build"
```

The wheel target packages `src/docmergeforge`, following the `src/` layout.

### Package identity

The maintained package metadata declares:

- package name: `docmergeforge`;
- current pre-stable version: `0.1.0`;
- Python requirement: 3.12 or newer;
- license: MIT;
- author metadata: Sanskar / `sanskarin@outlook.in`;
- project URLs for repository, documentation, issues, and funding.

The development-status classifier remains pre-alpha. Do not change version/readiness classifiers merely because features or documentation are extensive; release readiness is governed by actual acceptance evidence.

### Runtime dependencies

The normal runtime dependency set covers:

- PDF processing with `pypdf`;
- DOCX processing with `python-docx` and `docxcompose`;
- desktop UI with `PySide6`;
- PDF generation/support with `reportlab`.

Version ranges intentionally constrain major versions. Dependency upgrades should be reviewed with tests and, for document libraries, representative fidelity evidence where behavior can change.

### Optional development dependencies

The `dev` extra includes pytest/coverage, Ruff, Black, mypy, pre-commit, and typing support. The `build` extra includes PyInstaller and the CycloneDX BOM tooling used by packaging/release automation.

Typical developer install:

```bash
python -m pip install -e ".[dev]"
```

Typical build-tool install:

```bash
python -m pip install -e ".[build]"
```

Install both extras when a developer needs quality checks and desktop packaging.

### Entry points

```toml
[project.scripts]
docmergeforge = "docmergeforge.cli.main:main"
docmergeforge-gui = "docmergeforge.ui.main:main"
```

The CLI and GUI are deliberately separate entry points over the same runtime package. Shared safety rules should live below these presentation layers rather than be duplicated separately in each entry point.

### Pytest configuration

Tests live under `tests/`. Strict marker handling is enabled, and the maintained markers distinguish integration and regression scenarios. A marker controls selection/organization; it does not weaken the underlying assertion requirements.

### Ruff

Ruff targets Python 3.12, uses a 100-character line length, and enables the maintained lint families for pycodestyle errors, Pyflakes, import sorting, bugbear, pyupgrade, simplifications, and comprehension improvements.

Do not silence a new lint rule globally solely to make CI green. Prefer fixing the code or applying the smallest justified per-line/per-file exception with an explanation when necessary.

### Black

Black uses the same 100-character line length and Python 3.12 target. The Quality workflow checks formatting; it does not auto-format committed code.

### mypy

Strict mypy mode is enabled for `docmergeforge` with `src` as the mypy path. New public/internal code should preserve useful type information rather than introducing broad `Any` escapes to satisfy the checker.

## `.editorconfig`

`.editorconfig` defines editor-neutral formatting defaults so contributors using different IDEs do not create accidental whitespace/encoding churn.

When editing it, keep settings compatible with the formatter/linter configuration in `pyproject.toml`. Editor preferences should not contradict Black or create platform-specific line-ending noise.

## `.gitattributes`

`.gitattributes` defines repository Git attributes such as line-ending/text treatment and binary handling. It helps keep cross-platform checkouts deterministic.

Changing attributes can rewrite many files on a later checkout/commit. Review such changes carefully and avoid mixing repository-wide normalization with unrelated feature work.

## `.gitignore`

`.gitignore` excludes local/generated state that must not be committed, including typical virtual environments, Python caches, test/build outputs, IDE artifacts, and application-generated temporary/build files.

Before adding a new ignore pattern, verify it cannot hide a source, fixture, evidence file, or configuration file that maintainers actually need to review.

## `.pre-commit-config.yaml`

This file defines local pre-commit hooks and their pinned revisions/settings. It complements, rather than replaces, CI.

Recommended setup:

```bash
pre-commit install
pre-commit run --all-files
```

The maintained local hooks include:

- Ruff linting with fixes;
- Ruff formatting;
- YAML and JSON syntax checks;
- end-of-file and trailing-whitespace normalization;
- oversized-added-file checks;
- `python scripts/check_docs_links.py` for repository-local Markdown link integrity; and
- `python scripts/check_repository_reference.py` for complete Git-tracked repository documentation coverage.

The repository-reference hook uses `always_run: true` because a tracked-file deletion, rename, configuration change, source change, or non-Markdown addition can make the inventory stale even when no Markdown file itself is part of the staged change. `pass_filenames: false` ensures the checker evaluates the complete tracked repository rather than only staged paths.

The Quality workflow validates the pre-commit configuration separately and also invokes both documentation integrity commands directly. A local hook pass is useful developer feedback but does not prove the remote CI matrix passed.

## GitHub ownership and community metadata

### `.github/CODEOWNERS`

Defines default ownership/review routing. Keep path patterns broad enough to cover intended files while avoiding accidental ownership gaps.

### `.github/FUNDING.yml`

Declares the project's GitHub funding metadata. Existing funding/support references are project metadata and should not be silently removed or replaced during unrelated maintenance.

### `.github/SUPPORT.md`

Provides the short GitHub-facing path from generic support requests to the canonical project support documentation.

### `CODE_OF_CONDUCT.md`

Defines community behavior expectations and enforcement principles. Code-of-conduct changes are governance changes and should not be bundled casually with implementation work.

### `CONTRIBUTING.md`

Defines contributor environment setup, coding/testing expectations, documentation requirements, commit/pull-request guidance, and safety/release-claim rules.

The contributor guide should remain aligned with the actual commands enforced by `.github/workflows/quality.yml`.

### `SECURITY.md`

Defines vulnerability reporting and supported security scope. It is the public reporting-policy entry point; `docs/security.md` explains the technical security model in more depth.

### `LICENSE`

Contains the MIT license. Do not modify license text without an intentional project licensing decision.

### `THIRD_PARTY_NOTICES.md`

Records important third-party dependency/license notices. Review it when adding dependencies or changing packaging/distribution material.

## Issue templates

### `.github/ISSUE_TEMPLATE/bug_report.yml`

Collects structured reproduction information for bugs. Fields should encourage reporters to include version, platform, input type, expected/actual behavior, and non-sensitive diagnostics without requesting private manuscript contents unnecessarily.

### `.github/ISSUE_TEMPLATE/feature_request.yml`

Collects the use case and requested behavior for new features. Feature requests should not imply a committed release date or production-readiness claim.

### `.github/ISSUE_TEMPLATE/config.yml`

Controls issue chooser behavior and external/support routes. Keep links synchronized with canonical repository support/security locations.

## Pull request template

### `.github/PULL_REQUEST_TEMPLATE.md`

The PR template is a review checklist. It should prompt contributors to cover:

- scope and behavior;
- tests and failure paths;
- documentation;
- privacy/security implications;
- packaging/release implications where applicable;
- evidence boundaries for external-office or human acceptance.

Repository-file additions/renames/deletions should also update `docs/repository-reference.md` so the documentation coverage guard remains green.

## Dependabot

### `.github/dependabot.yml`

Configures automated dependency update proposals. Dependabot reduces update discovery burden but does not make upgrades risk-free. Document-engine, Qt, PyInstaller, build, and security-tool upgrades should still pass the maintained test/acceptance layers.

## GitHub Actions configuration

All workflow files live under `.github/workflows/` and are documented individually in [Automation and Workflow Reference](automation-reference.md). Common configuration principles include:

- minimum required GitHub permissions;
- deterministic dependency installation where practical;
- cancellation/concurrency rules for replaceable runs;
- clear distinction between portable CI and controlled/manual acceptance environments;
- artifact/evidence retention sufficient for review;
- no conversion of a configured workflow into a production-readiness claim without actual passing evidence.

## Root development records

### `PROJECT_STATE.md`

A concise continuation checkpoint for repository work. It should describe what is implemented and what remains without becoming a duplicate changelog.

### `what_changed.md`

The active development-pass ledger. It records detailed additions/changes/hardening, verification status, and remaining release gates. Older detailed history is archived under `docs/history/` to keep the active file manageable.

### `CHANGELOG.md`

The durable chronological change history. Unlike `what_changed.md`, it is intended as a user/developer-facing summary organized over the life of the project rather than a live implementation scratchpad.

## Branding assets

Branding files live under `assets/branding/` and are referenced by documentation and/or desktop packaging/resource helpers.

### `assets/branding/logo.svg`

Primary scalable project logo. Keep it suitable for vector rendering and packaged resource use.

### `assets/branding/readme-banner.svg`

Wide banner intended for the repository README/header presentation.

### `assets/branding/social-preview.svg`

Artwork sized/composed for repository/social preview use. GitHub's repository settings may require a rendered raster upload separately; the SVG remains the source asset.

### `assets/branding/splash.svg`

Splash-screen artwork for desktop/package presentation.

### `assets/branding/bmc-support-card.svg`

Project support artwork associated with the existing Buy Me a Coffee support link.

## Configuration change checklist

When modifying repository configuration or metadata:

1. identify whether the change affects local development, CI, packaging, governance, or distribution;
2. keep tool settings consistent across local and CI usage;
3. avoid weakening lint/type/test/security rules simply to bypass a failure;
4. update the relevant canonical guide;
5. update `docs/repository-reference.md` for any added/renamed/deleted tracked path;
6. run documentation link and repository-reference checks;
7. run the affected quality/build/test workflow or record that current-run evidence is still pending;
8. never turn configuration presence into a claim that signing, native-office fidelity, accessibility, or release acceptance has occurred.
