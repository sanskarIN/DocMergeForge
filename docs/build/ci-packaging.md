# CI Packaging Guide

This guide documents the repository's current executable-packaging automation and how to use its artifacts safely.

## Current workflow

File:

```text
.github/workflows/package.yml
```

Workflow name:

```text
Package Desktop
```

## Triggers

The workflow currently runs on:

- manual `workflow_dispatch`;
- pushes of tags matching `v*`;
- `main` pushes when packaging-relevant files change.

The `main` path filter currently covers:

```text
.github/workflows/package.yml
pyproject.toml
scripts/build_desktop.py
src/docmergeforge/packaging/**
src/docmergeforge/ui/**
```

This keeps real package-building coverage tied to packaging/UI changes without rebuilding all three desktop artifacts for unrelated documentation-only commits.

## Build matrix

Current matrix:

| Runner | Python |
|---|---|
| `windows-latest` | 3.12 |
| `macos-latest` | 3.12 |
| `ubuntu-latest` | 3.12 |

`fail-fast: false` allows one platform to continue even if another platform fails.

## Permissions

The workflow currently uses:

```yaml
permissions:
  contents: read
```

It uploads workflow artifacts but does not publish a GitHub Release or write repository contents.

## Exact workflow stages

For each matrix platform, the workflow currently:

1. checks out the repository with `actions/checkout@v4`;
2. sets up Python with `actions/setup-python@v5`;
3. installs the Linux `libegl1` Qt runtime prerequisite on Ubuntu;
4. upgrades pip;
5. installs `pip install -e ".[build]"`;
6. runs `python scripts/build_desktop.py --check`;
7. runs `python scripts/build_desktop.py`;
8. launches the freshly packaged desktop binary with `--packaged-smoke`;
9. archives the platform output;
10. uploads the archive with `actions/upload-artifact@v4`;
11. prints a notice that the artifacts are unsigned development builds.

## Packaged smoke mode

PyInstaller uses:

```text
src/docmergeforge/ui/packaged_entry.py
```

as the packaged application entry point.

Normal users still launch the regular desktop behavior. CI supplies:

```text
--packaged-smoke
```

which initializes the packaged Qt application, configuration, logging, theme/text scaling, and `MainWindow` in offscreen mode, then exits successfully without opening first-run/recovery dialogs or entering the normal long-running event loop.

This verifies more than a successful PyInstaller build: it verifies the produced binary can actually start far enough to import and initialize the packaged desktop application.

It does **not** replace clean-machine human testing, representative PDF/DOCX merge acceptance, signing, or notarization.

## Platform smoke commands

### Windows

The workflow uses PowerShell `Start-Process -Wait -PassThru` on:

```text
dist/DocMergeForge/DocMergeForge.exe
```

and fails if the process exit code is nonzero.

### macOS

The workflow prefers:

```text
dist/DocMergeForge.app/Contents/MacOS/DocMergeForge
```

and falls back to an onedir executable path when needed.

It launches with:

```bash
QT_QPA_PLATFORM=offscreen ... --packaged-smoke
```

### Linux

The workflow launches:

```bash
QT_QPA_PLATFORM=offscreen dist/DocMergeForge/DocMergeForge --packaged-smoke
```

## Current artifact names

Windows:

```text
DocMergeForge-Windows-unsigned.zip
```

macOS:

```text
DocMergeForge-macOS-unsigned.tar.gz
```

Linux:

```text
DocMergeForge-Linux-unsigned.tar.gz
```

The uploaded artifact container names also include `unsigned`.

## Current archive commands

### Windows

```powershell
Compress-Archive -Path dist/DocMergeForge/* -DestinationPath DocMergeForge-Windows-unsigned.zip
```

### macOS

The workflow archives the native `.app` bundle when PyInstaller creates it:

```bash
tar -czf DocMergeForge-macOS-unsigned.tar.gz -C dist DocMergeForge.app
```

and falls back to the onedir layout when needed.

### Linux

```bash
tar -czf DocMergeForge-Linux-unsigned.tar.gz -C dist DocMergeForge
```

## How to run manually

From the repository Actions tab:

1. open **Package Desktop**;
2. choose **Run workflow**;
3. select the intended branch/ref;
4. run the workflow;
5. wait for all intended matrix jobs to finish;
6. inspect each job and packaged smoke step before downloading artifacts.

