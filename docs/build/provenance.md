# Build Provenance

DocMergeForge uses three complementary integrity/provenance layers for current unsigned executable archives:

1. an archive `.sha256` sidecar;
2. a privacy-safe DocMergeForge JSON provenance record bound to archive filename, byte size, and SHA-256;
3. a signed GitHub Artifact Attestation generated with `actions/attest@v4` and independently verified on a fresh native runner.

These layers improve traceability of the unsigned build stage. They do **not** substitute for Windows Authenticode signing, macOS Developer ID signing/notarization, or human production acceptance.

## DocMergeForge provenance implementation

Library:

```text
src/docmergeforge/packaging/provenance.py
```

Command wrapper:

```text
scripts/write_build_provenance.py
```

Tests:

```text
tests/unit/test_build_provenance.py
tests/integration/test_build_provenance_cli.py
```

## Local provenance command

Onedir example:

```bash
python scripts/write_build_provenance.py \
  --output DocMergeForge-Linux-unsigned.provenance.json \
  --mode onedir \
  --artifact-label DocMergeForge-Linux-unsigned \
  --artifact DocMergeForge-Linux-unsigned.tar.gz
```

Onefile example:

```bash
python scripts/write_build_provenance.py \
  --output DocMergeForge-Windows-onefile-unsigned.provenance.json \
  --mode onefile \
  --artifact-label DocMergeForge-Windows-onefile-unsigned \
  --artifact DocMergeForge-Windows-onefile-unsigned.zip
```

`--artifact` is optional for reusable/local metadata generation, but the CI packaging workflows provide it so provenance is bound to the exact archive bytes.

## JSON provenance fields

Schema version `1` records application/version, artifact label, build mode, explicit unsigned/not-notarized state, archive filename/size/SHA-256, source commit/repository/ref, OS/architecture, Python/PyInstaller versions, allowlisted CI identity, installed Python distribution versions, UTC generation time, and the privacy boundary.

The generator refuses a missing artifact path when `--artifact` is requested instead of pretending that archive bytes were inspected.

## CI allowlist and privacy boundary

Only these CI variables are intentionally copied when present:

```text
GITHUB_SHA
GITHUB_REF
GITHUB_REPOSITORY
GITHUB_RUN_ID
GITHUB_RUN_ATTEMPT
GITHUB_WORKFLOW
RUNNER_OS
RUNNER_ARCH
```

The generator does **not** dump the complete environment. It must never serialize manuscripts, PDF passwords, signing credentials, API tokens, arbitrary secrets, avoidable user home paths, or unrelated diagnostics.

Unit tests inject secret-like values and confirm they are not serialized. The CLI integration test executes the real wrapper and checks archive/source identity fields.

## Dependency snapshot

The JSON provenance records installed Python distributions as sorted name/version pairs. This is stronger evidence than dependency ranges alone because it describes the environment actually presented to PyInstaller.

It is **not** a standards-compliant SBOM. SPDX/CycloneDX remains a separate future supply-chain improvement.

## Atomic provenance write

`write_provenance()` writes a temporary JSON file and replaces the requested destination after successful serialization, preventing an ordinary interrupted write from leaving a partially written provenance document.

## Unsigned versus signed state

The current local provenance intentionally records:

```json
{
  "signed": false,
  "notarized": false
}
```

These fields describe platform-distribution trust, not whether a GitHub build-provenance attestation exists. A GitHub/Sigstore attestation does **not** make a Windows executable Authenticode-signed or a macOS application Developer ID signed/notarized.

Never change these booleans because signing is merely planned. They can change only after the corresponding final platform artifact is actually signed/notarized and independently verified.

## GitHub Artifact Attestations

Both Package Desktop and Onefile Acceptance now attest each native archive with:

```text
actions/attest@v4
```

The build job grants only the required additional permissions:

```yaml
permissions:
  contents: read
  id-token: write
  attestations: write
  artifact-metadata: write
```

