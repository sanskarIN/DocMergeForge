# DocMergeForge Project State

This file is a compact continuation checkpoint for future development sessions. Detailed change history belongs in [`what_changed.md`](what_changed.md) and historical records under [`docs/history/`](docs/history/).

## Current checkpoint

- Repository: `sanskarIN/DocMergeForge`
- Branch: `main`
- Version declared in `pyproject.toml`: `0.1.0`
- Checkpoint immediately before this state-file commit: `b92ef03ba2194abab6560768433b8a24206ebc63`
- Development status: pre-stable; do not claim `v1.0.0` or production certification from source/documentation changes alone.

## Latest completed maintenance surface

The latest continuation completed a repository-wide documentation mapping pass and made tracked-file documentation coverage an enforced Quality rule.

Added documentation:

- `docs/repository-reference.md`
  - literal inventory of every tracked repository file;
  - covers root metadata, GitHub configuration/workflows, assets, all docs, scripts, runtime modules, helpers, integration tests, regression tests, and unit tests;
  - establishes the maintenance rule that path additions/renames/deletions update the inventory in the same change.
- `docs/source-code-reference.md`
  - module-by-module runtime responsibility map;
  - architectural dependency direction;
  - safety-critical module boundaries and change checklist.
- `docs/test-suite-reference.md`
  - complete test-file map;
  - unit/integration/regression/acceptance distinctions;
  - behavior ownership and test-placement guidance.
- `docs/automation-reference.md`
  - every repository script and GitHub Actions workflow;
  - purpose, execution environment, evidence boundary, and linked canonical subsystem documentation.
- `docs/configuration-reference.md`
  - `pyproject.toml`, formatter/linter/type/test settings, Git/GitHub metadata, community/governance files, Dependabot, development records, and branding assets.
- `docs/documentation-catalog.md`
  - every maintained documentation file mapped by audience/task;
  - task-oriented lookup for common user/developer/operator/release goals.

## Documentation coverage enforcement

New implementation:

- `scripts/check_repository_reference.py`
  - obtains the tracked path set using `git ls-files`;
  - requires each exact repository-relative tracked file path to appear backticked in `docs/repository-reference.md`;
  - reports all missing entries deterministically;
  - distinguishes coverage failure from inability to read/inspect the repository.
- `tests/unit/test_repository_reference.py`
  - exact-path matching;
  - deterministic missing-path ordering;
  - successful command behavior;
  - missing-entry reporting;
  - unreadable-reference handling.
- `.github/workflows/quality.yml`
  - now runs `python scripts/check_repository_reference.py` after the existing local Markdown-link checker.

The coverage guard is intentionally based on Git-tracked files. Generated/untracked virtual environments, caches, build artifacts, private corpora, transaction residue, and other local state are outside this documentation inventory contract.

## Contributor/navigation updates

- `docs/README.md` has a Repository Internals section linking all new canonical references.
- `CONTRIBUTING.md` requires the documentation link checker and repository-reference checker in the normal local validation set.
- `.github/PULL_REQUEST_TEMPLATE.md` requires repository-reference updates when tracked paths change.
- `docs/development.md` documents repository documentation integrity as part of the definition of done.
- `what_changed.md` records the full documentation pass, verification boundary, and remaining release work.

## Previous feature checkpoint: guarded project synchronization

The preceding continuation added guarded project-selection synchronization:

- `src/docmergeforge/project/discovery.py` for raw current-source discovery independent of persisted `selected_files` filtering while excluding a strictly nested output subtree;
- `src/docmergeforge/project/sync.py` for deterministic synchronization planning, numbered/in-range eligibility, current/proposed/added/removed/reordered evidence, versioned backups, guarded persistence, symlink refusal, stale-plan protection, and no-op behavior;
- `docmergeforge project-sync`, preview-only by default, with `--apply` and a separate `--allow-removals` approval;
- `src/docmergeforge/project/drift.py` plus `scripts/check_project_sync.py` and cross-platform project-sync CI coverage.

A project can intentionally select unnumbered front/back matter or other material outside the automatic numbered/in-range rule. Such paths can appear in a proposal's `removed` list, so `--apply` alone does not authorize removal. The synchronization command changes project metadata only; it never deletes manuscript source files.

### Reconciled completed follow-up

The earlier checkpoint incorrectly left one already-completed synchronization follow-up in the recommended-work list. Current source confirms that `MergeApplicationService.discover()` already calls `discover_project_sources()` before applying persisted selection filtering, so normal project discovery and synchronization share the same strictly-nested-output exclusion policy. `tests/unit/test_service_discovery_safety.py` directly protects that service-level behavior. This item is complete and must not be reimplemented in a future continuation unless behavior actually changes.

## Verification boundary

Do not infer a green build merely from commits being present.

For the checkpoint inspected immediately before this state-file correction:

- the current source contains the shared project-discovery routing and its service-level regression test;
- the repository documentation pass and coverage-enforcement files remain present on `main`;
- GitHub combined commit status for `b92ef03ba2194abab6560768433b8a24206ebc63` exposed no passing status set;
- the available commit-workflow helper does not establish push-triggered `main` workflow results.

Therefore no fresh current-head pass is claimed here for:

- Ruff;
- Black check;
- strict mypy;
- Markdown link validation;
- repository-reference coverage execution;
- pytest/coverage;
- Quality workflow matrix;
- 120-Part Regression;
- Build Smoke;
- Security/CodeQL.

The committed checker/test/CI source is implementation evidence only until an actual run is observed.

External-office, stress, accessibility, clean-machine packaging, signing/notarization, and other release gates remain independent from documentation completeness.

## Recommended next development work

1. Observe a current-head Quality run and fix any lint/format/test/link/reference failure without weakening repository rules.
2. Keep `docs/repository-reference.md`, `docs/documentation-catalog.md`, and the relevant subsystem reference synchronized with every future path/responsibility change.
3. Consider a project-file revision/concurrency guard if multi-writer project editing is intended; project persistence is currently documented as last-writer-wins outside the narrower stale-state protection already present in project synchronization.
4. Evaluate whether the desktop project/order UI should expose the same preview/apply/second-removal-approval synchronization model.
5. Continue independent release-gate work for native-office fidelity, measured multi-gigabyte stress, human accessibility, clean-machine packaged applications, signing, and notarization.

## Continuation rule

Future sessions should read this file plus `what_changed.md`, inspect the current `main` head, and use the repository/source/test/automation/configuration/documentation references before changing a subsystem. Continue from repository evidence instead of re-implementing already committed features, and do not turn configured checks into claimed passing evidence without an observed run.
