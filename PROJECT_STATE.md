# DocMergeForge Project State

This file is a compact continuation checkpoint for future development sessions. Detailed change history belongs in [`what_changed.md`](what_changed.md) and historical records under [`docs/history/`](docs/history/).

## Current checkpoint

- Repository: `sanskarIN/DocMergeForge`
- Branch: `main`
- Version declared in `pyproject.toml`: `0.1.0`
- Checkpoint immediately before this state-file commit: `54db4f228dd735d31b4125109eaa7e874317ce35`
- Development status: pre-stable; do not claim `v1.0.0` or production certification from source/documentation changes alone.

## Latest completed feature: guarded existing-project persistence

The latest continuation closed the main known stale-write gap around reusable project JSON files while preserving the existing atomic-save model.

Implementation:

- `src/docmergeforge/project/store.py`
  - `project_file_revision(path)` returns a SHA-256 revision of the exact persisted bytes;
  - `load_project_snapshot(path)` parses a project and derives its revision from the same exact byte snapshot;
  - `save_project_if_revision(...)` refuses to replace an existing project whose bytes no longer match the expected revision;
  - generic `save_project(...)` refuses project destinations addressed through symbolic links;
  - normal project replacement still uses the maintained atomic text-save path.
- `src/docmergeforge/project/sync.py`
  - `apply_project_sync(...)` accepts an optional exact revision;
  - exact revision is checked before backup/write preparation;
  - the existing semantic on-disk project comparison remains as an additional defense;
  - the expected revision is checked again before final atomic replacement;
  - caller selection is restored if final persistence fails.
- `src/docmergeforge/cli/main.py`
  - `project-sync` loads project + revision together and carries the revision into apply;
  - `project-create` converts handled persistence failures into structured JSON with exit code `2` instead of leaking a save exception.
- `src/docmergeforge/ui/main.py`
  - **Resume Project** loads project + revision together and refuses to overwrite a project changed while the user reviews/reorders inputs;
  - resumed ordering deliberately does **not** write a recovery checkpoint before the guarded save;
  - after the guarded save succeeds, the desktop writes the `ordering` recovery checkpoint, then updates recent-project history and starts merge;
  - new-project save failures are surfaced to the desktop user;
  - ordering and SQL-preset recovery checkpoint failures are surfaced and stop the affected workflow.

Regression coverage added/expanded:

- `tests/unit/test_project_store_persistence_guard.py`
  - exact snapshot revision identity;
  - successful guarded save;
  - stale-content rejection with no overwrite;
  - symbolic-link project-save refusal.
- `tests/unit/test_cli_project_sync.py`
  - exact byte-level project drift rejection between snapshot and apply.
- `tests/unit/test_cli_workflow.py`
  - structured `project-create` save failure with exit code `2`.
- `tests/integration/test_order_dialog_accessibility.py`
  - desktop resume sequence explicitly asserts order confirmation → guarded save → recovery checkpoint → recent-project update → merge start;
  - this prevents a rejected stale project from leaving a newly written stale recovery snapshot.

Canonical documentation updated:

- `docs/project-sync.md`;
- `docs/project-files.md`;
- `docs/source-code-reference.md`;
- `docs/test-suite-reference.md`;
- `what_changed.md`.

### Important concurrency boundary

The SHA-256 project revision mechanism is an **optimistic stale-write guard**, not a universal cross-process lock. It detects project changes observed between snapshot and revision checks, including byte-only JSON drift. An arbitrary external writer can still race the tiny interval after a final revision check and before atomic replacement because that external writer is not participating in a coordinated lock protocol.

If true simultaneous multi-writer project editing becomes an intended supported feature, design a separate coordinated locking/revision protocol with ownership, timeout/recovery, filesystem semantics, and tests. Do not reimplement or relabel the completed optimistic guard as universal locking.

## Previous completed maintenance: repository-wide documentation mapping

