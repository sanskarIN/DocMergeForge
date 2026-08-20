# DocMergeForge Project State

This file is a compact continuation checkpoint for future development sessions. Detailed change history belongs in [`what_changed.md`](what_changed.md) and historical records under [`docs/history/`](docs/history/).

## Current checkpoint

- Repository: `sanskarIN/DocMergeForge`
- Branch: `main`
- Version declared in `pyproject.toml`: `0.1.0`
- Checkpoint immediately before this state-file commit: `e1e142a55535d23b6b68f4a55dd65cefb79046bc`
- Development status: pre-stable; do not claim `v1.0.0` or production certification from source/documentation changes alone.

## Latest completed continuation: cross-platform browser security and documentation synchronization

The repository already had the cross-platform delivery expansion before this continuation: native Windows/macOS/Linux desktop + CLI support and responsive browser-hosted access for Android, iOS/iPadOS, ChromeOS, desktop browsers, and other modern browser platforms. The latest continuation hardened that web boundary, expanded regression coverage, corrected stale public/internal documentation, and synchronized the durable continuation record.

Implementation/hardening:

- `src/docmergeforge/web/app.py`
  - LAN access tokens are entered through a masked browser field or bootstrapped from a `#token=...` URL fragment;
  - the old `?token=...` query-token bootstrap is removed so the application no longer deliberately places access tokens in the HTTP request target;
  - fragment tokens move into tab-scoped `sessionStorage` and the fragment is removed from the visible address;
  - merge requests send the token in `X-DocMergeForge-Token`;
  - upload handles close through a `finally` path on success and upload validation/size failures;
  - unexpected merge-engine exceptions are logged on the host and returned to the browser as a generic `422` response rather than reflecting raw host details;
  - the browser shell applies content-security, anti-framing, no-referrer, no-sniff, and permissions headers.
- `src/docmergeforge/web/main.py`
  - still defaults to loopback and refuses non-loopback binds without token protection;
  - token-enabled startup now directs operators to the browser token field or `#token=...` fragment and explicitly warns against `?token=...`.

Regression coverage:

- `tests/integration/test_web_app.py`
  - secure fragment/bootstrap shell behavior;
  - browser security headers;
  - PDF and DOCX web merge/download paths;
  - access-token enforcement;
  - generic unexpected-error privacy;
  - upload-size fail-closed behavior;
  - mixed-format rejection;
  - filename/path safety;
  - health/platform endpoints.
- `tests/unit/test_web_main.py`
  - loopback-host detection and safe server parser defaults.
- `tests/unit/test_platforms.py`
  - maintained platform capability/support matrix.

Canonical/public documentation synchronized in this continuation:

- `README.md`;
- `docs/platform-support.md`;
- `docs/security.md`;
- `docs/privacy.md`;
- `docs/installation.md`;
- `docs/architecture.md`;
- `docs/source-code-reference.md`;
- `docs/test-suite-reference.md`;
- `docs/testing-and-ci.md`;
- `docs/known-limitations.md`;
- `what_changed.md`;
- `PROJECT_STATE.md`.

### Cross-platform support boundary

Current support should be described precisely:

- Windows 10/11: native desktop GUI, CLI, and responsive web client;
- macOS: native desktop GUI, CLI, and responsive web client;
- Linux: native desktop GUI, CLI, and responsive web client;
- Android: responsive browser client connected to a DocMergeForge Python host; no native APK/AAB claim;
- iPhone/iPad: responsive browser client connected to a DocMergeForge Python host; no native IPA claim;
- ChromeOS/other modern browser platforms: responsive browser client connected to a DocMergeForge Python host.

The browser shell/PWA is not the document-processing engine. PDF/DOCX processing still runs on the Python host. Do not describe the current mobile/browser path as fully offline in-browser processing or as native mobile packaging.

### Browser/network security boundary

- Loopback remains the safest local-first web mode.
- Non-loopback CLI binds require a token.
- A token authenticates merge requests but does not encrypt manuscript bytes or PDF passwords in transit.
- The maintained browser flow keeps access tokens out of HTTP query parameters; use the masked browser field or a trusted one-time `#token=...` fragment.
- Use trusted LAN transport for plain HTTP; use HTTPS plus an appropriately hardened reverse proxy/authentication/request-limit layer when traffic crosses an untrusted network.
- Do not expose the built-in Uvicorn server directly to the public Internet.
- `--max-upload-mib` limits uploaded file bytes copied into DocMergeForge's request workspace; it is not a complete edge request-body/connection/resource firewall. Exposed reverse-proxy deployments need independent body-size, timeout, concurrency, TLS, and authentication controls.

### Browser/privacy boundary

- Responsive browser use sends the selected PDF/DOCX bytes from the browser device to the chosen Python host.
- A submitted shared encrypted-PDF password crosses that same browser-to-host connection.
- The browser token is tab-session state and is not written into project JSON.
- Host access/error logs and reverse-proxy/network infrastructure can contain sensitive operational metadata and must be reviewed before sharing.
- Browser request workspaces are temporary download workspaces, not durable full-project recovery journals.

