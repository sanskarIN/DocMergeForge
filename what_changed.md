# What Changed

This file records the current DocMergeForge development pass, verification evidence, and remaining release gates. Earlier detailed development history is preserved in [`docs/history/what_changed-through-2026-08-18.md`](docs/history/what_changed-through-2026-08-18.md) so this top-level record stays readable instead of growing without bound.

An item is not treated as finished merely because code was pushed. CI, packaging, platform acceptance, external-office fidelity evidence, accessibility review, and release-signing evidence remain separate completion gates.

## 2026-08-19 — Project-file revision guards and stale-write protection

### Added
- Added `project_file_revision(...)` in `src/docmergeforge/project/store.py` to derive an exact SHA-256 content revision from the persisted project bytes.
- Added `load_project_snapshot(...)` so a project object and its revision token come from the same exact byte snapshot instead of separate reads that could observe different file states.
- Added `save_project_if_revision(...)` as an optimistic compare-before-save primitive for editing an existing project. It refuses a write when the current project bytes no longer match the revision observed at load.
- Added exact-revision support to `apply_project_sync(...)` so synchronization callers can carry their initial project snapshot revision through apply and final persistence.
- Added regression coverage for snapshot revision identity, successful guarded saves, stale content rejection without overwrite, symbolic-link project-save refusal, CLI byte-level drift rejection, and structured `project-create` save failures.

### Changed
- Generic project saving now refuses a destination addressed through a symbolic link before validating/serializing project data.
- Desktop **Resume Project** now loads the project and exact revision together, allows order review, and saves only if the project still matches the observed revision. A project changed externally during the interaction is not overwritten.
- Desktop project creation now catches project-save failures, records them in diagnostics, surfaces a critical dialog, and stops instead of letting the persistence exception escape the UI callback.
- Desktop ordering and SQL-preset recovery checkpoints now go through a shared UI helper that surfaces checkpoint persistence failures and stops the affected workflow rather than continuing after a recovery snapshot could not be written.
- `docmergeforge project-sync` now loads its project through `load_project_snapshot(...)` and passes the revision into apply.
- Synchronization now performs an exact revision check before backup/write preparation, retains its semantic project comparison as a second defense, and performs another expected-revision check immediately before final atomic project replacement.
- `docmergeforge project-create` now converts handled project-save `OSError`/`ValueError` failures into structured JSON with `created=false`, the project path, an error message, and exit code `2`.
- `docs/project-sync.md`, `docs/project-files.md`, `docs/source-code-reference.md`, and `docs/test-suite-reference.md` now describe the exact revision contract, desktop behavior, CLI behavior, tests, and the limit that optimistic revision checks are not universal cross-process locking.
- `PROJECT_STATE.md` was first corrected to remove an already-completed discovery-routing task: `MergeApplicationService.discover()` already uses `discover_project_sources()` and `tests/unit/test_service_discovery_safety.py` already protects the shared nested-output exclusion behavior.

### Fixed / Hardened
- Closed the stale desktop overwrite window where **Resume Project** could load a project, wait for the user to edit/reorder it, and then silently replace a project file that changed on disk during that interaction.
- Strengthened project synchronization from semantic stale-state comparison alone to exact byte-revision checking. An external JSON reformat that remains semantically equivalent is still detected as a changed project snapshot and requires a fresh preview before apply.
- Kept the semantic synchronization comparison in addition to exact revisions so callers without an expected revision still retain the earlier fail-closed project-state check.
- Ensured a late guarded-save failure restores the caller's original in-memory `selected_files`; any backup already created before that late failure remains available for review/recovery.
- Prevented project files from being written through symbolic-link destinations by the generic project persistence function, not only by the synchronization wrapper.
- Prevented new desktop persistence failures introduced by stricter save rules from surfacing as uncaught UI callback exceptions.
- Prevented CLI project creation from reporting success or crashing with an unhandled save exception when the project file cannot be safely persisted.

### Concurrency boundary
- The new project revision mechanism is an **optimistic stale-write guard**, not a cooperative file lock or transactional multi-writer database protocol.
- A normal guarded workflow detects changes that occur after its captured snapshot and before its revision checks, including byte-only changes.
- An arbitrary external writer that changes the file in the small interval after the final revision check and before atomic replacement is not participating in a coordinated lock protocol and can still race that replacement.
- If true simultaneous multi-writer project editing becomes an intended supported feature, it should be designed as a separate coordinated locking/revision protocol rather than represented as already solved by this optimistic guard.

