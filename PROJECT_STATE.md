# DocMergeForge Project State

This file is the compact continuation checkpoint for future development sessions. Read it together with [`what_changed.md`](what_changed.md), the historical records under [`docs/history/`](docs/history/), and the repository/source/test/automation/configuration references before changing a subsystem.

## Current checkpoint

- Repository: `sanskarIN/DocMergeForge`
- Target branch: `main`
- Active release-preparation branch: `release/2.8.5-prep`
- Version declared in `pyproject.toml`: `2.8.5`
- Release-preparation base: `aac5bf6d275991e21b68e15f5ad31f084fbc72e2`
- Development/release status: `2.8.5` candidate preparation; package versioning does **not** by itself certify production readiness, native mobile packaging, signing/notarization, human accessibility acceptance, or external-office fidelity.

## Latest continuation: 2.8.5 release preparation

The `2.8.5` preparation pass is intentionally evidence-first. It updates package/runtime version metadata and release-facing documentation without converting unobserved CI, packaging, device, accessibility, stress, signing, or fidelity gates into passing claims.

### Release metadata

The candidate version is synchronized across:

- `pyproject.toml` — package version `2.8.5`;
- `src/docmergeforge/__init__.py` — runtime `__version__ = "2.8.5"`;
- `tests/unit/test_version_metadata.py` — package/runtime synchronization plus an explicit `2.8.5` candidate pin.

The existing pre-alpha distribution classifier remains intentionally conservative. A numeric version change is not used as a substitute for release acceptance evidence.

### Workflow-generation cleanup

The focused Project Sync Safety workflow was the remaining workflow still using older GitHub Action majors. The release-preparation branch aligns it with the repository's maintained Node-24-era action generations:

- `actions/checkout@v7`;
- `actions/setup-python@v7`.

This incorporates the substantive changes proposed independently by Dependabot PRs #3 and #4 into one reviewed release-preparation line. The PRs should be closed as superseded after the release branch is merged, not represented as separately required product work.

### Recent-project synchronization status corrected

The desktop convenience shortcut from **Recent Projects** into the guarded synchronization workflow is already implemented on current `main` and covered by integration tests. It is no longer future work.

`ProjectSyncMainWindow` exposes both:

- **Synchronize Project Sources** — browse for a project JSON;
- **Synchronize Recent Project** — select from maintained recent-project history.

Both routes converge on the same `_synchronize_project_path(...)` guarded workflow and therefore preserve the same preview, duplicate blocking, separate removal approval, exact-revision propagation, backup, stale-write, and metadata-only semantics.

## Previous completed continuation: guarded desktop project synchronization

The desktop application exposes the existing review-first project synchronization model that was previously available through the CLI.

### Maintained public desktop entry

`pyproject.toml` routes:

```text
docmergeforge-gui = "docmergeforge.ui.desktop_entry:main"
```

`src/docmergeforge/ui/desktop_entry.py` provides `ProjectSyncMainWindow`, an extension of the established desktop `MainWindow` that adds synchronization actions without duplicating project discovery/synchronization business logic.

Normal installed desktop startup and normal packaged desktop startup both route through this synchronization-enabled entry.

### Desktop synchronization workflow

The maintained desktop flow is:

1. select a saved project JSON directly or through recent-project history;
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

## Runtime and documentation paths associated with desktop synchronization

### Added in the desktop-sync continuation

- `src/docmergeforge/ui/desktop_entry.py` — synchronization-enabled maintained desktop startup and workflow orchestration.
- `src/docmergeforge/ui/project_sync_dialog.py` — accessible synchronization review dialog.
- `tests/integration/test_project_sync_desktop.py` — offscreen Qt/workflow regression coverage for the desktop path, including browse and recent-project routing.
- `docs/history/what_changed-through-2026-08-20-cross-platform.md` — verbatim archive of the previous top-level development record before the desktop-sync continuation.

### Changed across the synchronization/release-prep boundary

- `pyproject.toml` — public GUI console-script target and `2.8.5` candidate package version.
- `src/docmergeforge/__init__.py` — `2.8.5` runtime package version.
- `src/docmergeforge/ui/packaged_entry.py` — packaged startup/smoke uses the synchronization-enabled window.
- `src/docmergeforge/packaging/desktop.py` — packaging preflight requires the desktop entry/dialog modules.
- `.github/workflows/project-sync-safety.yml` — focused safety matrix and maintained action majors.
- `tests/unit/test_build_desktop.py` — packaging prerequisite coverage.
- `tests/unit/test_version_metadata.py` — pins maintained CLI/GUI/web public entry points and the `2.8.5` candidate version.
- `README.md` — public desktop synchronization feature/safety description and release-preparation status.
- `docs/desktop-guide.md` — operator workflow.
- `docs/project-sync.md` — shared desktop/CLI synchronization contract.
- `docs/source-code-reference.md` — runtime responsibility map.
- `docs/test-suite-reference.md` — test ownership/evidence map.
- `docs/repository-reference-cross-platform.md` — tracked-path coverage for the cross-platform/desktop additions.
- `docs/release-process.md` — versioning/release evidence policy.
- `docs/release-evidence.md` — evidence ledger; candidate evidence must use exact run/checkpoint IDs.
- `CHANGELOG.md` — release-preparation record.
- `what_changed.md` — active continuation record.

