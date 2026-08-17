# Build Provenance

DocMergeForge uses four complementary integrity/provenance layers for current unsigned executable archives:

1. an archive `.sha256` sidecar;
2. a privacy-safe DocMergeForge JSON provenance record bound to archive filename, byte size, and SHA-256;
3. a signed GitHub/Sigstore build-provenance attestation generated with `actions/attest@v4`;
4. a CycloneDX 1.6 build-environment dependency SBOM that is also attached to the archive as a separately signed GitHub/Sigstore attestation predicate.

Fresh native runners verify the signed predicates and the local checksum/provenance evidence before executing the downloaded package. These layers improve traceability of the unsigned build stage. They do **not** substitute for Windows Authenticode signing, macOS Developer ID signing/notarization, or human production acceptance.

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

## Dependency snapshot in local JSON provenance

The DocMergeForge JSON provenance records installed Python distributions as sorted name/version pairs. This is useful compact build-environment evidence, but it is not the standards-based SBOM layer.

The standards-based layer is generated separately with CycloneDX as described below.

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

These fields describe platform-distribution trust, not whether GitHub build/SBOM attestations exist. A GitHub/Sigstore attestation does **not** make a Windows executable Authenticode-signed or a macOS application Developer ID signed/notarized.

Never change these booleans because signing is merely planned. They can change only after the corresponding final platform artifact is actually signed/notarized and independently verified.

## GitHub build-provenance attestations

Both Package Desktop and Onefile Acceptance attest each native archive with:

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

## Verified build-provenance attestation runs

Onedir:

```text
Run:        32030972195
Checkpoint: b0e112b0fecf9b6c70fcaeffd0551222dd2ed7aa
```

Onefile:

```text
Run:        32031798935
Checkpoint: c42c3cab4083e51255d78730b613af735235494f
```

All Windows/macOS/Ubuntu build and fresh-runner jobs passed for both modes. See [Release Evidence Ledger](../release-evidence.md) for their artifact IDs/container digests.

## CycloneDX SBOM generation

The build extra pins:

```text
cyclonedx-bom==7.3.1
```

Each platform packaging job runs the official CycloneDX Python generator against the exact build environment presented to PyInstaller:

```bash
cyclonedx-py environment \
  --pyproject pyproject.toml \
  --spec-version 1.6 \
  --output-format JSON \
  --output-file <artifact-label>.cdx.json
```

The generator validates the CycloneDX document under its normal validation behavior. The SBOM file is uploaded beside the archive, checksum sidecar, and DocMergeForge JSON provenance.

### Scope of the SBOM

The current CycloneDX document is a **build-environment dependency SBOM**. It describes the installed Python environment used to package the application and therefore may include PyInstaller/CycloneDX/build-time dependencies that are not embedded in the final executable, while exact binary bundling details remain governed by PyInstaller collection behavior.

Do not describe this SBOM as a byte-perfect post-PyInstaller binary inventory. If that stronger claim is needed later, add a separate binary-content inventory/analysis gate and verify it independently.

## CycloneDX SBOM attestations

Each archive receives a second `actions/attest@v4` invocation with the generated SBOM:

```yaml
- uses: actions/attest@v4
  with:
    subject-path: <archive>
    sbom-path: <artifact-label>.cdx.json
```

For CycloneDX JSON, GitHub records the predicate type:

```text
https://cyclonedx.org/bom
```

Each fresh runner therefore verifies two distinct predicates:

```bash
gh attestation verify <archive> --repo sanskarIN/DocMergeForge

gh attestation verify <archive> \
  --repo sanskarIN/DocMergeForge \
  --predicate-type https://cyclonedx.org/bom
```

Only after both signed predicates pass does the workflow continue to local JSON provenance, `.sha256`, extraction, and packaged mixed PDF+DOCX smoke.

## Verified CycloneDX onedir acceptance