Each separate fresh runner verifies the downloaded archive before ordinary checksum/provenance/execution checks:

```bash
gh attestation verify <downloaded-archive> --repo sanskarIN/DocMergeForge
```

This adds signed GitHub/Sigstore build provenance bound to the exact archive bytes and independently checks that provenance after the upload/download boundary.

## Verified onedir attestation

```text
Run:        32030972195
Checkpoint: b0e112b0fecf9b6c70fcaeffd0551222dd2ed7aa
```

All Windows/macOS/Ubuntu build jobs and all three fresh-runner jobs passed. Each platform completed native build, packaged mixed PDF+DOCX smoke, archive/hash/local-provenance generation, GitHub Artifact Attestation creation, artifact upload, fresh-runner download, `gh attestation verify`, archive-bound JSON provenance validation, sidecar checksum verification, extraction, and packaged smoke again.

Attestation-era workflow artifact containers:

```text
Windows artifact ID: 9288984074
Container digest: sha256:a169001b7c76777acc6c30f246498b50c8a735c0fafca9657f7738d50f330ed1

macOS artifact ID: 9288934609
Container digest: sha256:e5aff9fc17eec544e395947afe553d5732b8e2af7de9fbfa78ff095a5d92d7f2

Linux artifact ID: 9289011135
Container digest: sha256:2e560f8fb8e3869320c998d3967890b8b22d51c98b7cd308e1063af124662008
```

## Verified onefile attestation

```text
Run:        32031798935
Checkpoint: c42c3cab4083e51255d78730b613af735235494f
```

All Windows/macOS/Ubuntu build and fresh-runner jobs passed the same attestation-first verification sequence for onefile archives.

Attestation-era workflow artifact containers:

```text
Windows artifact ID: 9289300227
Container digest: sha256:58c0b60c67599181463c33f6efb5e77c86fdd29dbf8f98f3c4af3f91ee28867e

macOS artifact ID: 9289251930
Container digest: sha256:ac3e41a5e85891d095053e7d0be5c75a519502c8d0100ea61bfa7614b836cab1

Linux artifact ID: 9289257661
Container digest: sha256:d698e261487e756adf5eabbb4e169e99467d16842753a1a0f56341fdd02c1b3b
```

The GitHub artifact-container digest identifies the Actions artifact container. It is additional workflow evidence and must not be confused with the inner platform archive digest. The actual archive retains its own `.sha256`, archive SHA-256/size in DocMergeForge provenance, and GitHub attestation.

## What the combined evidence proves

For current unsigned onedir and onefile CI archives, the repository now has evidence that:

- the package is traceable to source/build context;
- local JSON provenance is privacy-filtered and archive-bound;
- a compact independent SHA-256 sidecar matches the archive;
- signed GitHub/Sigstore build provenance exists for the archive;
- a separate native runner verifies that attestation after download;
- the fresh runner also recomputes archive identity and validates local provenance/checksum;
- the downloaded package extracts and executes a real packaged mixed PDF+DOCX publication smoke.

This does **not** prove production code signing, notarization, interactive clean-machine UX, representative real-world fidelity, accessibility acceptance, installer behavior, multi-gigabyte scale, or stable-release readiness.

## Final-byte rule

Checksums, local provenance, and build attestations describe the exact bytes they were created for. If signing, notarization, stapling, installer wrapping, or repackaging changes artifact bytes, generate and verify new evidence for the final distribution artifact. Do not reuse an unsigned-build digest for changed signed bytes.

## Future supply-chain improvements

Remaining useful improvements include a standards-compliant SPDX/CycloneDX SBOM, package hashes/licenses, final signing certificate identity/status, macOS notarization evidence, release-channel download identity, and reproducible-build comparison evidence.

Each addition must preserve the privacy boundary and be backed by independent verification rather than metadata generation alone.

See [Release Evidence Ledger](../release-evidence.md), [Executable Verification](verification.md), and [Release Process](../release-process.md).
