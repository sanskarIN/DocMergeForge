# Cross-Platform Repository Reference Addendum

This addendum extends the main [Complete Repository File Reference](repository-reference.md) for the cross-platform/browser implementation. The repository-reference coverage check reads both documents so newly introduced platform files remain explicitly documented without replacing the detailed historical inventory in the main reference.

## Cross-platform runtime

- `src/docmergeforge/platforms.py` — typed maintained support matrix and privacy-safe runtime identification shared by diagnostics and the web API.
- `src/docmergeforge/web/__init__.py` — package marker for the responsive browser/PWA surface.
- `src/docmergeforge/web/app.py` — FastAPI application, responsive browser shell, PWA manifest/service worker, upload isolation, filename sanitization, access-token enforcement, platform/status endpoints, and PDF/DOCX merge/download orchestration through the existing engines.
- `src/docmergeforge/web/main.py` — `docmergeforge-web` server entry point, loopback-safe defaults, non-loopback token requirement, upload-limit configuration, and Uvicorn startup.

## Cross-platform tests

- `tests/unit/test_platforms.py` — verifies the maintained platform matrix and privacy-safe runtime payload contract.
- `tests/unit/test_web_main.py` — verifies loopback recognition and safe web-server defaults.
- `tests/integration/test_web_app.py` — exercises browser API health/platform responses, PDF merging, DOCX merging, token protection, filename safety, and mixed-format rejection.

## Cross-platform documentation

- `docs/platform-support.md` — authoritative delivery-mode support matrix for Windows, macOS, Linux, Android, iOS/iPadOS, ChromeOS, and modern browsers, including LAN security and native-mobile claim boundaries.
- `docs/repository-reference-cross-platform.md` — this addendum and explicit inventory of files introduced by the cross-platform implementation.

## Existing files changed by this implementation

These paths were already documented in the main repository reference and remain covered there:

- `pyproject.toml` — now declares the optional web runtime, HTTPX development dependency, web classifier/keywords, and `docmergeforge-web` console entry point.
- `.github/workflows/quality.yml` — now installs `.[dev,web]` so browser code participates in lint, type checking, and the full test suite on Python 3.12 and 3.13.
- `scripts/check_repository_reference.py` — now treats the main reference plus this cross-platform addendum as one coverage corpus.
- `docs/README.md` — documentation portal updated with platform/browser guidance.
- `README.md` — public overview updated with the cross-platform delivery matrix and web launch commands.
- `docs/installation.md` — installation guidance updated for the optional web runtime and phone/tablet access.
- `docs/testing-and-ci.md` — testing guidance updated for browser/API coverage.
- `docs/source-code-reference.md` — source reference updated for platform and web modules.
- `docs/test-suite-reference.md` — test reference updated for platform/web tests.
- `CHANGELOG.md` — records the cross-platform feature set.
- `PROJECT_STATE.md` — continuation checkpoint updated with the new execution surface and remaining native-mobile boundary.
- `what_changed.md` — current development record updated with implementation and verification details.

The addendum does not redefine existing module responsibilities. It only supplies explicit coverage for paths that did not exist when the main repository reference was last expanded.
