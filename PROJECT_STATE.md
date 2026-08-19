# DocMergeForge Project State

This file is a compact continuation checkpoint for future development sessions. Detailed change history belongs in [`what_changed.md`](what_changed.md) and historical records under [`docs/history/`](docs/history/).

## Current checkpoint

- Repository: `sanskarIN/DocMergeForge`
- Branch: `main`
- Version declared in `pyproject.toml`: `0.1.0`
- Checkpoint immediately before this state-file commit: `991253b7f386fb68a4c96758ca600b001e728de2`
- Development status: pre-stable; do not claim `v1.0.0` or production certification from source changes alone.

## Newly completed implementation surface

The latest continuation added guarded project-selection synchronization.

Implemented components:

- `src/docmergeforge/project/discovery.py`
  - raw project-source discovery independent of persisted `selected_files` filtering;
  - recursive source scanning;
  - exclusion of a strictly nested project output subtree.
- `src/docmergeforge/project/sync.py`
  - deterministic synchronization planning;
  - automatic candidate rule limited to numbered PDF/DOCX files inside the configured expected range;
  - platform-aware resolved-path de-duplication;
  - `current`/`proposed`/`added`/`removed`/`reordered` evidence;
  - versioned project backup before changed writes;
  - atomic project replacement through the maintained project persistence path;
  - symlinked project-file refusal;
  - stale in-memory selection guard;
  - no-op behavior without backup/rewrite.
- `docmergeforge project-sync`
  - preview-only by default;
  - `--apply` for reviewed mutation;
  - separate `--allow-removals` approval when existing selected paths would be removed;
  - structured JSON output and handled `OSError`/safety failures.

## Why removal approval is separate

A project can intentionally select unnumbered front/back matter or other material outside the automatic numbered/in-range rule. Such paths appear in a synchronization proposal's `removed` list.

Therefore:

```bash
docmergeforge project-sync --project "./Book.json" --apply
```

must not remove existing selections by itself. Intentional removals require:

```bash
docmergeforge project-sync \
  --project "./Book.json" \
  --apply \
  --allow-removals
```

The flag changes project metadata only; it never deletes manuscript source files.

## Test coverage added in this continuation

New synchronization tests cover:

- nested-output exclusion during raw project discovery;
- numbered/in-range PDF/DOCX eligibility;
- deterministic ordering;
- added/removed/reordered diff evidence;
- project backup creation;
- preservation/versioning of an existing `.bak` file;
- atomic project replacement behavior;
- no-op synchronization without writes;
- stale-plan/in-memory-selection rejection;
- symlinked project-file refusal;
- CLI parsing/preview/apply behavior;
- second approval for removals;
- approved removals with backup preservation;
- structured CLI handling of project-sync write failures.

These tests are committed source coverage. They must not be represented as passing current-head CI until an actual run is observed.

## Documentation updated

Current documentation now includes:

- [`docs/project-sync.md`](docs/project-sync.md) — dedicated safety/operator guide;
- [`docs/project-files.md`](docs/project-files.md) — project metadata and synchronization semantics;
- [`docs/cli-reference.md`](docs/cli-reference.md) — complete command/options/output/exit behavior;
- [`docs/audit-and-compare.md`](docs/audit-and-compare.md) — safe bridge from review findings to an independently reviewed selection refresh;
- [`docs/development-phases.md`](docs/development-phases.md) — v0.2 project-workflow milestone/status;
- root [`README.md`](README.md) and [`docs/README.md`](docs/README.md) navigation/usage links.

## Verification boundary

Do not infer a green build merely from commits being present.

At this checkpoint, the repository still needs current-head evidence for the normal source-quality gates, including as applicable:

- Ruff;
- Black check;
- strict mypy;
- Markdown link validation;
- pytest/coverage;
- Quality workflow matrix;
- 120-Part Regression;
- Build Smoke;
- Security/CodeQL.

External-office, stress, accessibility, clean-machine packaging, signing/notarization, and other release gates remain independent from this project-sync work.

## Recommended next development work

1. Observe current-head CI and fix any synchronization-specific lint/type/test/documentation failure without weakening repository rules.
2. Consider eliminating the remaining duplicate raw-discovery logic in `MergeApplicationService.discover()` by safely routing it through `discover_project_sources()` once regression evidence is available.
3. Consider a project-file revision/concurrency guard around synchronization apply if multi-writer project editing is intended; normal project persistence is currently documented as last-writer-wins rather than collaborative locking.
4. Evaluate whether the desktop project/order UI should expose the same preview/apply synchronization model without weakening its explicit review semantics.
5. Continue the existing independent release-gate work for native-office fidelity, measured large-scale stress, human accessibility, clean-machine packaged applications, signing, and notarization.

## Continuation rule

Future sessions should read this file plus `what_changed.md`, inspect the current `main` head, and continue from repository evidence instead of re-implementing already committed features.