### Verification Status
- Latest implementation/documentation checkpoint immediately before this development-record update: `966f9ff0df844ba41c94c07601afe6ad9e916313`.
- Commit diffs inspected during this pass confirmed the persistence and desktop changes were focused on the intended project-store, synchronization, CLI, UI, test, and documentation surfaces rather than broad unrelated rewrites.
- `pyproject.toml` still declares version `0.1.0`, Python `>=3.12`, Ruff rules `E/F/I/B/UP/SIM/C4`, Black line length 100, and strict mypy for the `docmergeforge` package.
- Focused regression test source was added for the new behaviors, but committed tests are implementation evidence only until execution is observed.
- No fresh current-head Ruff, Black, strict mypy, documentation-link, repository-reference, pytest/coverage, Quality, Regression, Build Smoke, or Security/CodeQL pass is claimed in this section without an actual reviewed run.
- External-office production flags are not changed by this work, and the repository remains pre-stable at `0.1.0`.

### Remaining Project-Persistence / Synchronization Work
- Observe and review a current-head Quality run; fix any lint, formatting, typing, test, documentation-link, or repository-reference failure without weakening maintained rules.
- If true collaborative/multi-writer project editing is intended, design a coordinated lock/revision protocol with explicit ownership, timeout/recovery, filesystem semantics, and tests. Do not relabel the optimistic revision guard as universal locking.
- Evaluate whether the desktop project/order UI should expose the same explicit synchronization preview/apply/second-removal-approval model already available in the CLI.
- Keep project persistence, synchronization, source-code, and test-suite documentation synchronized whenever this boundary changes.

### Remaining Release-Gate Work
- Execute and review the maintained supervised LibreOffice UNO multi-document and process-cleanup workflows, then expand representative real-world fidelity evidence for sections, page styles, headers/footers, numbering, advanced OOXML, fonts, and interoperability behavior.
- Execute and review the controlled Microsoft Word native normal-merge and real timeout-cleanup workflow on the dedicated Windows/Word environment; then run representative private corpora and exact-version human rendering/repair-prompt acceptance.
- Execute and record a genuinely measured multi-gigabyte stress run.
- Complete human keyboard-only, screen-reader, high-contrast, display-scaling, reduced-motion, and localization-readiness acceptance.
- Complete representative clean-machine interactive packaged-app acceptance, platform-specific distribution polish, Windows production signing, macOS signing/notarization/stapling, final post-signing hashes, and signature verification.
- Perform additional physical power-loss, storage-device disconnect, and network/multi-host filesystem acceptance only where those semantics are intended to be claimed.
- Enable appropriate GitHub branch protection/rulesets and required status checks through repository administration if enforced review/CI policy on `main` is desired.
- Do not set LibreOffice or Word to `production_ready=true`, and do not claim `v1.0.0`, until the corresponding full application/release acceptance matrix is actually verified.

## 2026-08-19 — Repository-wide documentation mapping and coverage enforcement

### Added
- Added `docs/repository-reference.md` as a literal repository-wide inventory documenting every tracked root file, GitHub metadata/workflow, branding asset, documentation page, script, runtime module, helper, integration test, regression test, and unit test.
- Added `docs/source-code-reference.md` with package-by-package and module-by-module runtime responsibilities, architectural dependency direction, safety boundaries, and maintenance expectations.
- Added `docs/test-suite-reference.md` with the complete test-file map, evidence-layer distinctions, behavior ownership, test-placement guidance, and the difference between committed tests and observed passing evidence.
- Added `docs/automation-reference.md` covering every maintained script and GitHub Actions workflow, including normal operating environment, evidence scope, and production-readiness boundaries.
- Added `docs/configuration-reference.md` covering `pyproject.toml`, formatting/type/test configuration, Git/GitHub metadata, governance/community files, Dependabot, development records, and branding assets.
- Added `docs/documentation-catalog.md` mapping every maintained documentation file by audience and task, plus a task-oriented lookup table for users, developers, operators, and release maintainers.
- Added `scripts/check_repository_reference.py`, which reads the actual Git-tracked path set with `git ls-files` and fails when a path is not explicitly backticked in `docs/repository-reference.md`.
- Added `tests/unit/test_repository_reference.py` covering exact-path matching, deterministic missing-path reporting, successful command behavior, missing-path failure behavior, and unreadable-reference handling.

