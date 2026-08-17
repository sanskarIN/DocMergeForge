# CI Packaging Guide

This guide documents the repository's current default **onedir** executable-packaging automation and how to consume its unsigned artifacts safely.

## Workflow

```text
.github/workflows/package.yml
```

Workflow name:

```text
Package Desktop
```

Triggers:

- manual `workflow_dispatch`;
- pushes of tags matching `v*`;
- `main` pushes when packaging-relevant files change.

The path filter includes the workflow itself, `pyproject.toml`, desktop/provenance build scripts, `src/docmergeforge/packaging/**`, and `src/docmergeforge/ui/**`.

## Native build matrix

| Runner | Python |
|---|---|
| `windows-latest` | 3.12 |
| `macos-latest` | 3.12 |
| `ubuntu-latest` | 3.12 |

`fail-fast: false` allows platform-specific evidence to complete independently.

## Build-host stages

For every native platform, Package Desktop currently:

1. checks out the source revision;
2. sets up Python 3.12;
3. installs Linux `libegl1` where required;
4. installs `.[build]`;
5. runs packaging preflight;
6. builds the native PyInstaller onedir application;
7. executes `--packaged-smoke` on the built application;
8. performs a real temporary mixed PDF+DOCX publication inside that packaged process;
9. archives the application;
10. creates/verifies an archive SHA-256 sidecar;
11. generates privacy-safe provenance bound to the exact archive filename, byte size, and SHA-256;
12. uploads archive, `.sha256`, and `.provenance.json` together.

## Fresh-runner stages

After all build jobs finish, a second Windows/macOS/Ubuntu matrix consumes the uploaded artifacts.

These verification jobs intentionally do **not**:

- check out the repository;
- set up Python;
- install DocMergeForge;
- install PyInstaller/build dependencies.

Linux installs only the documented `libegl1` system runtime.

Each fresh runner:

1. downloads its named workflow artifact;
2. reads the provenance JSON;
3. recomputes archive SHA-256 and byte size;
4. requires provenance source SHA to equal the workflow head SHA;
5. requires build mode `onedir` and the expected artifact label;
6. requires `signed: false` and `notarized: false` for the current unsigned stage;
7. requires provenance archive filename/size/SHA-256 to equal the downloaded archive;
8. independently verifies the `.sha256` sidecar;
9. extracts the archive;
10. locates the native packaged application;
11. executes `--packaged-smoke` again.

This is automated **downloaded-artifact verification**, stronger than launching only the pre-upload `dist` output.

## Verified final evidence

Archive-bound provenance run:

```text
Run: 32025126032
Checkpoint: 59107192d494d76a4112cdeaa9a55f01cfe37972
Windows build: PASS
macOS build: PASS
Ubuntu build: PASS
Windows fresh runner: PASS
macOS fresh runner: PASS
Ubuntu fresh runner: PASS
```

Artifacts:

```text
Windows ID: 9286905238
macOS ID:   9286908194
Linux ID:   9286879514
```

See [Build Provenance](provenance.md) for the corresponding GitHub artifact-container digests and provenance details.

## Packaged smoke coverage

PyInstaller uses:

```text
src/docmergeforge/ui/packaged_entry.py
```

Normal launches delegate to the existing desktop main path. `--packaged-smoke` is a deterministic acceptance mode that initializes Qt/settings/logging/theme, constructs the main window, creates a temporary PDF and DOCX, executes a one-part mixed project through the real merge service, verifies both manuscript outputs plus manifest/checksum evidence, and exits.

It exercises bundled `pypdf`, `python-docx`, `docxcompose`, ReportLab publication helpers, source hashing, output locking, transactional publication, and evidence generation.

## Artifact files

Windows:

```text
DocMergeForge-Windows-unsigned.zip
DocMergeForge-Windows-unsigned.zip.sha256
DocMergeForge-Windows-unsigned.provenance.json
```

macOS:

```text
DocMergeForge-macOS-unsigned.tar.gz
DocMergeForge-macOS-unsigned.tar.gz.sha256
DocMergeForge-macOS-unsigned.provenance.json
```

Linux:

```text
DocMergeForge-Linux-unsigned.tar.gz
DocMergeForge-Linux-unsigned.tar.gz.sha256
DocMergeForge-Linux-unsigned.provenance.json
```

Artifact names retain `unsigned` deliberately.

## Archive behavior

Windows uses `Compress-Archive` around the onedir application. macOS archives the native `.app` bundle when PyInstaller creates it and otherwise uses the onedir fallback. Linux archives `dist/DocMergeForge`.

The archive-level SHA-256 is recorded both in the `.sha256` sidecar and inside provenance. The fresh runner recomputes the archive identity independently and requires both metadata paths to agree.

## Relationship to Build Smoke

`Build Smoke` verifies source compilation, CLI availability, accessibility metadata, and packaging preflight. It does not invoke the complete PyInstaller build.

`Package Desktop` actually builds, executes, archives, hashes, provenance-binds, uploads, downloads, re-verifies, extracts, and executes the artifact on a separate runner.

## Relationship to Onefile Acceptance

`Package Desktop` is the default onedir distribution workflow. `--one-file` is treated separately by:

```text
.github/workflows/onefile-acceptance.yml
```

Onefile Acceptance run `32025167433` passed the same archive-bound provenance/fresh-runner model on Windows/macOS/Ubuntu. Do not infer onefile acceptance from onedir or vice versa.

## Manual consumption

When downloading an artifact for review:

1. record run ID and head commit;
2. extract the GitHub workflow-artifact container;
3. inspect provenance;
4. verify the packaged archive against its `.sha256` sidecar;
5. verify provenance archive filename/size/SHA-256 against the same archive;
6. extract the platform archive;
7. launch normally on the matching OS;
8. perform representative human packaged-app testing before a production claim.

## Current trust boundary

The workflow has no production signing credentials or signing/notarization stages. Provenance intentionally records:

```json
{
  "signed": false,
  "notarized": false
}
```

Do not remove `unsigned` from artifact naming or change those values until signing/notarization are actually performed and independently verified.

## Remaining production gates

Package Desktop does not by itself prove:

- Windows production signing/SmartScreen acceptance;
- macOS Developer ID signing/notarization/stapling;
- human interactive clean-machine UI acceptance;
- representative real-world manuscript fidelity;
- human accessibility acceptance;
- measured multi-gigabyte workload acceptance;
- MSI/MSIX/DMG/PKG/AppImage/DEB/RPM installer/container support;
- final post-signing release hashes/provenance;
- stable `v1.0.0` readiness.

See [Executable Verification](verification.md), [Release Build Checklist](release-checklist.md), and [Release Process](../release-process.md).
