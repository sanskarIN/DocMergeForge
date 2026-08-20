# DocMergeForge Project State

This file is the compact continuation checkpoint for future development sessions. Read it together with [`what_changed.md`](what_changed.md), the historical records under [`docs/history/`](docs/history/), and the repository/source/test/automation/configuration references before changing a subsystem.

## Current checkpoint

- Repository: `sanskarIN/DocMergeForge`
- Branch: `main`
- Version declared in `pyproject.toml`: `0.1.0`
- Checkpoint immediately before this state-file commit: `b2379226f7681ffe64a2dcfa3b9d59c75006bf30`
- Continuation base for the latest completed feature: `9775190f38e613e33f20aafc82b678a1ca3a233d`
- Development status: pre-stable; do not claim `v1.0.0`, production certification, native mobile packaging, or completed signing/notarization from source changes alone.

## Latest completed continuation: guarded desktop project synchronization

The desktop application now exposes the existing review-first project synchronization model that was previously available through the CLI.

### Maintained public desktop entry

`pyproject.toml` now routes:

```text
docmergeforge-gui = "docmergeforge.ui.desktop_entry:main"
```

`src/docmergeforge/ui/desktop_entry.py` provides `ProjectSyncMainWindow`, an extension of the established desktop `MainWindow` that adds **Synchronize Project Sources** without duplicating project discovery/synchronization business logic.

Normal installed desktop startup and normal packaged desktop startup both route through this synchronization-enabled entry.

### Desktop synchronization workflow

The maintained desktop flow is:

1. select a saved project JSON;
2. load the project and exact SHA-256 content revision from the same byte snapshot;
3. call the shared `plan_project_sync(...)` planner;
4. show a read-only preview containing current/proposed counts, additions, removals, reordering, duplicate parts, missing parts, and complete proposed order;
5. block Apply when same-kind duplicate numbered candidates make the proposal ambiguous;
6. treat an unchanged unambiguous project as a true no-op;
7. require a second explicit confirmation when paths would be removed from `selected_files`;
8. apply through the shared `apply_project_sync(...)` path while carrying the captured exact revision;
9. create the maintained versioned project backup for changed writes;
10. surface stale/write failures rather than silently retrying or overwriting an externally changed project;
11. update recent-project metadata after a successful apply;
12. leave manuscript source files untouched.

Synchronization does not automatically run a merge. Normal project dry-run/preflight remains the publication-readiness boundary.

### Synchronization safety boundary

Desktop and CLI synchronization intentionally share these rules:

- only numbered PDF/DOCX files inside the configured expected range enter the automatic proposal;
- deterministic ordering is used;
- PDF and DOCX duplicate detection is independent;
- same-kind duplicate part numbers block apply;
- missing parts remain evidence and may still be persisted for a work-in-progress project;
- manually selected unnumbered/out-of-range front/back matter can appear as removals and therefore requires explicit review/approval;
- removal changes project metadata only and never deletes source files;
- changed project JSON gets a versioned backup before atomic replacement;
- exact-revision and semantic stale-state checks remain active;
- a late guarded-save failure restores the caller's in-memory selection;
- unchanged synchronization does not create an unnecessary backup or rewrite.

The SHA-256 project revision mechanism is still an **optimistic stale-write guard**, not a universal cooperative cross-process lock. Do not represent simultaneous multi-writer editing as solved unless a separate coordinated locking/revision protocol is designed and accepted.

## New/changed runtime paths in the latest continuation

### Added

- `src/docmergeforge/ui/desktop_entry.py` — synchronization-enabled maintained desktop startup and workflow orchestration.
- `src/docmergeforge/ui/project_sync_dialog.py` — accessible synchronization review dialog.
- `tests/integration/test_project_sync_desktop.py` — offscreen Qt/workflow regression coverage for the new desktop path.
- `docs/history/what_changed-through-2026-08-20-cross-platform.md` — verbatim archive of the previous top-level development record before this desktop-sync continuation.

### Changed

- `pyproject.toml` — public GUI console-script target.
- `src/docmergeforge/ui/packaged_entry.py` — packaged startup/smoke uses the synchronization-enabled window.
- `src/docmergeforge/packaging/desktop.py` — packaging preflight requires the new desktop entry/dialog modules.
- `tests/unit/test_build_desktop.py` — packaging prerequisite coverage.
- `tests/unit/test_version_metadata.py` — pins maintained CLI/GUI/web public entry points.
- `README.md` — public desktop synchronization feature/safety description.
- `docs/desktop-guide.md` — operator workflow.
- `docs/project-sync.md` — shared desktop/CLI synchronization contract.
- `docs/source-code-reference.md` — runtime responsibility map.
- `docs/test-suite-reference.md` — test ownership/evidence map.
- `docs/repository-reference-cross-platform.md` — tracked-path coverage for the new files/archive.
- `what_changed.md` — current continuation record only; the preceding complete record is archived under `docs/history/`.

## Regression coverage added/expanded

`tests/integration/test_project_sync_desktop.py` protects:

- presence/accessibility of the desktop synchronization action;
- accessible complete preview content;
- disabled apply for ambiguous duplicate parts;
- exact revision propagation into the shared apply path;
- preview approval before removal approval;
- removal denial producing no project write;
- unchanged plan producing no project write;
- stale-revision failure surfacing through diagnostics/UI.

Additional related coverage:

