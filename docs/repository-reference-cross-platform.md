# Cross-Platform Repository Reference Addendum

This addendum extends the main [Complete Repository File Reference](repository-reference.md) for the cross-platform/browser implementation and later cross-platform desktop follow-up work. The repository-reference coverage check reads both documents so newly introduced platform files remain explicitly documented without replacing the detailed historical inventory in the main reference.

## Cross-platform runtime

- `src/docmergeforge/platforms.py` — typed maintained support matrix and privacy-safe runtime identification shared by diagnostics and the web API.
- `src/docmergeforge/web/__init__.py` — package marker for the responsive browser/PWA surface.
- `src/docmergeforge/web/app.py` — FastAPI application, responsive browser shell, PWA manifest/service worker, upload isolation, cross-platform filename sanitization, access-token enforcement, platform/status endpoints, and PDF/DOCX merge/download orchestration through the existing engines.
- `src/docmergeforge/web/main.py` — `docmergeforge-web` server entry point, loopback-safe defaults, non-loopback token requirement, upload-limit configuration, LAN connection guidance, and Uvicorn startup.

## Cross-platform desktop follow-up

- `src/docmergeforge/ui/project_sync_dialog.py` — accessible desktop preview surface for guarded reusable-project source synchronization. It presents current/proposed/add/remove/reorder/duplicate/missing evidence and exposes apply only when the existing synchronization plan is both changed and unambiguous; removal approval remains a separate workflow step.
- `src/docmergeforge/ui/desktop_entry.py` — desktop startup wrapper and `ProjectSyncMainWindow` extension that adds the synchronization action without duplicating synchronization logic. It loads project + exact revision together, builds the shared preview plan, requires separate approval for removals, applies through `apply_project_sync(...)`, and preserves the existing desktop startup path.

## Cross-platform tests

- `tests/unit/test_platforms.py` — verifies the maintained platform matrix and privacy-safe runtime payload contract.
- `tests/unit/test_web_main.py` — verifies loopback recognition and safe web-server defaults.
- `tests/integration/test_web_app.py` — exercises browser API health/platform responses, PDF merging, DOCX merging, token protection, POSIX/Windows-style filename safety, and mixed-format rejection.

## Cross-platform documentation

- `docs/platform-support.md` — authoritative delivery-mode support matrix for Windows, macOS, Linux, Android, iOS/iPadOS, ChromeOS, and modern browsers, including LAN security and native-mobile claim boundaries.
- `docs/repository-reference-cross-platform.md` — this addendum and explicit inventory of files introduced by the cross-platform implementation and related follow-up work.

## Existing files changed by this implementation

These paths were already documented in the main repository reference and remain covered there:

- `pyproject.toml` — declares the optional web runtime, HTTPX development dependency, web classifier/keywords, and `docmergeforge-web` console entry point.
- `.github/workflows/quality.yml` — installs `.[dev,web]` so browser code participates in lint, type checking, documentation checks, and the full test suite on Python 3.12 and 3.13.
- `.github/workflows/build-smoke.yml` — installs the web runtime and invokes `docmergeforge-web --help` on Ubuntu, Windows, and macOS in addition to the existing desktop build checks.
- `scripts/check_repository_reference.py` — treats the main reference plus this cross-platform addendum as one coverage corpus.
- `tests/unit/test_repository_reference.py` — verifies both explicit single-reference behavior and the maintained default multi-reference corpus.
- `docs/README.md` — exposes the platform guide, browser execution surface, and reference addendum from the documentation portal.
- `docs/installation.md` — covers optional web installation, phone/tablet LAN access, token requirements, storage, encrypted PDFs, and native-mobile packaging boundaries.

## Documentation synchronization boundary

The platform guide and this addendum remain the authoritative documentation for newly introduced cross-platform paths. Existing broader release/history documents such as `README.md`, `CHANGELOG.md`, `PROJECT_STATE.md`, and `what_changed.md` are synchronized in focused documentation commits rather than being treated as automatically current merely because a path is named here.

The addendum does not redefine existing module responsibilities. It supplies explicit coverage for paths that did not exist when the main repository reference was last expanded and records existing files modified by cross-platform implementation and follow-up work.
