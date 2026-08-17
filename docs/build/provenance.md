# Build Provenance

DocMergeForge includes a privacy-safe build provenance generator for executable artifacts. It is designed to make release/debug evidence more reproducible without copying arbitrary environment variables, secrets, manuscript paths, or document contents into build metadata.

## Implementation

Library:

```text
src/docmergeforge/packaging/provenance.py
```

Command wrapper:

```text
scripts/write_build_provenance.py
```

## Command

Example onedir build metadata:

```bash
python scripts/write_build_provenance.py \
  --output DocMergeForge-Linux-unsigned.provenance.json \
  --mode onedir \
  --artifact-label DocMergeForge-Linux-unsigned
```

Example onefile metadata:

```bash
python scripts/write_build_provenance.py \
  --output DocMergeForge-Windows-onefile-unsigned.provenance.json \
  --mode onefile \
  --artifact-label DocMergeForge-Windows-onefile-unsigned
```

## Recorded fields

Schema version `1` currently records:

- application name and DocMergeForge version;
- artifact label;
- build mode (`onedir` or `onefile`);
- explicit `signed: false` and `notarized: false` for the current unsigned build stage;
- GitHub source commit/repository/ref when available;
- operating system/release;
- machine architecture;
- Python version/implementation;
- Python executable filename, not its full local path;
- PyInstaller version when installed;
- allowlisted CI run identity;
- installed Python distribution names/versions;
- UTC generation timestamp;
- a privacy note describing the metadata boundary.

## CI allowlist

Only these CI environment variables are intentionally copied when present:

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

The generator does **not** enumerate and serialize the full environment.

Therefore values such as signing passwords, tokens, arbitrary secrets, user environment variables, and unrelated credentials are excluded by design.

## Dependency snapshot

The provenance JSON records installed Python distributions as sorted name/version pairs. This is stronger evidence than the dependency ranges in `pyproject.toml`, because a PyInstaller build uses the versions actually installed in its build environment.

It is still not a cryptographic software bill of materials. A future SBOM/signing pipeline can add stronger package hashes, license metadata, and attestations when required.

## Atomic write

`write_provenance()` writes a temporary JSON file and replaces the requested path after serialization completes. This avoids leaving a partially written provenance file after an ordinary write failure.

## Privacy boundary

Provenance must never include:

- manuscript paths or filenames;
- manuscript contents;
- PDF passwords;
- signing private keys/passwords;
- API tokens;
- arbitrary environment dumps;
- user home-directory paths when avoidable;
- diagnostic exports unrelated to the build.

Unit tests include secret-like environment values and verify they are not serialized.

## Unsigned versus signed provenance

The current generator describes the **unsigned build stage** and deliberately sets:

```json
{
  "signed": false,
  "notarized": false
}
```

Do not edit those fields to `true` merely because signing is planned.

A future production signing/notarization pipeline should create a separate post-signing attestation or validated final provenance record after signatures/notarization are actually applied and verified.

## Hash relationship

Provenance is different from the archive SHA-256 sidecar:

- provenance explains **what/how/where** was built;
- SHA-256 identifies the exact archive bytes.

For release evidence, retain both.

If signing/notarization/repacking changes artifact bytes, regenerate the final artifact hash. Do not reuse an unsigned-archive hash for a changed signed artifact.

## Local build use

Outside GitHub Actions, unavailable CI fields are recorded as `unknown` where applicable. The runtime/build fields and installed distribution snapshot remain useful.

For high-value local release builds, record the source commit externally as well and build from a clean, reviewed checkout.

## Current integration status

The provenance generator and its unit tests are implemented. It is a reusable packaging primitive.

Until the package/onefile workflows explicitly generate, upload, and fresh-runner-verify provenance files, do not state that every CI artifact already contains provenance. That integration is a separate acceptance step.

## Future production improvements

Possible future additions include:

- SPDX/CycloneDX SBOM;
- package hashes;
- builder identity attestation;
- GitHub artifact attestation;
- signing certificate identity/status;
- macOS notarization request/status;
- final download URL/hash;
- reproducible-build comparison evidence.

Each addition should preserve the privacy boundary and be backed by verification, not only metadata generation.