- `tests/unit/test_build_desktop.py` requires the base window, desktop entry, sync dialog, and packaged entry in build-root preflight;
- `tests/unit/test_version_metadata.py` pins `docmergeforge`, `docmergeforge-gui`, and `docmergeforge-web` entry targets;
- `tests/integration/test_packaged_entry_smoke.py` now reaches the synchronization-enabled packaged window before the existing real temporary PDF/DOCX publication smoke.

Committed test source is implementation evidence only until execution is observed.

## Previous completed continuation: cross-platform browser hardening

The previous top-level development record is preserved verbatim at:

- `docs/history/what_changed-through-2026-08-20-cross-platform.md`.

Current cross-platform delivery remains:

- Windows 10/11: native desktop GUI, CLI, responsive web client;
- macOS: native desktop GUI, CLI, responsive web client;
- Linux: native desktop GUI, CLI, responsive web client;
- Android: responsive browser client connected to a DocMergeForge Python host; no native APK/AAB claim;
- iPhone/iPad: responsive browser client connected to a DocMergeForge Python host; no native IPA claim;
- ChromeOS/other modern browser platforms: responsive browser client connected to a DocMergeForge Python host.

Browser mode remains a network client to the Python host, not fully offline in-browser document processing. LAN token authentication is not transport encryption. Untrusted-network deployments require their own HTTPS/reverse-proxy/authentication/request-limit hardening rather than direct public exposure of the built-in server.

## Previous completed project-persistence and synchronization foundation

The desktop feature above builds on already-completed shared infrastructure:

- `project/store.py` exact content revisions, same-snapshot loading, guarded saves, symlink refusal, atomic persistence;
- `project/discovery.py` raw project-aware source discovery with nested-output exclusion;
- `project/sync.py` deterministic proposal planning, duplicate/missing evidence, versioned backups, removal approval, stale-plan checking, semantic/exact stale-write defenses, and no-op behavior;
- CLI `project-sync` preview/apply/`--allow-removals` flow;
- `project/drift.py` and project-sync CI/checking surfaces;
- desktop **Resume Project** exact-revision guard and recovery-checkpoint ordering.

Do not reimplement these foundations in UI-specific code unless the domain contract itself intentionally changes.

## Repository documentation coverage

The tracked-file documentation checker reads the maintained reference corpus:

- `docs/repository-reference.md`;
- `docs/repository-reference-cross-platform.md`.

The latest continuation added exact backticked references for every new tracked runtime/test/history path before or alongside the corresponding file becoming part of the maintained checkpoint.

The checker is configured in Quality and pre-commit. Configuration is not the same as an observed passing current-head execution.

## Verification boundary

Do not infer a green build merely from commits being present.

During the latest continuation:

- focused GitHub commit/tree/file inspection was used to keep changes scoped;
- packaging/source/test/documentation dependencies were cross-checked against the repository;
- an unintended temporary Ruff-rule-set expansion introduced while changing the GUI entry was immediately reverted in the next focused commit;
- the maintained Ruff rule set remains `E/F/I/B/UP/SIM/C4`;
- a raw GitHub archive/checkout could not be obtained in the execution environment, so local quality/test execution was not available;
- repository workflow definitions remain configured for Quality/Build Smoke, but no fresh passing current-head execution is claimed without observed run evidence.

Until observed for the current head, no fresh pass is claimed for:

- Ruff;
- Black check;
- strict mypy;
- Markdown link validation;
- repository-reference coverage execution;
- pytest/coverage;
- Quality workflow matrix;
- 120-Part Regression;
- Build Smoke;
- Package Desktop / Onefile Acceptance;
- Security/CodeQL;
- representative Android/iOS/iPadOS/ChromeOS/manual browser acceptance;
- human desktop accessibility/clean-machine acceptance.

External-office, measured stress, signing/notarization, and other release gates remain independent.

## Repository administration state observed during this continuation

GitHub branch metadata reported `main` as not protected, with required status checks disabled at the repository-rules layer at the inspected checkpoint.

This is an administrative governance state, not an application correctness failure. If enforced review/CI policy on `main` is desired, configure branch protection/rulesets through repository administration with the intended required checks. Do not claim protection is enabled until repository metadata confirms it.

## Recommended next development work

1. Observe a current-head Quality run; fix any lint/format/type/test/link/reference failure without weakening maintained rules.
2. Review current Build Smoke and packaged-app results specifically for the synchronization-enabled desktop entry on Windows, macOS, and Linux.
3. If a convenience shortcut from **Recent Projects** into synchronization is added, preserve the same preview, duplicate blocking, separate removal approval, exact revision, and backup semantics; do not bypass them.
4. Keep synchronization domain rules centralized in `project.sync` rather than forking CLI and desktop business logic.
5. Perform representative manual browser/device acceptance for the responsive cross-platform client.
6. If Internet/untrusted-network hosting is intentionally supported later, define and acceptance-test an explicit HTTPS reverse-proxy/authentication/body-limit/timeout/concurrency/host-hardening deployment profile.
7. If simultaneous multi-writer project editing becomes a supported requirement, design a separate coordinated lock/revision protocol rather than relabeling the optimistic revision guard.
8. Continue independent release-gate work for native-office fidelity, measured multi-gigabyte stress, human accessibility, clean-machine packaged applications, Windows signing, and macOS signing/notarization.
9. Keep README, project-sync/desktop/source/test references, repository-reference corpus, `what_changed.md`, and this checkpoint synchronized whenever the boundary changes.

## Continuation rule

Future sessions should inspect the actual current `main` head, read this file plus `what_changed.md`, and consult the repository/source/test/automation/configuration references before modifying a subsystem. Continue from repository evidence instead of re-opening completed work, and never turn configured automation or committed tests into claimed passing evidence without an observed run.
