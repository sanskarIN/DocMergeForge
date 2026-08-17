# Executable Build Documentation

This directory is the canonical build and packaging manual for DocMergeForge desktop executables.

DocMergeForge currently uses **PyInstaller** through `scripts/build_desktop.py`. Supported repository build modes are:

- **onedir** — default distribution/development build mode;
- **onefile** — optional single-file PyInstaller mode with an independent acceptance workflow;
- **unsigned native CI artifacts** — Windows, macOS, and Linux archives with packaged publication smoke, archive checksum, archive-bound JSON provenance, CycloneDX SBOM, signed GitHub/Sigstore build provenance, signed CycloneDX predicate, and independent fresh-runner verification.

The repository does **not** currently claim production-signed Windows binaries, macOS Developer ID/notarized applications, native installers, or a stable `v1.0.0` release.

> **Made by the Sanskar** · [Buy Me a Coffee](https://buymeacoffee.com/sanskarIN)

## Build documentation map

1. [Common Build Guide](common.md)
2. Native guides — [Windows](windows.md), [macOS](macos.md), [Linux](linux.md)
3. [CI Packaging](ci-packaging.md)
4. [Build Provenance and SBOM](provenance.md)
5. [Signing and Notarization](signing-and-notarization.md)
6. [Executable Verification](verification.md)
7. [Build Troubleshooting](troubleshooting.md)
8. [Release Build Checklist](release-checklist.md)
9. [Release Evidence Ledger](../release-evidence.md)

## Canonical build commands

From the repository root after installing `.[build]`:

```bash
python scripts/build_desktop.py --check
python scripts/build_desktop.py
```

Optional onefile build:

```bash
python scripts/build_desktop.py --one-file
```

Explicit repository root:

```bash
python scripts/build_desktop.py --check --root /path/to/DocMergeForge
python scripts/build_desktop.py --root /path/to/DocMergeForge
```

## What the helper packages

`src/docmergeforge/packaging/desktop.py` currently configures PyInstaller to:

- use `src/docmergeforge/ui/packaged_entry.py` as the packaged entry point;
- delegate normal packaged launches to the existing desktop main behavior;
- expose `--packaged-smoke` for deterministic CI acceptance;
- name the application `DocMergeForge`;
- build windowed/clean/non-interactively;
- collect DocMergeForge plus `docxcompose`, `docx`, and `pypdf` dependencies/data;
- include `assets/branding` when present;
- build `--onedir` by default or `--onefile` when requested.

## Native-build rule

PyInstaller is not used here as a general cross-compiler. Build each target on its matching OS or native CI runner:

| Target | Build host |
|---|---|
| Windows | Windows |
| macOS | macOS |
| Linux | Linux |

## Current automated evidence stack

Every current unsigned archive carries or is associated with four complementary evidence layers:

1. `<archive>.sha256` — independent archive checksum;
2. `<artifact-label>.provenance.json` — privacy-safe source/build identity bound to archive filename, byte size, and SHA-256;
3. `<artifact-label>.cdx.json` — validated CycloneDX 1.6 **build-environment dependency SBOM** generated with pinned `cyclonedx-bom==7.3.1`;
4. signed GitHub/Sigstore attestations — one default build-provenance predicate and one CycloneDX predicate for the exact archive.

The CycloneDX document describes the Python build environment used to package the application. It is not represented as a byte-perfect inventory of every component embedded by PyInstaller.

## Package Desktop — onedir

`.github/workflows/package.yml` builds the default onedir package on Windows/macOS/Ubuntu. Each build job:

1. validates packaging configuration;
2. builds the native application;
3. runs the packaged mixed PDF+DOCX smoke;
4. creates the native archive;
5. creates `.sha256` and archive-bound JSON provenance;
6. generates CycloneDX 1.6 JSON;
7. creates signed build-provenance and CycloneDX SBOM attestations;
8. uploads archive/checksum/provenance/SBOM.

A separate fresh-runner matrix downloads only the artifact and must verify:

```bash
gh attestation verify <archive> --repo sanskarIN/DocMergeForge

gh attestation verify <archive> \
  --repo sanskarIN/DocMergeForge \
  --predicate-type https://cyclonedx.org/bom
```

It then independently validates archive-bound JSON provenance, verifies `.sha256`, extracts the archive, and executes the packaged mixed-document smoke again.

Verified CycloneDX/two-predicate evidence:

```text
Run:        32033135355
Checkpoint: 59dc14bbf1d4301177e475ac350694bdd9d90ada
All Windows/macOS/Ubuntu build and fresh-runner jobs: PASS
```

## Onefile Acceptance

`.github/workflows/onefile-acceptance.yml` independently applies the same checksum/provenance/CycloneDX/two-attestation/fresh-runner model to `--one-file` packages.

Verified evidence:

```text
Run:        32033541414
Checkpoint: dc624e23d07e0ce94ef345245630d153ee60091a
All Windows/macOS/Ubuntu build and fresh-runner jobs: PASS
```

Onedir and onefile are separate distribution surfaces; one does not prove the other.

## Current unsigned artifact families

Onedir archives:

```text
DocMergeForge-Windows-unsigned.zip
DocMergeForge-macOS-unsigned.tar.gz
DocMergeForge-Linux-unsigned.tar.gz
```

Onefile archives:

```text
DocMergeForge-Windows-onefile-unsigned.zip
DocMergeForge-macOS-onefile-unsigned.tar.gz
DocMergeForge-Linux-onefile-unsigned.tar.gz
```

Each workflow artifact also contains matching `.sha256`, `.provenance.json`, and `.cdx.json` evidence files. The names intentionally retain `unsigned`.

## Development build versus production distribution

A successful PyInstaller build plus fresh-runner checksum/provenance/SBOM/attestation verification is strong automated distribution evidence, but it still does not equal production acceptance.

Remaining production-oriented gates include:

- human interactive clean-machine testing;
- representative real-world PDF/DOCX fidelity review;
- human accessibility acceptance;
- measured multi-gigabyte stress if such scale is claimed;
- Windows Authenticode/SmartScreen review where distributed;
- macOS Developer ID signing/notarization/stapling/Gatekeeper review where distributed;
- intentional installer/container formats and their acceptance;
- final post-signing/post-notarization hashes, provenance, SBOM, and trust verification;
- exact post-bundling binary/component inventory if that stronger supply-chain claim is required.

## Final-byte rule

Current checksums/provenance/SBOM predicates attest the exact **unsigned archive bytes** created by CI. If signing, notarization, stapling, installer wrapping, or repackaging changes those bytes, generate new evidence for the final distribution artifact. Never reuse unsigned-build hashes or attestations for changed signed bytes.

## Build source of truth

```text
scripts/build_desktop.py
scripts/write_build_provenance.py
src/docmergeforge/packaging/desktop.py
src/docmergeforge/packaging/provenance.py
src/docmergeforge/ui/packaged_entry.py
pyproject.toml
.github/workflows/package.yml
.github/workflows/onefile-acceptance.yml
```

Documentation remains conservative: if these files do not implement and verify a behavior, this manual does not claim it is automated.

## Related documentation

- [Building Executables overview](../building-executables.md)
- [Release Packaging](../release-packaging.md)
- [Release Process](../release-process.md)
- [Testing and CI](../testing-and-ci.md)
- [Security Model](../security.md)
- [Known Limitations](../known-limitations.md)
