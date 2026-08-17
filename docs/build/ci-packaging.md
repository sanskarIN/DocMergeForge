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
9. runs a tiny mixed PDF+DOCX publication inside that packaged process;
10. archives the platform output;
11. generates a SHA-256 sidecar for the archive and verifies it where the platform tool supports direct check mode;
12. uploads the archive and checksum sidecar with `actions/upload-artifact@v4`;
13. prints a notice that the artifacts are unsigned development builds.

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

The smoke mode:

1. initializes the packaged Qt application in offscreen mode;
2. loads application settings and configures logging/theme/text scale;
3. constructs and closes `MainWindow` without entering the normal interactive event loop;
4. creates a temporary `Part 1.pdf` with `pypdf`;
5. creates a temporary `Part 1.docx` with `python-docx`;
6. runs a one-part mixed project through `MergeApplicationService`;
7. exercises PDF front matter/page numbering so ReportLab packaging is covered;
8. exercises DOCX composition through the normal DOCX engine;
9. exercises output locking, transaction staging/promotion, reports, manifest, and checksums;
10. verifies two validated manuscript artifacts plus generated manifest/checksum evidence exist;
11. deletes the temporary smoke fixture when the process exits normally.

This is substantially stronger than checking that PyInstaller merely produced a file: the generated binary must initialize the desktop stack and execute the core PDF/DOCX publication path.

It still does **not** replace clean-machine interactive acceptance, large real-world manuscript fidelity testing, signing, or notarization.

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
DocMergeForge-Windows-unsigned.zip.sha256
```

macOS:

```text
DocMergeForge-macOS-unsigned.tar.gz
DocMergeForge-macOS-unsigned.tar.gz.sha256
```

Linux:

```text
DocMergeForge-Linux-unsigned.tar.gz
DocMergeForge-Linux-unsigned.tar.gz.sha256
```

The uploaded artifact container names also include `unsigned`.

## Archive and checksum generation

Windows archives with PowerShell `Compress-Archive`, then records `Get-FileHash -Algorithm SHA256` in the `.sha256` sidecar.

macOS archives the native `.app` bundle when PyInstaller creates it (falling back to onedir when needed), then uses:

```bash
shasum -a 256 DocMergeForge-macOS-unsigned.tar.gz > DocMergeForge-macOS-unsigned.tar.gz.sha256
shasum -a 256 -c DocMergeForge-macOS-unsigned.tar.gz.sha256
```

Linux archives the onedir bundle and uses:

```bash
sha256sum DocMergeForge-Linux-unsigned.tar.gz > DocMergeForge-Linux-unsigned.tar.gz.sha256
sha256sum -c DocMergeForge-Linux-unsigned.tar.gz.sha256
```

These are development-artifact integrity hashes. If a production artifact is signed, notarized, repackaged, or otherwise changed later, generate and publish a new checksum for the exact final bytes users download.

## How to run manually

From the repository Actions tab:

1. open **Package Desktop**;
2. choose **Run workflow**;
3. select the intended branch/ref;
4. run the workflow;
5. wait for all intended matrix jobs to finish;
6. inspect each build, packaged smoke, hash, and upload step before downloading artifacts.

A manual run is a development packaging action unless release signing/acceptance is separately completed.

## Tag-triggered packaging

A `v*` tag causes the same unsigned packaging workflow to run.

Important: a tag does not automatically make an artifact production-ready. Before creating a stable release tag, follow the repository release process and complete the acceptance matrix.

## Artifact download and verification

After a successful workflow run:

1. download each platform artifact;
2. record workflow run ID and head commit SHA;
3. extract the workflow artifact ZIP/container;
4. verify the included `.sha256` sidecar against the packaged archive;
5. extract the platform archive into a clean location;
6. launch it on the matching target OS normally, not only with smoke mode;
7. perform representative packaged-app merge acceptance;
8. retain the final hash/evidence with the release candidate.

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
- launches the packaged executable;
- performs a tiny packaged PDF+DOCX publication;
- archives the application;
- generates a SHA-256 sidecar;
- uploads the archive plus checksum.

This closes the earlier gaps where CI proved packaging configuration without launching the binary or exercising its bundled document pipeline.

It still does not prove production distribution acceptance.

## Relationship to Quality, Regression, Recovery, and Security

Before treating Package Desktop output as a release candidate, verify the same implementation line has appropriate green results from:

- Quality;
- 120-Part Regression;
- Build Smoke;
- Recovery Acceptance when transaction/recovery code changed;
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

## Suggested future release workflow separation

A robust future structure can separate:

1. **Build** — create unsigned native artifacts.
2. **Verify** — launch/test/hash unsigned artifacts.
3. **Sign** — sign only verified immutable inputs.
4. **Notarize** — macOS notarization where required.
5. **Re-verify** — verify final signed/notarized artifacts.
6. **Publish** — attach final hashes/artifacts to a release.

This is a recommended production architecture, not a claim that signing/notarization/publishing already exists.

## CI packaging acceptance record

Record at minimum:

```text
Commit/tag:
Workflow run ID:
Windows build/publication smoke: pass/fail
macOS build/publication smoke: pass/fail
Linux build/publication smoke: pass/fail
Windows artifact + SHA-256:
macOS artifact + SHA-256:
Linux artifact + SHA-256:
Clean-machine interactive verification:
Signing status:
Notarization status:
Known deviations:
```

## Current limitations

The current workflow does not:

- sign Windows executables;
- notarize macOS artifacts;
- create MSI/MSIX/DMG/PKG/AppImage/DEB/RPM;
- publish signed/final release checksums to a GitHub Release;
- create a GitHub Release;
- prove clean-machine interactive use;
- prove large/representative real-world manuscript fidelity from the packaged application.

Those steps remain documented release gates, not hidden assumptions.
