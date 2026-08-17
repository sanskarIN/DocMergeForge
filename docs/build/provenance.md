# Build Provenance

DocMergeForge includes a privacy-safe build provenance generator for executable artifacts. It is designed to make release/debug evidence reproducible without copying arbitrary environment variables, secrets, manuscript paths, or document contents into build metadata.

## Implementation

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

## Command

Onedir archive-bound provenance:

```bash
python scripts/write_build_provenance.py \
  --output DocMergeForge-Linux-unsigned.provenance.json \
  --mode onedir \
  --artifact-label DocMergeForge-Linux-unsigned \
  --artifact DocMergeForge-Linux-unsigned.tar.gz
```

Onefile archive-bound provenance:

```bash
python scripts/write_build_provenance.py \
  --output DocMergeForge-Windows-onefile-unsigned.provenance.json \
  --mode onefile \
  --artifact-label DocMergeForge-Windows-onefile-unsigned \
  --artifact DocMergeForge-Windows-onefile-unsigned.zip
```

`--artifact` is optional for reusable/local metadata generation, but CI package workflows provide it so the provenance is bound to the exact uploaded archive.

## Recorded fields

Schema version `1` records:

- application name and DocMergeForge version;
- artifact label;
- build mode (`onedir` or `onefile`);
- explicit `signed: false` and `notarized: false` for the current unsigned build stage;
- archive filename, byte size, and SHA-256 when `--artifact` is supplied;
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

## Archive binding

When `--artifact PATH` is supplied, provenance records:

```json
{
  "artifact": {
    "archive_filename": "DocMergeForge-Linux-unsigned.tar.gz",
    "archive_size": 123456789,
    "archive_sha256": "..."
  }
}
```

The generator refuses a missing artifact path rather than producing a provenance record that pretends the archive was inspected.

The fresh-runner packaging workflows recompute the downloaded archive byte size and SHA-256 and require them to match the provenance values. The normal `.sha256` sidecar is also verified separately. This means the archive identity is checked through both provenance metadata and the checksum sidecar.

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

The generator does **not** enumerate and serialize the full environment. Signing passwords, tokens, arbitrary secrets, user environment variables, and unrelated credentials are excluded by design.

## Dependency snapshot

The provenance JSON records installed Python distributions as sorted name/version pairs. This is stronger evidence than dependency ranges in `pyproject.toml`, because PyInstaller packages the environment that was actually installed at build time.

It is still not a standards-compliant cryptographic SBOM. A future SPDX/CycloneDX or attestation pipeline can add package hashes/licenses/builder attestations when required.

## Atomic write

`write_provenance()` writes a temporary JSON file and replaces the requested path after serialization completes. This avoids leaving a partially written provenance file after an ordinary write failure.

## Privacy boundary

Provenance must never include manuscript paths/contents, PDF passwords, signing private keys/passwords, API tokens, arbitrary environment dumps, avoidable user home-directory paths, or unrelated diagnostic exports.

Unit tests inject secret-like environment values and verify they are not serialized. The CLI integration test also executes the real command wrapper and verifies archive/source identity fields.

## Unsigned versus signed provenance

The current generator describes the **unsigned build stage** and deliberately sets:

```json
{
  "signed": false,
  "notarized": false
}
```

Do not edit these values to `true` because signing is planned. A future production signing/notarization pipeline should create or extend a post-signing attestation only after signatures/notarization are actually applied and independently verified.

## Provenance versus checksum sidecar

The two evidence files have related but distinct roles:

- `.sha256` sidecar — compact checksum consumers can verify easily;
- `.provenance.json` — source/build/dependency identity plus the archive digest/size.

For release evidence, retain both. If signing/notarization/repacking changes artifact bytes, regenerate final artifact hashes/provenance appropriate to the final distribution stage.

## Local build use

Outside GitHub Actions, unavailable CI fields are recorded as `unknown` where applicable. Runtime/build fields, dependency snapshot, and optional archive binding remain useful.

For high-value local release builds, also record the source commit externally and build from a clean reviewed checkout.

## Current integration status

The generator, unit tests, command-wrapper integration test, Package Desktop integration, and Onefile Acceptance integration are implemented.

Both workflows now generate provenance beside each archive/checksum and fresh runners validate source SHA, build mode, artifact label, unsigned/notarized state, archive filename, archive byte size, and archive SHA-256 before executing the downloaded package.

The archive-bound workflow definitions are implemented; final successful run IDs should be recorded in `CHANGELOG.md` and `what_changed.md` only after all Windows/macOS/Ubuntu build and fresh-runner jobs complete successfully.

## Future production improvements

Potential additions include a standards-compliant SPDX/CycloneDX SBOM, package hashes/licenses, builder identity/artifact attestations, signing certificate identity/status, macOS notarization evidence, final download URL/hash, and reproducible-build comparison evidence.

Each addition should preserve the privacy boundary and be backed by verification rather than metadata generation alone.