```text
Run:        32033135355
Checkpoint: 59dc14bbf1d4301177e475ac350694bdd9d90ada
```

All Windows/macOS/Ubuntu build jobs and all three fresh-runner jobs passed SBOM generation, build-provenance attestation, CycloneDX SBOM attestation, upload/download, both predicate verifications, archive-bound JSON provenance verification, checksum verification, extraction, and packaged mixed-document smoke.

SBOM-era workflow artifact containers:

```text
Windows artifact ID: 9289721065
Container digest: sha256:f00410bd8016ca05243a0be114dbe3ab336529f7a2b2251968b42922cc67e37d

macOS artifact ID: 9289679866
Container digest: sha256:c9ffec38d0c70b50e24bbd54e74c29d69b52206540b1402c9a76cbf535e54539

Linux artifact ID: 9289686689
Container digest: sha256:30b851a609ae3394174015f4f80fce52b356069131395978039c5ad82122a143
```

## Verified CycloneDX onefile acceptance

```text
Run:        32033541414
Checkpoint: dc624e23d07e0ce94ef345245630d153ee60091a
```

All Windows/macOS/Ubuntu build and fresh-runner jobs passed the same two-predicate SBOM/provenance verification sequence for onefile archives.

SBOM-era workflow artifact containers:

```text
Windows artifact ID: 9289869031
Container digest: sha256:23082e8dce64e5225aa8234d0054f1c7c731dacd9810816a7d7a499759b5ebb6

macOS artifact ID: 9289825286
Container digest: sha256:474cc73883e67fd0bbc074ef3fdbccd9de709a8a5f1a220582c53a25c662c35c

Linux artifact ID: 9289846554
Container digest: sha256:44aba02321c0c09103987b1dc18eea5553ba16b00162ca9fed3af4420835bbda
```

## Container digest versus archive digest

The GitHub artifact-container digest identifies the Actions artifact container. It is additional workflow evidence and must not be confused with the inner platform archive digest.

The actual platform archive retains:

- its own `.sha256` sidecar;
- archive filename/size/SHA-256 in DocMergeForge JSON provenance;
- a signed GitHub/Sigstore build-provenance attestation;
- a signed CycloneDX SBOM predicate;
- the uploaded `.cdx.json` build-environment SBOM.

## What the combined evidence proves

For current unsigned onedir and onefile CI archives, the repository has evidence that:

- the package is traceable to source/build context;
- local JSON provenance is privacy-filtered and archive-bound;
- an independent SHA-256 sidecar matches the archive;
- signed GitHub/Sigstore build provenance exists for the archive;
- a validated CycloneDX 1.6 build-environment dependency SBOM is generated;
- a signed CycloneDX SBOM predicate is bound to the archive;
- a separate native runner verifies both signed predicates after download;
- the fresh runner also recomputes archive identity and validates local provenance/checksum;
- the downloaded package extracts and executes a real packaged mixed PDF+DOCX publication smoke.

This does **not** prove production code signing, notarization, interactive clean-machine UX, representative real-world fidelity, human accessibility acceptance, installer behavior, multi-gigabyte scale, or a byte-perfect post-PyInstaller binary inventory.

## Final-byte rule

Checksums, local provenance, SBOM predicates, and build attestations describe the exact archive bytes they were created for. If signing, notarization, stapling, installer wrapping, or repackaging changes artifact bytes, generate and verify new evidence for the final distribution artifact. Do not reuse unsigned-build evidence for changed signed bytes.

## Future supply-chain improvements

Remaining useful improvements include exact post-bundling binary/component inventory if required, package/license policy validation, final signing certificate identity/status, macOS notarization evidence, release-channel download identity, and reproducible-build comparison evidence.

Each addition must preserve the privacy boundary and be backed by independent verification rather than metadata generation alone.

See [Release Evidence Ledger](../release-evidence.md), [Executable Verification](verification.md), and [Release Process](../release-process.md).
