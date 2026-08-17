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

The fresh-runner packaging workflows recompute the downloaded archive byte size and SHA-256 and require them to match provenance. The normal `.sha256` sidecar is also verified separately. Archive identity is therefore checked through both the provenance document and checksum sidecar.

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

Unit tests inject secret-like environment values and verify they are not serialized. The CLI integration test executes the real command wrapper and verifies archive/source identity fields.

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
- `.provenance.json` — source/build/dependency identity plus archive filename/size/digest.

For release evidence, retain both. If signing/notarization/repacking changes artifact bytes, regenerate final artifact hashes/provenance appropriate to the final distribution stage.

## Local build use

Outside GitHub Actions, unavailable CI fields are recorded as `unknown` where applicable. Runtime/build fields, dependency snapshot, and optional archive binding remain useful.

For high-value local release builds, also record the source commit externally and build from a clean reviewed checkout.

## Verified onedir integration

Package Desktop run `32025126032` at checkpoint `59107192d494d76a4112cdeaa9a55f01cfe37972` passed the complete Windows/macOS/Ubuntu build and fresh-runner sequence.

Every platform:

1. built the native onedir PyInstaller application;
2. ran packaged mixed PDF+DOCX publication smoke;
3. created the archive and SHA-256 sidecar;
4. generated archive-bound provenance;
5. uploaded archive/checksum/provenance together;
6. downloaded the artifact on a separate native runner without repository checkout/project installation;
7. verified provenance source SHA, build mode, artifact label, unsigned/notarized state, archive filename, byte size, and archive SHA-256;
8. verified the checksum sidecar independently;
9. extracted and executed packaged publication smoke again.

Artifacts:

```text
Windows artifact ID: 9286905238
GitHub artifact digest: sha256:28d3303fd6a49e46b765bc2114696f152095c3edd83ddb354e36e8b6b1909b8a

macOS artifact ID: 9286908194
GitHub artifact digest: sha256:f8431c63a1630eb180f5cf671fa600e66620d8f86c84f7d8c8aeb6d257023976

Linux artifact ID: 9286879514
GitHub artifact digest: sha256:db38d4f879de226c0cc66aecdf49e408756c017ddc19e20734dda253b8e3360a
```

These GitHub artifact-container digests are additional workflow evidence; users should still verify the archive-level `.sha256` sidecar/provenance digest for the actual packaged archive inside the workflow artifact.

## Verified onefile integration

Onefile Acceptance run `32025167433` at checkpoint `b8a181b7138a1bc617766dd3e86c9ab32aade75e` passed the same archive-bound provenance and fresh-runner model for onefile on Windows/macOS/Ubuntu.

Artifacts:

```text
Windows onefile artifact ID: 9286898078
GitHub artifact digest: sha256:d29a4bff3f00e264a057bdf150f50d3100145620c8f35ee4674480bb3b883147

macOS onefile artifact ID: 9286838805
GitHub artifact digest: sha256:a005aea008217a4451d7edc653b54a019c29e3f6bbf81924e8889d7804707e84

Linux onefile artifact ID: 9286861365
GitHub artifact digest: sha256:e6231c235afc11e9e51420b87ef3a59fe00d37368950f881bb0dd79beac5cc08
```

## What this evidence proves

It proves the current unsigned onedir and onefile CI artifacts are traceable to their source/build environment, bound to exact archive bytes, independently checksum/provenance verified after upload/download, extractable, and executable through the packaged mixed-document smoke on fresh native runners.

It does **not** prove production code signing, macOS notarization, human interactive clean-machine UX, representative real-world fidelity, or stable-release readiness.

## Future production improvements

Potential additions include a standards-compliant SPDX/CycloneDX SBOM, package hashes/licenses, builder identity/artifact attestations, signing certificate identity/status, macOS notarization evidence, final download URL/hash, and reproducible-build comparison evidence.

Each addition should preserve the privacy boundary and be backed by verification rather than metadata generation alone.
