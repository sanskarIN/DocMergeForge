# What Changed

This file records the **current** DocMergeForge development continuation. Earlier detailed records are preserved so this top-level checkpoint remains fast to review:

- [`docs/history/what_changed-through-2026-08-18.md`](docs/history/what_changed-through-2026-08-18.md) — earlier repository development history;
- [`docs/history/what_changed-through-2026-08-20-cross-platform.md`](docs/history/what_changed-through-2026-08-20-cross-platform.md) — the complete top-level record through the responsive cross-platform web/security continuation immediately preceding desktop synchronization.

A source change, test file, workflow definition, or commit is implementation/configuration evidence only. It is not represented as a passing CI, packaged-app, browser/device, accessibility, external-office, signing, notarization, or production-release result unless that exact evidence was observed.

## 2026-08-24 — Version 2.8.5 release preparation

### Goal

Prepare DocMergeForge package/runtime/release metadata for `2.8.5`, remove stale continuation guidance, and close the remaining GitHub Actions generation mismatch without claiming unobserved release acceptance.

This work is based on `main` checkpoint `aac5bf6d275991e21b68e15f5ad31f084fbc72e2` and is being developed on `release/2.8.5-prep` for review before merge.

### Version metadata synchronized

- `pyproject.toml` now declares `version = "2.8.5"`.
- `src/docmergeforge/__init__.py` now exposes `__version__ = "2.8.5"`.
- `tests/unit/test_version_metadata.py` retains package/runtime equality checking and now pins `EXPECTED_RELEASE_VERSION = "2.8.5"` so candidate drift fails explicitly.
- The existing pre-alpha classifier remains conservative. The numeric version is not treated as proof of production readiness.

### Project Sync Safety workflow aligned

`.github/workflows/project-sync-safety.yml` was the remaining focused workflow using older GitHub Action generations. It now uses:

```text
actions/checkout@v7
actions/setup-python@v7
```

This matches the maintained Node-24-era action generation documented elsewhere in the repository. Dependabot PR #3 and PR #4 propose the same two one-line upgrades independently; after this combined release-preparation change is merged, those PRs can be closed as superseded rather than merged separately.

### Recent-project synchronization is complete

The earlier continuation record listed a Recent Projects synchronization shortcut as possible future work. That item is now complete on `main`.

`ProjectSyncMainWindow` exposes two stable accessible actions:

- **Synchronize Project Sources** for browsing to a project JSON;
- **Synchronize Recent Project** for selecting from maintained recent-project history.

Both routes call the same `_synchronize_project_path(...)` workflow. They therefore preserve the shared `project.sync` planner/apply semantics, full preview, same-kind duplicate blocking, unchanged no-op behavior, separate removal approval, exact revision propagation, backup behavior, stale-write failure surfacing, and metadata-only mutation boundary.

The integration suite covers both browse and recent-project routing in addition to the synchronization safety contract.

### Project checkpoint synchronized

`PROJECT_STATE.md` now records:

- target `main` plus active `release/2.8.5-prep` branch;
- package version `2.8.5`;
- release-preparation base `aac5bf6d275991e21b68e15f5ad31f084fbc72e2`;
- the Recent Projects shortcut as completed rather than future work;
- exact candidate verification gates that still require observed evidence.

### Focused commits in this continuation

- `253aed48f661b5009c95d2a298cb7038081ac1f8` — `ci(sync): align focused workflow action majors`.
- `4eda83909a62fb2fd6dbf6a3ca05da6e50b681a8` — `chore(version): prepare package metadata for 2.8.5`.
- `1823ff8bf406055298dbdaed82f84a83d836196a` — `chore(version): expose 2.8.5 package version`.
- `67015d621ca4b86ab4731b79dded7e0badd967e8` — `test(version): pin 2.8.5 release candidate metadata`.
- `1ee0e76d6714cd4c2c15c02dc6c8edaeab918454` — `docs(state): advance checkpoint to 2.8.5 preparation`.

### Verification boundary for 2.8.5

No fresh candidate-head pass is claimed yet. Before `2.8.5` is treated as release-verified, observe and review the exact candidate commit for the applicable gates, including:

- Quality on Python 3.12 and 3.13;
- Project Sync Safety on Ubuntu, Windows, and macOS;
- 120-Part Regression;
- Build Smoke on Ubuntu, Windows, and macOS;
- Security/CodeQL;
- Package Desktop and Onefile Acceptance if those artifacts are distributed;
- downloaded-artifact verification;
- release documentation/reference checks.