A manual run is a development packaging action unless release signing/acceptance is separately completed.

## Tag-triggered packaging

A `v*` tag causes the same unsigned packaging workflow to run.

Important: a tag does not automatically make an artifact production-ready. Before creating a stable release tag, follow the repository release process and complete the acceptance matrix.

## Artifact download and verification

After a successful workflow run:

1. download each platform artifact;
2. record workflow run ID and head commit SHA;
3. extract it into a clean location;
4. launch it on the matching target OS normally, not only with smoke mode;
5. perform packaged-app merge acceptance;
6. generate local SHA-256 values for the downloaded archives;
7. retain evidence with the release candidate.

## Relationship to Build Smoke

`Build Smoke` and `Package Desktop` are different.

### Build Smoke

Build Smoke validates, on Windows/macOS/Linux:

- Python/source compilation;
- CLI availability;
- accessibility metadata smoke;
- packaging configuration preflight.

It does not invoke PyInstaller.

### Package Desktop

Package Desktop:

- invokes PyInstaller;
- launches the packaged executable in deterministic smoke mode;
- archives and uploads the package.

This closes the earlier gap where CI proved packaging configuration but never launched the binary it had just built.

It still does not prove production distribution acceptance.

## Relationship to Quality, Regression, and Security

Before treating Package Desktop output as a release candidate, verify the same implementation checkpoint has appropriate green results from:

- Quality;
- 120-Part Regression;
- Build Smoke;
- Security/CodeQL.

Package Desktop should not be used to bypass a failed quality gate.

## Why artifacts are labeled unsigned

The current CI workflow has no signing credentials or signing steps. The explicit name prevents accidental misrepresentation.

Do not remove `unsigned` from artifact naming until:

- a secure signing workflow exists;
- credentials are provisioned outside source control;
- signing is performed;
- signatures are verified in CI or acceptance;
- macOS notarization is performed/verified when claimed.

## Signing secrets in GitHub Actions

If production signing is later implemented:

- use GitHub Actions secrets/environments or an external managed signing service;
- use least-privilege credentials;
- protect release environments with approvals when appropriate;
- never echo secrets;
- never store private keys/passwords directly in workflow YAML;
- ensure pull-request code from untrusted forks cannot access signing secrets;
- verify signatures after signing;
- separate unsigned build artifacts from final signed artifacts.

## Suggested future release workflow separation

A robust future structure can separate:

1. **Build** — create unsigned native artifacts.
2. **Verify** — launch/test/hash unsigned artifacts.
3. **Sign** — sign only verified immutable inputs.
4. **Notarize** — macOS notarization where required.
5. **Re-verify** — verify final signed/notarized artifacts.
6. **Publish** — attach final hashes/artifacts to a release.

This is a recommended architecture, not a claim that these stages already exist.

## Artifact retention

Workflow artifacts are not a permanent release channel by themselves. For long-term release distribution, publish validated final artifacts through an intentional release mechanism and retain hashes/evidence.

## Failure triage

If one matrix platform fails:

1. inspect that platform job logs;
2. identify whether failure occurred during install, preflight, PyInstaller build, packaged launch, archive, or upload;
3. reproduce on a native local machine when possible;
4. fix shared packaging configuration where appropriate;
5. rerun the complete affected platform build;
6. do not publish a partial multi-platform release while claiming all platforms passed.

## CI packaging acceptance record

Record at minimum:

```text
Commit/tag:
Workflow run ID:
Windows build: pass/fail
Windows packaged smoke: pass/fail
macOS build: pass/fail
macOS packaged smoke: pass/fail
Linux build: pass/fail
Linux packaged smoke: pass/fail
Windows artifact:
macOS artifact:
Linux artifact:
Artifact hashes:
Clean-machine verification:
Signing status:
Notarization status:
Known deviations:
```

## Current limitations

The current workflow does not:

- sign Windows executables;
- notarize macOS artifacts;
- create MSI/MSIX/DMG/PKG/AppImage/DEB/RPM;
- generate/publish a release checksum manifest;
- create a GitHub Release;
- prove clean-machine interactive use;
- prove representative manuscript fidelity from the packaged application.

Those steps remain documented release gates, not hidden assumptions.