### Changed
- The primary Quality matrix now runs `python scripts/check_repository_reference.py` after local Markdown link validation, turning repository-file documentation completeness into an enforced CI contract instead of a one-time manual inventory.
- `.pre-commit-config.yaml` now runs the repository-reference checker as an `always_run` local hook, so source/config/test/workflow/asset additions, renames, and deletions can be caught before CI even when no Markdown file itself is staged.
- `docs/testing-and-ci.md` now lists the repository-reference checker in local quality commands, unit-test coverage, Quality workflow behavior, a dedicated documentation-coverage section, and the stable-release CI evidence matrix.
- `docs/configuration-reference.md` now documents the exact local documentation-integrity hooks, why the repository-reference hook uses `always_run: true`, and why local execution is not remote CI evidence.
- Root `README.md` now links the complete documentation catalog plus source, test, automation, configuration, and every-file references, and includes the repository-reference checker in the public quality command set.
- `docs/README.md` now exposes a dedicated Repository Internals section linking the documentation catalog, complete file reference, source reference, test reference, automation reference, and configuration/governance reference.
- `CONTRIBUTING.md` now requires both documentation-link validation and repository-reference coverage locally, directs contributors to the new internals references, and requires path additions/renames/deletions to update the complete repository inventory.
- `.github/PULL_REQUEST_TEMPLATE.md` now asks contributors/reviewers to confirm repository-reference coverage when tracked paths change.
- `docs/development.md` now documents the repository documentation-integrity model, complete internals references, local coverage commands, and a definition-of-done item for repository-reference coverage.
- `PROJECT_STATE.md` now carries the repository-documentation checkpoint and remaining evidence boundaries for future continuation sessions.

### Documentation coverage contract
- Coverage is based on Git-tracked files rather than filesystem traversal, so generated caches, local virtual environments, build outputs, private corpora, and other untracked local state are intentionally excluded.
- A path is considered explicitly cataloged only when the exact repository-relative path appears in backticks in `docs/repository-reference.md`; vague directory-level prose is not enough to satisfy the automated guard.
- The guard checks path coverage, not semantic prose quality. Reviewers remain responsible for ensuring the description of each tracked file is accurate and that behavior belongs in the correct canonical guide.
- New files are expected to update the inventory in the same focused change, preventing gradual documentation drift as the codebase grows.
- The same contract is now visible in contributor guidance, PR review, local pre-commit, direct developer commands, and the remote Quality workflow.

### Verification Status
- Latest implementation/documentation checkpoint immediately before this final development-record update: `ee8b356e3c445b42614ba900d3fc9956ee0e1e1b`.
- The earlier recursive `main` tree inspection confirmed the newly added repository reference, source-code reference, automation reference, test-suite reference, configuration reference, documentation catalog, coverage checker, coverage-check tests, and Quality workflow update were tracked. Later commits in this pass changed existing tracked paths only and did not introduce additional undocumented paths.
- GitHub's combined-status endpoint returned no status checks for `ee8b356e3c445b42614ba900d3fc9956ee0e1e1b`. The available commit-workflow helper is scoped to pull-request-triggered runs and therefore does not establish the state of a push-triggered Quality run on `main`.
- A direct local `git clone` attempt from the execution sandbox could not resolve `github.com`; that environment limitation is not represented as a repository test failure or pass.
- No fresh Ruff, Black, strict mypy, documentation-link, repository-reference, pytest, Quality, Regression, Build Smoke, or Security/CodeQL pass is claimed from this documentation pass until an actual current-head run is visible and reviewed.
- The added test source, pre-commit hook, and CI command demonstrate intended enforcement but are not represented as passing execution evidence by themselves.
- External-office production flags remain unchanged: `libreoffice.production_ready=false` and `word.production_ready=false`.
- The repository remains pre-stable at `0.1.0`; documentation completeness does not by itself establish `v1.0.0`, signing, notarization, native-office fidelity, accessibility certification, or clean-machine production readiness.

### Remaining Documentation / Maintenance Work
- Review the next visible current-head Quality run and fix any formatter, lint, test, link, or repository-reference failure without weakening the maintained rules.
- Keep `docs/repository-reference.md`, `docs/documentation-catalog.md`, and the appropriate subsystem reference synchronized whenever paths or responsibilities change.
- Update `CHANGELOG.md` and other release-facing summaries when the repository reaches the next externally meaningful release checkpoint; do not invent a release solely for documentation expansion.
- Continue to record real acceptance evidence separately from implementation descriptions so documentation never turns configured automation into claimed observed results.

