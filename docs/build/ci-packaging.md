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

1. checks out the source revision with `actions/checkout@v7`;
2. sets up Python 3.12 with `actions/setup-python@v7`;
3. installs Linux `libegl1` where required;
4. installs `.[build]`, including PyInstaller and pinned `cyclonedx-bom==7.3.1`;
5. runs packaging preflight;
6. builds the native PyInstaller onedir application;
7. executes `--packaged-smoke` on the built application;
8. performs a real temporary mixed PDF+DOCX publication inside that packaged process;
9. archives the application;
10. creates/verifies an archive SHA-256 sidecar;
11. generates privacy-safe JSON provenance bound to the exact archive filename, byte size, and SHA-256;
12. generates a validated CycloneDX 1.6 JSON build-environment dependency SBOM;
13. creates a signed GitHub/Sigstore build-provenance attestation for the archive;
14. creates a second signed GitHub/Sigstore CycloneDX SBOM attestation for the same archive;
15. uploads archive, `.sha256`, `.provenance.json`, and `.cdx.json` together using `actions/upload-artifact@v7`.

## Fresh-runner stages

After all build jobs finish, a second Windows/macOS/Ubuntu matrix consumes the uploaded artifacts.

These verification jobs intentionally do **not** check out the repository, set up Python, install DocMergeForge, or install PyInstaller/build dependencies. Linux installs only the documented `libegl1` system runtime.

Each fresh runner:

1. downloads its named workflow artifact with `actions/download-artifact@v8`;
2. verifies signed default build provenance with `gh attestation verify`;
3. separately requires predicate type `https://cyclonedx.org/bom`;
4. reads the DocMergeForge provenance JSON;
5. recomputes archive SHA-256 and byte size;
6. requires provenance source SHA to equal the workflow head SHA;
7. requires build mode `onedir` and the expected artifact label;
8. requires `signed: false` and `notarized: false` for the current unsigned platform-distribution stage;
9. requires provenance archive filename/size/SHA-256 to equal the downloaded archive;
10. independently verifies the `.sha256` sidecar;
11. extracts the archive;
12. locates the native packaged application;
13. executes `--packaged-smoke` again.

This is automated **downloaded-artifact verification**, stronger than launching only the pre-upload `dist` output.

## Current verified evidence

CycloneDX/two-attestation run:

```text
Run:        32033135355
Checkpoint: 59dc14bbf1d4301177e475ac350694bdd9d90ada
Windows build: PASS
macOS build:   PASS
Ubuntu build:  PASS
Windows fresh runner: PASS
macOS fresh runner:   PASS
Ubuntu fresh runner:  PASS
```

SBOM-era artifact containers:

```text
Windows ID: 9289721065
Container digest: sha256:f00410bd8016ca05243a0be114dbe3ab336529f7a2b2251968b42922cc67e37d

macOS ID: 9289679866
Container digest: sha256:c9ffec38d0c70b50e24bbd54e74c29d69b52206540b1402c9a76cbf535e54539

Linux ID: 9289686689
Container digest: sha256:30b851a609ae3394174015f4f80fce52b356069131395978039c5ad82122a143
```

See [Build Provenance](provenance.md) and [Release Evidence Ledger](../release-evidence.md) for evidence semantics and history.

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
DocMergeForge-Windows-unsigned.cdx.json
```

macOS:

```text
DocMergeForge-macOS-unsigned.tar.gz
DocMergeForge-macOS-unsigned.tar.gz.sha256
DocMergeForge-macOS-unsigned.provenance.json
DocMergeForge-macOS-unsigned.cdx.json
```

Linux:

```text
DocMergeForge-Linux-unsigned.tar.gz
DocMergeForge-Linux-unsigned.tar.gz.sha256
DocMergeForge-Linux-unsigned.provenance.json
DocMergeForge-Linux-unsigned.cdx.json
```

Artifact names retain `unsigned` deliberately.

## Archive and SBOM scope

Windows uses `Compress-Archive` around the onedir application. macOS archives the native `.app` bundle when PyInstaller creates it and otherwise uses the onedir fallback. Linux archives `dist/DocMergeForge`.

The archive-level SHA-256 is recorded both in the `.sha256` sidecar and inside DocMergeForge provenance. The fresh runner recomputes archive identity independently and requires both metadata paths to agree.

The CycloneDX file describes the installed Python **build environment** used by PyInstaller. It may include build-time tools such as PyInstaller/CycloneDX components and is not represented as a byte-perfect post-bundling inventory of the executable.

## Signed attestation verification

Fresh runners require both predicates independently:

```bash
gh attestation verify <archive> --repo sanskarIN/DocMergeForge

gh attestation verify <archive> \
  --repo sanskarIN/DocMergeForge \
  --predicate-type https://cyclonedx.org/bom
```

A successful GitHub/Sigstore attestation does not mean Windows Authenticode signing or macOS Developer ID signing/notarization has occurred.

## Relationship to Build Smoke

`Build Smoke` verifies source compilation, CLI availability, accessibility metadata/preference smoke, and packaging preflight. It does not invoke the complete PyInstaller build.

`Package Desktop` actually builds, executes, archives, hashes, provenance-binds, generates/attests an SBOM, uploads, downloads, re-verifies signed/local evidence, extracts, and executes the artifact on a separate runner.

## Relationship to Onefile Acceptance

`Package Desktop` is the default onedir distribution workflow. `--one-file` is treated separately by:

```text
.github/workflows/onefile-acceptance.yml
```

Current onefile CycloneDX evidence:

```text
Run:        32033541414
Checkpoint: dc624e23d07e0ce94ef345245630d153ee60091a
All six jobs: PASS
```

Do not infer onefile acceptance from onedir or vice versa.

## Manual consumption

When downloading an artifact for review:

1. record run ID and head commit;
2. extract the GitHub workflow-artifact container;
3. verify default build provenance;
4. verify the CycloneDX predicate;
5. inspect local JSON provenance and `.cdx.json` scope/content;
6. verify the packaged archive against its `.sha256` sidecar;
7. verify provenance archive filename/size/SHA-256 against the same archive;
8. extract the platform archive;
9. launch normally on the matching OS;
10. perform representative human packaged-app testing before a production claim.

## Current trust boundary

The workflow has no production signing credentials or platform signing/notarization stages. Local provenance intentionally records:

```json
{
  "signed": false,
  "notarized": false
}
```

Do not remove `unsigned` from artifact naming or change those values until platform signing/notarization are actually performed and independently verified.

## Remaining production gates

Package Desktop does not by itself prove Windows production signing/SmartScreen acceptance, macOS Developer ID signing/notarization/stapling, human interactive clean-machine UI acceptance, representative real-world manuscript fidelity, human accessibility acceptance, measured multi-gigabyte workload acceptance, exact post-bundling binary-component inventory, MSI/MSIX/DMG/PKG/AppImage/DEB/RPM installer/container support, final post-signing release evidence, or stable `v1.0.0` readiness.

See [Executable Verification](verification.md), [Release Build Checklist](release-checklist.md), and [Release Process](../release-process.md).