## Verified configuration facts for the latest continuation

The actual workflow files were inspected during this continuation:

- `.github/workflows/quality.yml`
  - Python 3.12 and 3.13 on Ubuntu;
  - installs `.[dev,web]`;
  - runs pre-commit config validation, Ruff, Black check, strict mypy, Markdown-link validation, repository-reference validation, and full pytest with coverage.
- `.github/workflows/build-smoke.yml`
  - Ubuntu, Windows, and macOS;
  - installs `.[build,web]`;
  - runs source compilation, `docmergeforge --help`, `docmergeforge-web --help`, accessibility smoke, and desktop packaging preflight.

These workflow definitions establish configured checks only. GitHub's combined-status surface exposed no status contexts at the inspected current-continuation checkpoints, so no fresh execution pass is claimed from those definitions.

## Previous completed feature: guarded existing-project persistence

The prior project-persistence continuation closed the main known stale-write gap around reusable project JSON files while preserving the existing atomic-save model.

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
  - **Resume Project** loads project + revision together and refuses to overwrite a project changed while the user reviews ordering;
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

### Important project concurrency boundary

The SHA-256 project revision mechanism is an **optimistic stale-write guard**, not a universal cross-process lock. It detects project changes observed between snapshot and revision checks, including byte-only JSON drift. An arbitrary external writer can still race the tiny interval after a final revision check and before atomic replacement because that external writer is not participating in a coordinated lock protocol.

If true simultaneous multi-writer project editing becomes an intended supported feature, design a separate coordinated locking/revision protocol with ownership, timeout/recovery, filesystem semantics, and tests. Do not reimplement or relabel the completed optimistic guard as universal locking.

## Previous completed maintenance: repository-wide documentation mapping

The earlier maintenance continuation completed a repository-wide documentation mapping pass and made tracked-file documentation coverage an enforced Quality rule.

Key files:

- `docs/repository-reference.md` — literal inventory of every tracked repository path;
- `docs/repository-reference-cross-platform.md` — maintained addendum for cross-platform/web additions where used by the checker/reference corpus;
- `docs/source-code-reference.md` — module-by-module runtime responsibility map, now including platform/web modules;
- `docs/test-suite-reference.md` — complete maintained test-file map, now including web/platform tests;
- `docs/automation-reference.md` — scripts and GitHub Actions workflow reference;
- `docs/configuration-reference.md` — project/tooling/governance configuration reference;
- `docs/documentation-catalog.md` — documentation map by audience/task;
- `scripts/check_repository_reference.py` — tracked-path documentation checker;
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

For the latest continuation:

- cross-platform browser hardening, regression source, and synchronized canonical/public documentation are committed on `main`;
- only existing tracked paths were changed in this latest continuation, so no new path was introduced that would require a new repository-reference inventory entry;
- `pyproject.toml` remains pre-stable at version `0.1.0` and retains Ruff, Black, strict mypy, pytest/coverage, documentation-link, repository-reference, and responsive-web dependency configuration;
- committed tests and inspected workflow definitions are implementation/configuration evidence, not execution evidence.

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
- Security/CodeQL;
- representative Android/iOS/iPadOS/ChromeOS/manual browser acceptance.

External-office, stress, accessibility, clean-machine packaging, signing/notarization, and other release gates remain independent from source completeness.

## Recommended next development work

1. Observe a current-head Quality run and fix any lint/format/type/test/link/reference failure without weakening repository rules.
2. Perform representative manual browser/device acceptance for the current responsive client before broadening compatibility claims beyond the automated host/API coverage.
3. If Internet/untrusted-network hosting is intentionally supported later, define and acceptance-test the HTTPS reverse-proxy/authentication/body-limit/timeout/concurrency/host-hardening deployment profile instead of promoting the built-in server as that profile.
4. Keep `docs/repository-reference.md`, its maintained addenda, `docs/documentation-catalog.md`, source/test references, README, architecture, privacy/security/platform/install/limitations/CI docs, and `what_changed.md` synchronized with future path/responsibility/security changes.
5. Evaluate whether the desktop project/order UI should expose the CLI's synchronization preview/apply/second-removal-approval model.
6. If simultaneous multi-writer project editing is explicitly required, design a coordinated lock/revision protocol; otherwise retain the current simpler optimistic revision model.
7. Continue independent release-gate work for native-office fidelity, measured multi-gigabyte stress, human accessibility, clean-machine packaged applications, Windows signing, and macOS signing/notarization.

## Continuation rule

Future sessions should read this file plus `what_changed.md`, inspect the current `main` head, and use the repository/source/test/automation/configuration/documentation references before changing a subsystem. Continue from repository evidence instead of re-implementing already committed features, and do not turn configured checks into claimed passing evidence without an observed run.
