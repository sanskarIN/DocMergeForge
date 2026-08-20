# What Changed

This file records the **current** DocMergeForge development continuation. Earlier detailed records are preserved so this top-level checkpoint remains fast to review:

- [`docs/history/what_changed-through-2026-08-18.md`](docs/history/what_changed-through-2026-08-18.md) — earlier repository development history;
- [`docs/history/what_changed-through-2026-08-20-cross-platform.md`](docs/history/what_changed-through-2026-08-20-cross-platform.md) — the complete top-level record through the responsive cross-platform web/security continuation immediately preceding this one.

A source change, test file, workflow definition, or commit is implementation/configuration evidence only. It is not represented as a passing CI, packaged-app, browser/device, accessibility, external-office, signing, notarization, or production-release result unless that exact evidence was observed.

## 2026-08-20 — Guarded desktop project synchronization

### Goal completed

The desktop application now exposes the CLI project's review-first synchronization model instead of requiring desktop users to switch to the command line when a saved project's source membership changes.

The implementation deliberately **reuses** the existing `docmergeforge.project.sync` planner/apply path. It does not create a second desktop-only discovery or selection algorithm.

### Added

- Added `src/docmergeforge/ui/project_sync_dialog.py`:
  - accessible **Synchronize Project Sources** preview dialog;
  - read-only current/proposed selected-file counts;
  - additions and removals;
  - complete proposed order;
  - reordering state;
  - duplicate PDF/DOCX part evidence;
  - missing PDF/DOCX part evidence;
  - `safe_to_apply` and numbered-completeness evidence;
  - Apply disabled for unchanged or ambiguous same-kind duplicate proposals;
  - explicit text that synchronization mutates project metadata only and never deletes manuscript source files.
- Added `src/docmergeforge/ui/desktop_entry.py`:
  - maintained `docmergeforge-gui` startup;
  - `ProjectSyncMainWindow`, extending the established desktop window without rewriting the existing merge UI;
  - a first-class **Synchronize Project Sources** home action;
  - exact project+revision snapshot loading before preview;
  - shared `plan_project_sync(...)` planning;
  - separate removal confirmation after preview approval;
  - shared `apply_project_sync(...)` persistence with the captured exact revision;
  - successful recent-project refresh and local diagnostic logging;
  - handled stale/write failures surfaced to the desktop user.
- Added `tests/integration/test_project_sync_desktop.py` with offscreen Qt integration coverage for:
  - the accessible home action;
  - complete preview/accessibility state;
  - duplicate-part apply blocking;
  - exact-revision propagation into apply;
  - separate removal approval before write;
  - declined removal approval producing no write;
  - unchanged synchronization producing a no-op;
  - stale project-revision failure surfacing rather than silent overwrite.

### Changed

- `pyproject.toml` now routes the public desktop console script through the maintained synchronization-enabled entry:

  ```text
  docmergeforge-gui = "docmergeforge.ui.desktop_entry:main"
  ```

- `src/docmergeforge/ui/packaged_entry.py` now:
  - delegates normal packaged startup to the synchronization-enabled desktop entry;
  - instantiates `ProjectSyncMainWindow` during packaged GUI smoke;
  - retains the existing real temporary PDF/DOCX publication smoke after GUI initialization.
- `src/docmergeforge/packaging/desktop.py` now requires all maintained desktop startup modules during `build_desktop.py --check`:
  - `ui/main.py`;
  - `ui/desktop_entry.py`;
  - `ui/project_sync_dialog.py`;
  - `ui/packaged_entry.py`.
- `tests/unit/test_build_desktop.py` now protects those packaging prerequisites.
- `tests/unit/test_version_metadata.py` now pins all maintained public console entry points so metadata drift cannot silently bypass the desktop synchronization entry.
- The root `README.md` now publicly describes guarded desktop synchronization, its metadata-only boundary, duplicate blocking, second removal approval, backup behavior, and exact-revision stale-write protection.

### Shared synchronization safety preserved

The desktop workflow preserves the same domain rules as the CLI:

- automatic proposals contain numbered PDF/DOCX files inside the configured expected range;
- proposal order is deterministic;
- same-kind duplicate part numbers make the plan ambiguous and block apply;
- a PDF Part 1 plus DOCX Part 1 is valid because the pipelines are independent;
- missing parts remain review/preflight evidence and do not by themselves prohibit a work-in-progress metadata synchronization;
- manually selected unnumbered/out-of-range front/back matter can appear as removals and therefore receives a separate approval gate;
- removals affect only `selected_files`; source files are never deleted;
- changed writes create a versioned project backup;
- project persistence remains atomic;
- the captured exact SHA-256 project revision is carried through apply;
- semantic stale-state checking remains an additional defense;
- a stale project write fails instead of silently replacing externally changed project JSON;
- unchanged synchronization is a true no-op.

The exact revision mechanism remains an optimistic stale-write guard, not a universal cooperative multi-process lock. True simultaneous multi-writer editing would require a separately designed locking/revision protocol.

### Documentation synchronized

Updated:

- `README.md`;
- `docs/desktop-guide.md`;
- `docs/project-sync.md`;
- `docs/source-code-reference.md`;
- `docs/test-suite-reference.md`;
- `docs/repository-reference-cross-platform.md`.

The repository-reference addendum explicitly catalogs the new desktop runtime/test paths and this archived prior progress record so the tracked-file documentation contract remains maintainable.

### Packaging and entry-point hardening

