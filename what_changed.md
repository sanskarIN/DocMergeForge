# What Changed

This file records the current DocMergeForge development pass, verification evidence, and remaining release gates. Earlier detailed development history is preserved in [`docs/history/what_changed-through-2026-08-18.md`](docs/history/what_changed-through-2026-08-18.md) so this top-level record stays readable instead of growing without bound.

An item is not treated as finished merely because code was pushed. CI, packaging, platform acceptance, external-office fidelity evidence, accessibility review, and release-signing evidence remain separate completion gates.

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
- `docs/README.md` now exposes a dedicated Repository Internals section linking the documentation catalog, complete file reference, source reference, test reference, automation reference, and configuration/governance reference.
- `CONTRIBUTING.md` now requires both documentation-link validation and repository-reference coverage locally, directs contributors to the new internals references, and requires path additions/renames/deletions to update the complete repository inventory.
- `.github/PULL_REQUEST_TEMPLATE.md` now asks contributors/reviewers to confirm repository-reference coverage when tracked paths change.
- `docs/development.md` now documents the repository documentation-integrity model, complete internals references, local coverage commands, and a definition-of-done item for repository-reference coverage.

### Documentation coverage contract
- Coverage is based on Git-tracked files rather than filesystem traversal, so generated caches, local virtual environments, build outputs, private corpora, and other untracked local state are intentionally excluded.
- A path is considered explicitly cataloged only when the exact repository-relative path appears in backticks in `docs/repository-reference.md`; vague directory-level prose is not enough to satisfy the automated guard.
- The guard checks path coverage, not semantic prose quality. Reviewers remain responsible for ensuring the description of each tracked file is accurate and that behavior belongs in the correct canonical guide.
- New files are expected to update the inventory in the same focused change, preventing gradual documentation drift as the codebase grows.

### Verification Status
- Implementation/documentation checkpoint immediately before this development-record update: `e1eace6420afdbee1ef698d9d5d5e7662b38722c`.
- The recursive `main` tree inspected at that checkpoint contained the newly added repository reference, source-code reference, automation reference, test-suite reference, configuration reference, documentation catalog, coverage checker, coverage-check tests, and Quality workflow update.
- The connector's combined-status endpoint returned no status checks for that inspected checkpoint. The available commit-workflow helper is scoped to pull-request-triggered runs and therefore does not establish the state of a push-triggered Quality run on `main`.
- No fresh Ruff, Black, strict mypy, documentation-link, repository-reference, pytest, Quality, Regression, Build Smoke, or Security/CodeQL pass is claimed from this documentation pass until an actual current-head run is visible and reviewed.
- The added test source and CI command demonstrate intended enforcement but are not represented as passing execution evidence by themselves.
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
- Consider safely routing `MergeApplicationService.discover()` through the new raw discovery helper to remove duplicated nested-output exclusion logic after regression evidence is available.
- Consider a project-file revision/concurrency guard if synchronized project JSON is expected to support multi-writer editing; normal project persistence is still documented as last-writer-wins rather than collaborative locking.
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
