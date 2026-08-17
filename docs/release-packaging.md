# Release Packaging

DocMergeForge has verified native PyInstaller pipelines for default onedir and optional onefile packages on Windows, macOS, and Ubuntu. Current CI outputs remain **unsigned development archives**; production platform signing, notarization, installer/container distribution, and human clean-machine acceptance remain separate release gates.

For commands, see [Building Executables](building-executables.md) and the [Complete Executable Build Manual](build/README.md). For acceptance policy, see [Release Process](release-process.md) and [Release Evidence Ledger](release-evidence.md).

## Shared packaging configuration

Packaging arguments live in:

```text
src/docmergeforge/packaging/desktop.py
```

The build helper:

```text
scripts/build_desktop.py
```

uses that shared configuration so tests, local builds, and CI share one PyInstaller argument source.

Current packaged entry point:

```text
src/docmergeforge/ui/packaged_entry.py
```

Normal packaged launches delegate to the desktop main behavior. `--packaged-smoke` is a deterministic CI acceptance interface.

## Local packaging

Install build tooling:

```bash
pip install -e ".[build]"
```

The build extra currently includes PyInstaller and pinned `cyclonedx-bom==7.3.1` for supply-chain evidence generation.

Preflight:

```bash
python scripts/build_desktop.py --check
```

Onedir:

```bash
python scripts/build_desktop.py
```

Onefile:

```bash
python scripts/build_desktop.py --one-file
```

PyInstaller normally writes generated state to `build/` and `dist/`.

## Package Desktop — default onedir

Workflow:

```text
.github/workflows/package.yml
```

Triggers:

- manual dispatch;
- tags matching `v*`;
- packaging/UI-related changes on `main`.

Per-workflow/ref concurrency cancels stale in-progress package runs so obsolete `main` commits do not continue consuming native runner capacity.

Native matrix:

- `windows-latest`;
- `macos-latest`;
- `ubuntu-latest`;
- Python 3.12.

Every platform builds the real application, runs packaged mixed PDF+DOCX smoke, archives it, creates checksum/JSON provenance/CycloneDX evidence, creates two signed GitHub/Sigstore attestations, uploads the evidence bundle, then participates in a separate fresh-runner verification matrix.

## Onefile Acceptance

Workflow:

```text
.github/workflows/onefile-acceptance.yml
```

Onefile is independently built and accepted on the same three native runner families. It has its own stale-run cancellation group and must pass its own build-host plus fresh-runner sequence; onedir evidence is not reused to prove onefile behavior.

## Current evidence bundle

For each unsigned native archive, CI uploads:

```text
<archive>
<archive>.sha256
<artifact-label>.provenance.json
<artifact-label>.cdx.json
```

The JSON provenance is privacy-filtered and bound to the exact archive filename, byte size, and SHA-256.

The CycloneDX 1.6 JSON describes the Python **build environment** used by PyInstaller. It may include build-time tools and is not claimed to be a byte-perfect post-bundling executable inventory.

## Signed GitHub/Sigstore predicates

Each archive receives two separate `actions/attest@v4` attestations:

1. default build provenance;
2. CycloneDX predicate type `https://cyclonedx.org/bom`.

Fresh runners require both:

```bash
gh attestation verify <archive> --repo sanskarIN/DocMergeForge

gh attestation verify <archive> \
  --repo sanskarIN/DocMergeForge \
  --predicate-type https://cyclonedx.org/bom
```

Only after both signed predicates pass does verification continue to local provenance, `.sha256`, extraction, and the downloaded packaged smoke.

GitHub/Sigstore build attestations do **not** mean the Windows executable is Authenticode-signed or the macOS application is Developer ID signed/notarized.

## Verified executable evidence

Verified SBOM/two-predicate onedir acceptance:

```text
Package Desktop run: 32033135355
Checkpoint:          59dc14bbf1d4301177e475ac350694bdd9d90ada
All six jobs:        PASS
```

Verified SBOM/two-predicate onefile acceptance:

```text
Onefile Acceptance run: 32033541414
Checkpoint:              dc624e23d07e0ce94ef345245630d153ee60091a
All six jobs:            PASS
```

Subsequent concurrency-only workflow commits are verified separately in `CHANGELOG.md` / `what_changed.md` once their full matrices complete.

## Current unsigned archive names

Onedir:

```text
DocMergeForge-Windows-unsigned.zip
DocMergeForge-macOS-unsigned.tar.gz
DocMergeForge-Linux-unsigned.tar.gz
```

Onefile:

```text
DocMergeForge-Windows-onefile-unsigned.zip
DocMergeForge-macOS-onefile-unsigned.tar.gz
DocMergeForge-Linux-onefile-unsigned.tar.gz
```

The `unsigned` label is intentional and must remain until real platform signing/notarization has been performed and verified.

## Windows distribution status

Automated foundation now includes native PyInstaller build, archive, checksum, JSON provenance, CycloneDX SBOM, signed build/SBOM predicates, fresh-runner verification, and packaged mixed-document smoke.

Still separate production gates:

- Authenticode signing and timestamping;
- SmartScreen/trust review;
- MSI/MSIX/Inno/NSIS or another intentional installer;
- installer signing;
- representative human clean-machine install/upgrade/uninstall acceptance.

## macOS distribution status

Automated foundation now includes native `.app`/PyInstaller output, archive, checksum, JSON provenance, CycloneDX SBOM, both signed predicates, fresh-runner verification, and packaged mixed-document smoke.

Still separate production gates:

- Developer ID signing;
- hardened runtime/entitlements review where required;
- notarization;
- stapling;
- Gatekeeper acceptance;
- DMG/PKG or another intentional distribution container;
- representative clean-Mac human acceptance.

## Linux distribution status

Automated foundation includes Ubuntu-hosted PyInstaller build, tar archive, checksum/provenance/SBOM, both signed predicates, and fresh-runner smoke using only the documented `libegl1` system runtime prerequisite.

Still separate claims if desired:

- AppImage;
- DEB/RPM;
- repository/package signing;
- broad distro/glibc compatibility;
- Flatpak/Snap.

## Build Smoke versus Package Desktop

Build Smoke verifies source compilation, CLI availability, accessibility metadata/preference smoke, and packaging preflight on Windows/macOS/Linux. It does not run full PyInstaller packaging.

Package Desktop and Onefile Acceptance create and independently consume real uploaded packages, including supply-chain evidence and packaged mixed-document execution.

## Artifact hashing and final-byte rule

Current hashes/provenance/SBOM predicates describe exact **unsigned CI archive bytes**.

If signing, notarization, stapling, installer wrapping, or repackaging changes bytes, generate new final SHA-256 and appropriate final-stage provenance/SBOM/attestation evidence. Never publish an unsigned-stage hash as the hash of a changed signed artifact.

## Signing credentials

Production signing secrets must never be committed. Use protected CI secret stores, HSM/certificate services where appropriate, least privilege, controlled trigger permissions, rotation procedures, and independent verification.

## Human packaged-app acceptance

Automated `--packaged-smoke` is strong downloaded-artifact evidence but remains headless/deterministic. Before production support claims, representative clean machines should exercise normal UI launch, project/source selection, ordering, PDF/DOCX/mixed projects, encrypted-PDF interaction, cancellation/recovery, Unicode/long paths, accessibility, trust prompts, and normal exit/relaunch.

## Reproducibility

Centralized build arguments, dependency snapshots, checksums, SBOMs, and attestations improve traceability, but bit-for-bit reproducible binaries are not currently claimed. If reproducible-build equivalence becomes a requirement, add a deliberate repeated-build comparison gate.

## Production packaging definition of done

A production distribution target is complete only when the intended final bytes have passed relevant source/recovery/stress/fidelity/accessibility gates; downloaded-artifact evidence is current; signing/notarization succeeds where claimed; final signatures/trust are independently verified; intended installer/container behavior is accepted; final hashes/provenance/SBOM evidence match the distributed bytes; and release notes accurately state support and limitations.

Until then, the correct term remains **unsigned development build**.