The preceding maintenance continuation completed a repository-wide documentation mapping pass and made tracked-file documentation coverage an enforced Quality rule.

Key files:

- `docs/repository-reference.md` — literal inventory of every tracked repository path;
- `docs/source-code-reference.md` — module-by-module runtime responsibility map;
- `docs/test-suite-reference.md` — complete maintained test-file map;
- `docs/automation-reference.md` — scripts and GitHub Actions workflow reference;
- `docs/configuration-reference.md` — project/tooling/governance configuration reference;
- `docs/documentation-catalog.md` — documentation map by audience/task;
- `scripts/check_repository_reference.py` — exact tracked-path documentation checker;
- `tests/unit/test_repository_reference.py` — checker regression coverage;
- `.github/workflows/quality.yml` — runs the repository-reference checker after Markdown-link validation.

The coverage guard is based on Git-tracked files. Generated/untracked virtual environments, caches, build artifacts, private corpora, transaction residue, and other local state are outside this documentation inventory contract.

## Previous completed feature: guarded project synchronization

Project-selection synchronization remains implemented with:

- `src/docmergeforge/project/discovery.py` for raw current-source discovery independent of persisted `selected_files` filtering while excluding a strictly nested output subtree;
- `src/docmergeforge/project/sync.py` for deterministic synchronization planning, numbered/in-range eligibility, current/proposed/added/removed/reordered evidence, versioned backups, guarded persistence, symlink refusal, stale-plan protection, and no-op behavior;
- `docmergeforge project-sync`, preview-only by default, with `--apply` and a separate `--allow-removals` approval;
- `src/docmergeforge/project/drift.py` plus `scripts/check_project_sync.py` and cross-platform project-sync CI coverage.

A project can intentionally select unnumbered front/back matter or other material outside the automatic numbered/in-range rule. Such paths can appear in a proposal's `removed` list, so `--apply` alone does not authorize removal. Synchronization changes project metadata only; it never deletes manuscript source files.

### Reconciled completed discovery follow-up

Do not re-open the old task to route normal project discovery through the shared project-aware helper unless behavior actually changes. `MergeApplicationService.discover()` already calls `discover_project_sources()` before applying persisted selection filtering, and `tests/unit/test_service_discovery_safety.py` protects the shared strictly-nested-output exclusion behavior.

## Verification boundary

Do not infer a green build merely from commits being present.

For this continuation:

- source, regression tests, integration coverage, and canonical documentation for the new project revision behavior are committed on `main`;
- focused commit diffs were inspected for unintended broad rewrites;
- the resumed-project integration regression was refined to avoid lambda assignment patterns that could conflict with enabled Ruff `E` rules;
- `pyproject.toml` remains pre-stable at version `0.1.0` and retains Ruff, Black, strict mypy, and pytest configuration;
- committed tests are implementation evidence, not execution evidence.

Until an actual current-head run is observed, no fresh pass is claimed for:

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

External-office, stress, accessibility, clean-machine packaging, signing/notarization, and other release gates remain independent from source completeness.

## Recommended next development work

1. Observe a current-head Quality run and fix any lint/format/test/link/reference failure without weakening repository rules.
2. Keep `docs/repository-reference.md`, `docs/documentation-catalog.md`, and the relevant subsystem references synchronized with future path/responsibility changes.
3. If simultaneous multi-writer project editing is explicitly required, design a coordinated lock/revision protocol; otherwise retain the current simpler optimistic revision model.
4. Evaluate whether the desktop project/order UI should expose the CLI's synchronization preview/apply/second-removal-approval model.
5. Continue independent release-gate work for native-office fidelity, measured multi-gigabyte stress, human accessibility, clean-machine packaged applications, signing, and notarization.

## Continuation rule

Future sessions should read this file plus `what_changed.md`, inspect the current `main` head, and use the repository/source/test/automation/configuration/documentation references before changing a subsystem. Continue from repository evidence instead of re-implementing already committed features, and do not turn configured checks into claimed passing evidence without an observed run.