### Remaining Release-Gate Work
- Execute and review the maintained supervised LibreOffice UNO multi-document and process-cleanup workflows, then expand representative real-world fidelity evidence for sections, page styles, headers/footers, numbering, advanced OOXML, fonts, and interoperability behavior.
- Execute and review the controlled Microsoft Word native normal-merge and real timeout-cleanup workflow on the dedicated Windows/Word environment; then run representative private corpora and exact-version human rendering/repair-prompt acceptance.
- Execute and record a genuinely measured multi-gigabyte stress run.
- Complete human keyboard-only, screen-reader, high-contrast, display-scaling, reduced-motion, and localization-readiness acceptance.
- Complete representative clean-machine interactive packaged-app acceptance, platform-specific distribution polish, Windows production signing, macOS signing/notarization/stapling, final post-signing hashes, and signature verification.
- Perform additional physical power-loss, storage-device disconnect, and network/multi-host filesystem acceptance only where those semantics are intended to be claimed.
- Enable appropriate GitHub branch protection/rulesets and required status checks through repository administration if enforced review/CI policy on `main` is desired.
- Do not set LibreOffice or Word to `production_ready=true`, and do not claim `v1.0.0`, until the corresponding full application/release acceptance matrix is actually verified.

## 2026-08-19 — Guarded project synchronization and actionable selection maintenance

### Added
- Added `src/docmergeforge/project/discovery.py` so project synchronization can inspect the current raw source tree without first applying persisted `selected_files`, while still excluding a strictly nested output subtree.
- Added `src/docmergeforge/project/sync.py` with a typed `ProjectSyncPlan` that reports `current`, `proposed`, `added`, `removed`, and `reordered` selection evidence.
- Added deterministic automatic synchronization ordering across detected part number, document kind, natural filename, and normalized full path.
- Added `docmergeforge project-sync --project FILE.json` as a preview-only project-maintenance command.
- Added explicit `--apply` mutation approval and a separate `--allow-removals` approval whenever synchronization would remove an existing selected path.
- Added versioned project backups before changed synchronization writes. Existing `.bak` files are preserved with `_v2`, `_v3`, and later version names instead of being replaced.
- Added `PROJECT_STATE.md` as a compact durable continuation checkpoint for future repository-development sessions.
- Added `docs/project-sync.md` as the dedicated synchronization safety/operator guide.
- Added unit/CLI regression coverage for synchronization eligibility/order/diffs, nested-output exclusion, backup creation/versioning, no-op behavior, stale-plan rejection, symlink refusal, preview/apply semantics, removal approval, approved removals, and structured write failures.

### Changed
- The CLI now exposes a reviewable path from current project sources to an explicit deterministic `selected_files` proposal instead of leaving audit/compare findings with no maintained project-selection refresh workflow.
- Project synchronization considers only numbered PDF/DOCX files inside the project's configured expected range. Unnumbered/out-of-range explicit selections are intentionally visible as proposed removals rather than silently retained or silently dropped.
- `--apply` now fails closed with exit code `2` when `removed` is non-empty unless `--allow-removals` is supplied after review.
- Synchronization apply rejects project files addressed through symbolic links and refuses a plan whose in-memory selected-file baseline changed after planning.
- Project-sync backup/write `OSError`s and maintained safety `ValueError`s are surfaced as structured JSON failures instead of unhandled write-path tracebacks.
- `docs/project-files.md`, `docs/cli-reference.md`, `docs/audit-and-compare.md`, `docs/development-phases.md`, root `README.md`, and `docs/README.md` now describe/link the guarded synchronization workflow and its privacy/approval boundaries.

### Fixed / Hardened
- Closed the project-workflow gap where current source membership/order could be reviewed but there was no maintained, explicit, backup-backed CLI mechanism to apply a refreshed selection to a reusable project.
- Prevented a single apply flag from dropping intentionally selected prefaces, appendices, covers, or other manual exceptions that fall outside the automatic numbered/in-range proposal.
- Prevented an existing synchronization backup from being overwritten by later applies.
- Prevented unchanged synchronization proposals from creating unnecessary backup/project writes.
- Added a stale in-memory selection guard so a plan cannot be applied after its selection baseline changes during the same process.
- Preserved the existing project file through the maintained atomic text-save path and restore the caller's in-memory selection if final project saving fails.