The new desktop feature is not source-only:

- editable/wheel installs launch it through `docmergeforge-gui`;
- packaged application startup launches the same synchronization-enabled window;
- packaged smoke constructs that window before the real publication smoke;
- packaging preflight refuses a repository missing the new desktop entry/dialog modules;
- metadata regression tests pin CLI, GUI, and web console targets.

### Commits in this continuation before this record reset

- `f6bb8ffcf72500655006c392844963fcb6459d03` — `feat(ui): add project synchronization preview dialog`.
- `1ec59c4923961b8a34e8a3badaabc993937fc2c8` — `docs(reference): catalog desktop project sync dialog`.
- `61f2f76ce434f1c5aacaa16fc3cedb1092971b69` — `feat(ui): add guarded project sync desktop entry`.
- `030ae008027a2db626467ad4f393947677428120` — `docs(reference): catalog desktop sync entry wrapper`.
- `ae4941527bdb13690da4bfc829743dc367d120f7` — `feat(gui): route desktop script through sync-enabled entry`.
- `b8328a73266896418d26202713e7f910c08951a2` — `fix(config): preserve existing Ruff rule set`.
- `f3d3459da45a1401861558564e08065894f621f2` — `feat(package): include project sync in desktop builds`.
- `b5df252f6bcf3c0e228a8521905ba0f05985008a` — `refactor(ui): make sync desktop startup type-safe`.
- `e68326c6b73ebaae6b5556b8e7ed6d98c3fe3e8f` — `test(ui): cover guarded desktop project synchronization`.
- `de0f230af41d1dae9a76651df6f0a069a5cfbc50` — `docs(reference): catalog desktop sync tests`.
- `1d97e32d6608f343ab40d530f533ad9ecbd886ed` — `fix(package): require sync desktop modules in build preflight`.
- `9dff239d21b0dbdd69c0bdfe3c0bc6d0c5f0cab8` — `test(package): cover sync desktop build prerequisites`.
- `2676b7b089cdd55e67a560e51f1ec23dafe19883` — `test(metadata): pin maintained public entry points`.
- `9cfcec0061879daf80da37779ef39d08db5b3be7` — `docs(gui): document guarded project synchronization`.
- `f3ce13fc4d4986f5dd835699d70be625a79fb918` — `test(ui): extend desktop sync accessibility and stale-write coverage`.
- `4b1241f3fda5e31a450176cd7a5df2871cbb2b88` — `docs(test): map desktop project synchronization coverage`.
- `8de85cca9352e2d73ca1ea162eeeb2f755ae658c` — `docs(reference): map sync-enabled desktop architecture`.
- `abb6aae3a0fe14c81575263105a9ab079a509925` — `docs(sync): document shared desktop and CLI workflow`.
- `b4928c15d1fda743966db23f91b5cc235a55f406` — `refactor(test): simplify stale project sync failure helper`.
- `ef440e92bd750862b15fde5df90e940471428175` — `test(ui): cover unchanged desktop synchronization no-op`.
- `8ac078d1f0ccc5aa014cea4a551713cb0ff12046` — `docs(readme): expose guarded desktop project synchronization`.
- `ceb27871b64c500121d2fb89da1317dc21b32171` — `docs(reference): catalog archived cross-platform progress record`.

One intermediate `pyproject.toml` write accidentally added Ruff's `S` rule family while changing the GUI entry point. It was immediately reverted in the next focused commit (`b8328a7...`). The repository's maintained Ruff rule set remains `E/F/I/B/UP/SIM/C4`; this continuation does not weaken or silently broaden lint policy.

### Verification status

- Continuation base: `9775190f38e613e33f20aafc82b678a1ca3a233d`.
- Latest implementation/documentation checkpoint immediately before this active-record reset: `ceb27871b64c500121d2fb89da1317dc21b32171`.
- A compare from the continuation base through the pre-record checkpoint shows the expected GUI/project-sync/packaging/test/documentation surfaces and no unrelated document-engine rewrite.
- The public repository remains version `0.1.0` / pre-stable.
- Branch metadata inspected during this continuation reports `main` as not protected and required status checks disabled at the repository-rules layer. This is repository-administration state, not an application defect; enabling branch protection remains an administrative decision.
- The execution environment could not obtain a raw GitHub archive/checkout, so no local current-head Ruff, Black, mypy, docs checker, repository-reference checker, or pytest run is claimed.
- GitHub workflow definitions remain configured to run Quality on `main`, but configured automation is not treated as an observed passing current-head result.

### Remaining next work

1. Observe a current-head Quality run and fix any Ruff/Black/mypy/docs/reference/pytest failure without weakening the checks.
2. Review Build Smoke/package results for the synchronization-enabled desktop entry and fix any platform-specific startup or PyInstaller issue found by real runners.
3. Consider a recent-project shortcut into synchronization only if it can preserve the same explicit preview/removal/stale-write approvals; do not bypass the current safety gates for convenience.
4. Keep the desktop and CLI synchronization semantics shared in `project.sync`; do not fork them into UI-specific business logic.
5. Perform representative manual browser/device acceptance for the responsive cross-platform client.
6. Continue independent release gates for native-office fidelity, measured multi-gigabyte stress, human accessibility, clean-machine packaged apps, Windows signing, and macOS signing/notarization.
7. Do not claim `v1.0.0`, native mobile APK/AAB/IPA delivery, universal multi-writer project locking, or production certification until corresponding implementation and acceptance evidence exists.