## Regression coverage added/expanded

`tests/integration/test_project_sync_desktop.py` protects:

- presence/accessibility of both desktop synchronization actions;
- browse-project routing;
- recent-project routing;
- accessible complete preview content;
- disabled apply for ambiguous duplicate parts;
- exact revision propagation into the shared apply path;
- preview approval before removal approval;
- removal denial producing no project write;
- unchanged plan producing no project write;
- stale-revision failure surfacing through diagnostics/UI.

Additional related coverage:

- `tests/unit/test_build_desktop.py` requires the base window, desktop entry, sync dialog, and packaged entry in build-root preflight;
- `tests/unit/test_version_metadata.py` pins `docmergeforge`, `docmergeforge-gui`, and `docmergeforge-web` entry targets and candidate version metadata;
- `tests/integration/test_packaged_entry_smoke.py` reaches the synchronization-enabled packaged window before the existing real temporary PDF/DOCX publication smoke.

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

The checker is configured in Quality and pre-commit. Configuration is not the same as an observed passing candidate-head execution.

## Verification boundary

Do not infer a green build merely from commits being present.

For the `2.8.5` candidate, no fresh pass is claimed until the exact release-preparation head is observed for the relevant gates. Required source evidence includes:

- pre-commit configuration validation;
- Ruff;
- Black check;
- strict mypy;
- Markdown link validation;
- repository-reference coverage execution;
- pytest/coverage;
- Quality workflow matrix;
- 120-Part Regression;
- Build Smoke;
- Project Sync Safety matrix;
- Security/CodeQL.

Packaging/release evidence remains separate:

- Package Desktop / Onefile Acceptance on Windows, macOS, and Linux;
- downloaded-artifact verification;
- representative Android/iOS/iPadOS/ChromeOS/manual browser acceptance;
- human desktop accessibility/clean-machine acceptance;
- external-office fidelity acceptance;
- measured stress at the workload class actually claimed;
- Windows signing;
- macOS signing/notarization;
- final distribution/installer acceptance where applicable.

Older recorded passing runs remain historical evidence for their exact checkpoints and must not be relabeled as `2.8.5` candidate evidence.

## Repository administration state

At the release-preparation base, GitHub branch metadata reported `main` as not protected, with required status checks disabled at the repository-rules layer.

This is an administrative governance state, not an application correctness failure. If enforced review/CI policy on `main` is desired, configure branch protection/rulesets through repository administration with the intended required checks. Do not claim protection is enabled until repository metadata confirms it.

## Recommended next development work

1. Open/review the `release/2.8.5-prep` pull request and observe Quality plus the focused Project Sync Safety checks for the exact candidate head.
2. Fix any Ruff/Black/mypy/docs/reference/pytest/CI failure without weakening maintained checks.
3. Review current 120-Part Regression, Build Smoke, Security/CodeQL, Package Desktop, and Onefile Acceptance evidence for the exact candidate commit.
4. Keep synchronization domain rules centralized in `project.sync`; both browse and recent-project desktop actions must continue to converge on the shared guarded workflow.
5. Perform representative manual browser/device acceptance for the responsive cross-platform client.
6. If Internet/untrusted-network hosting is intentionally supported later, define and acceptance-test an explicit HTTPS reverse-proxy/authentication/body-limit/timeout/concurrency/host-hardening deployment profile.
7. If simultaneous multi-writer project editing becomes a supported requirement, design a separate coordinated lock/revision protocol rather than relabeling the optimistic revision guard.
8. Continue independent release-gate work for native-office fidelity, measured multi-gigabyte stress, human accessibility, clean-machine packaged applications, Windows signing, and macOS signing/notarization.
9. Native Android APK/AAB and native iOS IPA delivery remain separate implementation tracks; browser support must not be relabeled as native packaging.
10. Keep README, changelog, release-process/evidence docs, project-sync/desktop/source/test references, repository-reference corpus, `what_changed.md`, and this checkpoint synchronized whenever the release boundary changes.

## Continuation rule

Future sessions should inspect the actual current `main` and any active release branch, read this file plus `what_changed.md`, and consult the repository/source/test/automation/configuration/release references before modifying a subsystem. Continue from repository evidence instead of re-opening completed work, and never turn configured automation or committed tests into claimed passing evidence without an observed run for the exact checkpoint.