Human/production gates remain independent: representative device/browser acceptance, clean-machine desktop UX, human accessibility, real-world office fidelity, claimed-scale stress evidence, Windows signing, macOS signing/notarization, and any installer/distribution acceptance.

Historical workflow runs remain evidence only for their exact historical checkpoints; they are not relabeled as `2.8.5` evidence.

### Remaining next work after this preparation pass

1. Finish release-document synchronization (`CHANGELOG.md`, README release-status wording, release-process/evidence wording) for `2.8.5`.
2. Open/review the release-preparation PR and observe its exact CI results.
3. Fix any candidate-head lint/format/type/test/docs/reference failure without weakening checks.
4. Run/review cross-platform regression, build, security, packaging, and downloaded-artifact gates appropriate to the intended `2.8.5` distribution.
5. Continue representative browser/device acceptance; browser support is not native APK/AAB/IPA packaging.
6. Continue native-office fidelity, measured large-stress, human accessibility, clean-machine, signing/notarization, and distribution acceptance independently.
7. Keep synchronized project discovery/business rules centralized in `project.sync`; do not fork browse/recent/CLI semantics.
8. If simultaneous multi-writer project editing becomes required, design a coordinated lock/revision protocol rather than relabeling the optimistic SHA-256 stale-write guard.

## 2026-08-20 — Guarded desktop project synchronization

> Historical continuation below. Its original “remaining next work” list is superseded by the `2026-08-24` section above where later commits completed the Recent Projects shortcut and began `2.8.5` preparation.

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

- `pyproject.toml` routes the public desktop console script through the maintained synchronization-enabled entry:

  ```text
  docmergeforge-gui = "docmergeforge.ui.desktop_entry:main"
  ```

- `src/docmergeforge/ui/packaged_entry.py` delegates normal packaged startup to the synchronization-enabled desktop entry, instantiates `ProjectSyncMainWindow` during packaged GUI smoke, and retains the existing real temporary PDF/DOCX publication smoke after GUI initialization.
- `src/docmergeforge/packaging/desktop.py` requires all maintained desktop startup modules during `build_desktop.py --check`: `ui/main.py`, `ui/desktop_entry.py`, `ui/project_sync_dialog.py`, and `ui/packaged_entry.py`.
- `tests/unit/test_build_desktop.py` protects those packaging prerequisites.
- `tests/unit/test_version_metadata.py` pins all maintained public console entry points so metadata drift cannot silently bypass the desktop synchronization entry.
- The root `README.md` describes guarded desktop synchronization, its metadata-only boundary, duplicate blocking, second removal approval, backup behavior, and exact-revision stale-write protection.

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

The repository-reference addendum catalogs the new desktop runtime/test paths and archived prior progress record so the tracked-file documentation contract remains maintainable.

### Packaging and entry-point hardening

The desktop feature is not source-only:

- editable/wheel installs launch it through `docmergeforge-gui`;
- packaged application startup launches the same synchronization-enabled window;
- packaged smoke constructs that window before the real publication smoke;
- packaging preflight refuses a repository missing the new desktop entry/dialog modules;
- metadata regression tests pin CLI, GUI, and web console targets.

### Commits in that continuation before the record reset

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

One intermediate `pyproject.toml` write accidentally added Ruff's `S` rule family while changing the GUI entry point. It was immediately reverted in the next focused commit (`b8328a7...`). The maintained Ruff rule set remains `E/F/I/B/UP/SIM/C4`; that continuation did not weaken or silently broaden lint policy.

### Historical verification status

- Continuation base: `9775190f38e613e33f20aafc82b678a1ca3a233d`.
- Pre-record checkpoint: `ceb27871b64c500121d2fb89da1317dc21b32171`.
- At that checkpoint the package metadata was still `0.1.0`; the later `2026-08-24` continuation above supersedes that version state.
- Branch metadata reported `main` as not protected and required status checks disabled at the repository-rules layer.
- No current-candidate test result should be inferred from the existence of committed tests/workflows.

### Historical next-work list

The original list included current-head Quality/build/package review, the then-unimplemented Recent Projects shortcut, manual browser/device acceptance, shared synchronization semantics, and independent release gates. The shortcut is now complete; the remaining applicable gates are carried forward in the `2026-08-24` section above.