### Verification Status
- Implementation/documentation checkpoint immediately before this development-record update: `2be1d665065ecf53b83a453d571fd8111776967c`.
- The repository commit chain confirms the synchronization implementation, tests, safety hardening, documentation, and project-state commits are present on `main`.
- Focused regression tests were added for every synchronization behavior listed above, but committed test source is not represented as a passing run by itself.
- The available connector did not expose a current push-triggered Quality run through its commit-run wrapper, and combined commit status did not provide a passing check set at the inspected synchronization checkpoints. Therefore no current-head Ruff, Black, strict mypy, documentation-link, pytest, Quality, Regression, Build Smoke, or Security/CodeQL pass is claimed here.
- External-office production flags remain unchanged: `libreoffice.production_ready=false` and `word.production_ready=false`.
- The repository remains pre-stable at `0.1.0`; this pass does not claim signed/notarized release artifacts or `v1.0.0` readiness.

### Remaining Project-Synchronization Work
- Obtain and review current-head source CI; fix any synchronization-specific lint/type/test/link failures without weakening repository rules.
- Shared application discovery already routes through `discover_project_sources()` and is protected by `tests/unit/test_service_discovery_safety.py`; do not reimplement that completed item unless the discovery contract changes.
- Exact project revision guards are now implemented for synchronization and desktop resume. If stronger simultaneous multi-writer guarantees become a supported requirement, design a coordinated lock/revision protocol rather than duplicating the completed optimistic guard.
- Evaluate whether desktop project/order workflows should expose the same preview/apply/second-removal-approval model.

### Remaining Release-Gate Work
- Execute and review the maintained supervised LibreOffice UNO multi-document and process-cleanup workflows, then expand representative real-world fidelity evidence for sections, page styles, headers/footers, numbering, advanced OOXML, fonts, and interoperability behavior.
- Execute and review the controlled Microsoft Word native normal-merge and real timeout-cleanup workflow on the dedicated Windows/Word environment; then run representative private corpora and exact-version human rendering/repair-prompt acceptance.
- Execute and record a genuinely measured multi-gigabyte stress run.
- Complete human keyboard-only, screen-reader, high-contrast, display-scaling, reduced-motion, and localization-readiness acceptance.
- Complete representative clean-machine interactive packaged-app acceptance, platform-specific distribution polish, Windows production signing, macOS signing/notarization/stapling, final post-signing hashes, and signature verification.
- Perform additional physical power-loss, storage-device disconnect, and network/multi-host filesystem acceptance only where those semantics are intended to be claimed.
- Enable appropriate GitHub branch protection/rulesets and required status checks through repository administration if enforced review/CI policy on `main` is desired.
- Do not set LibreOffice or Word to `production_ready=true`, and do not claim `v1.0.0`, until the corresponding full application/release acceptance matrix is actually verified.

## 2026-08-19 — Durability, transaction recovery, path identity, naming, and range hardening

### Added
- Added `src/docmergeforge/core/part_range.py` as the shared expected-part-range contract used by validation, project persistence, project loading, and CLI parsing.
- Added a six-digit maximum part number of **999,999**, matching the maintained filename detector, plus a **10,000-part maximum span** to prevent malformed projects or CLI arguments from forcing unbounded missing-part allocations/diagnostics.
- Added regression coverage for case-distinct POSIX project selections, duplicate/aliased selections, binary-output `fsync` failures, recovery checkpoint persistence ordering, durable output-folder probing, strict transaction journal parsing, transaction symlink rejection, output-lock symlink rejection, Windows device-name filename prefixes, project/CLI range bounds, project-save range guards, and the filename-detector upper boundary.
- Added explicit tests proving malformed transaction journals fail closed for unsafe `..` child names, non-boolean JSON values, invalid phase types, non-hex SHA-256 values, output-folder final targets, duplicate final targets, and symlinked recovery artifacts.

### Changed
- Explicit project selection now compares resolved paths using platform-aware `os.path.normcase(...)` instead of unconditional case folding. Case-distinct POSIX source files remain individually selectable while aliases of the same resolved path are still detected as duplicates.
- Binary `atomic_output(...)` now flushes the completed temporary artifact with `fsync` before `os.replace(...)` promotes it to the final name.
- Batch `OutputTransaction` promotion now performs the same completed-file flush before writing the promotion journal and mutating final paths.
- Output-destination writeability probing now creates a real probe file, writes one byte, flushes it, requests `fsync`, and removes the probe instead of treating empty-file creation alone as sufficient evidence.
- Recovery checkpoints now persist a snapshot first and update the live project's `last_successful_checkpoint` only after the save succeeds, preventing an in-memory checkpoint from claiming persistence that failed.
- Project loading, project saving, direct validation, and CLI `--parts` parsing now enforce the same bounded range rules.
- Generated output basenames now protect Windows reserved device names even when followed by extensions/suffixes, including forms such as `CON.txt`, `COM1.release`, and `LPT9.final.copy`.
- `docs/recovery.md`, `docs/project-files.md`, and `docs/development-phases.md` were updated to document the new durability, path, range, naming, and fail-closed recovery boundaries without promoting unverified release claims.

### Fixed / Hardened
- Fixed explicit source selection incorrectly collapsing case-distinct POSIX paths.
- Fixed atomic binary publication and batch staging promotion not explicitly flushing completed artifact bytes before final-name replacement.
- Fixed the output-folder preflight probe succeeding after file creation without testing a flushed write.
- Fixed recovery checkpoint state being mutated before the recovery snapshot was proven to be saved.
- Hardened transaction recovery against JSON truthiness/coercion, invalid field types, unsafe child paths, output-directory self-targeting, duplicate final targets, reused staging/backup names, malformed fingerprints, symlinked journals, symlinked staging/backup children, and existing non-file recovery children.
- Hardened pending-transaction discovery so symlinked `.docmergeforge-staging-*` directories are ignored rather than treated as trusted transaction directories.
- Hardened the output-directory lock file against pre-existing symlinks and request `O_NOFOLLOW` where the platform exposes it.
- Fixed generated Windows filenames where a reserved device prefix followed by a dot previously escaped the exact-name reserved-device check.
- Fixed unbounded expected ranges that could force large validation lists/diagnostics from malformed project or CLI input.
- Fixed project persistence so an invalid expected range is rejected before a new project JSON file is written.

### Verification Status
- Implementation/documentation checkpoint immediately before this development-record update: `d9b54cff87ea2dbe4e9fc440635a9e0842a0526d`.
- The raw Git commit metadata inspected for that checkpoint records `Sanskar <sanskarin@outlook.in>` as both author and committer.
- Focused regression tests for every new hardening boundary were added to the repository, but a repository test file being present is not represented as a passing run by itself.
- No current-head Ruff, Black, strict mypy, full pytest, Quality, Regression, Build Smoke, Security/CodeQL, or documentation-link pass is fabricated here. Historical green runs remain evidence only for their exact earlier checkpoints.
- `libreoffice.production_ready=false` and `word.production_ready=false` remain unchanged. Portable OOXML remains the normal production-enabled DOCX path.
- The repository remains pre-stable at `0.1.0`; this pass does not claim signed/notarized production release artifacts or `v1.0.0` readiness.

### Remaining Release-Gate Work
- Obtain and review current-head Quality, 120-Part Regression, Build Smoke, Security/CodeQL, and documentation-link evidence after this hardening pass.
- Execute and review the maintained supervised LibreOffice UNO multi-document and process-cleanup workflows, then expand representative real-world fidelity evidence for sections, page styles, headers/footers, numbering, advanced OOXML, fonts, and interoperability behavior.
- Execute and review the controlled Microsoft Word native normal-merge and real timeout-cleanup workflow on the dedicated Windows/Word environment; then run representative private corpora and exact-version human rendering/repair-prompt acceptance.
- Execute and record a genuinely measured multi-gigabyte stress run.
- Complete human keyboard-only, screen-reader, high-contrast, display-scaling, reduced-motion, and localization-readiness acceptance.
- Complete representative clean-machine interactive packaged-app acceptance, platform-specific distribution polish, Windows production signing, macOS signing/notarization/stapling, final post-signing hashes, and signature verification.
- Perform additional physical power-loss, storage-device disconnect, and network/multi-host filesystem acceptance only where those semantics are intended to be claimed.
- Enable appropriate GitHub branch protection/rulesets and required status checks through repository administration if enforced review/CI policy on `main` is desired.
- Do not set LibreOffice or Word to `production_ready=true`, and do not claim `v1.0.0`, until the corresponding full application/release acceptance matrix is actually verified.
