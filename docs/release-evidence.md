# Release Evidence Ledger

This ledger records concrete DocMergeForge verification evidence. It is intentionally conservative: a feature is not marked production-accepted merely because it is implemented or because a related CI workflow passed.

For release policy and required human/production gates, see [Release Process](release-process.md), [Testing and CI](testing-and-ci.md), [Executable Verification](build/verification.md), and [Known Limitations](known-limitations.md).

## Evidence levels

- **Implemented** — code exists in the repository.
- **Source/acceptance CI verified** — the named source, integration, or acceptance workflow passed for the stated checkpoint.
- **Downloaded-artifact verified** — an uploaded package was consumed on a separate native runner without source checkout/project installation, its evidence was verified, and packaged smoke passed.
- **Human/production accepted** — representative end-user, fidelity, accessibility, signing/notarization, installer, and distribution expectations have been intentionally accepted.

Do not infer a higher level from a lower one.

## Core quality and regression evidence

### Hardening checkpoint

Checkpoint:

```text
82fe37725a2ae4e71678903c4d67fdff40d819e4
```

Verified runs:

| Gate | Run | Result |
|---|---:|---|
| Quality | `32014319266` | PASS on Python 3.12 and 3.13 |
| 120-Part Regression | `32014319264` | PASS |
| Build Smoke | `32014319394` | PASS on Windows/macOS/Ubuntu |
| Security / CodeQL | `32014319291` | PASS |

This checkpoint predates later publication-locking, packaged-artifact, provenance, and documentation-link hardening. Use the more specific evidence below for those behaviors.

## Publication locking and recovery evidence

### Cross-process output exclusion

Checkpoint:

```text
4785dc8386b92921be2117e5eb5f0b7f9aadce2a
```

Verified runs:

| Gate | Run | Result |
|---|---:|---|
| Quality | `32022625007` | PASS |
| 120-Part Regression | `32022625013` | PASS |
| Build Smoke | `32022625036` | PASS |
| Security / CodeQL | `32022625128` | PASS |

### Abrupt process termination

Recovery Acceptance run:

```text
32022863454
```

Result: PASS on Windows, macOS, and Ubuntu for controlled `os._exit()` interruption at all three accepted promotion phases:

1. after the first rollback backup;
2. after the first new final file is promoted;
3. after the last new final file is promoted but before the journal is marked committed.

The acceptance verifies restoration of the previous publication, staging/journal cleanup where safe, and reacquisition of the OS-level output lock.

This does **not** prove physical power-loss behavior, storage-device removal, filesystem corruption, or multi-host network-filesystem locking semantics.

## Real filesystem exhaustion evidence

Disk Full Acceptance corrected run:

```text
32023666826
```

Result: PASS on Ubuntu using an isolated 32 MiB tmpfs filled until the kernel returned real `ENOSPC` through the production `atomic_output()` path.

Verified properties include preservation of the previous published target and cleanup of atomic `.part` residue.

This is Linux/tmpfs evidence. It is not automatically NTFS, APFS, removable-storage, or network-filesystem acceptance.

## Default onedir executable evidence

Archive-bound Package Desktop run:

```text
Run:        32025126032
Checkpoint: 59107192d494d76a4112cdeaa9a55f01cfe37972
```

Result: PASS for all Windows/macOS/Ubuntu build-host and fresh-runner jobs.

Each platform completed native PyInstaller build, packaged mixed PDF+DOCX smoke, archive creation, SHA-256 sidecar generation, privacy-safe archive-bound provenance generation, artifact upload, separate native-runner download, provenance validation, checksum validation, extraction, and packaged mixed PDF+DOCX smoke again.

GitHub Actions artifact-container evidence:

| Platform | Artifact ID | GitHub artifact-container digest |
|---|---:|---|
| Windows | `9286905238` | `sha256:28d3303fd6a49e46b765bc2114696f152095c3edd83ddb354e36e8b6b1909b8a` |
| macOS | `9286908194` | `sha256:f8431c63a1630eb180f5cf671fa600e66620d8f86c84f7d8c8aeb6d257023976` |
| Linux | `9286879514` | `sha256:db38d4f879de226c0cc66aecdf49e408756c017ddc19e20734dda253b8e3360a` |

The GitHub artifact-container digest identifies the workflow artifact container. The actual platform archive also carries its own `.sha256` sidecar and its archive filename/size/SHA-256 inside the provenance JSON. Do not substitute the container digest for the inner archive digest in a production release record.

## Optional onefile executable evidence

Archive-bound Onefile Acceptance run:

```text
Run:        32025167433
Checkpoint: b8a181b7138a1bc617766dd3e86c9ab32aade75e
```

Result: PASS for all Windows/macOS/Ubuntu build-host and fresh-runner jobs.

GitHub Actions artifact-container evidence:

| Platform | Artifact ID | GitHub artifact-container digest |
|---|---:|---|
| Windows | `9286898078` | `sha256:d29a4bff3f00e264a057bdf150f50d3100145620c8f35ee4674480bb3b883147` |
| macOS | `9286838805` | `sha256:a005aea008217a4451d7edc653b54a019c29e3f6bbf81924e8889d7804707e84` |
| Linux | `9286861365` | `sha256:e6231c235afc11e9e51420b87ef3a59fe00d37368950f881bb0dd79beac5cc08` |

As with onedir, the inner onefile archive has a separate checksum sidecar and archive-bound provenance record.

## Current workflow-generation migration

The repository is migrating GitHub Actions to the current Node 24-era major generations:

- `actions/checkout@v7`;
- `actions/setup-python@v7`;
- `actions/upload-artifact@v7`;
- `actions/download-artifact@v8`;
- `actions/dependency-review-action@v5`;
- `github/codeql-action@v4`.

Do not treat this migration as verified in this ledger until the corresponding current-head workflows complete successfully. Record the final checkpoint/run IDs here after that evidence exists.

## Stress evidence

The repository includes a configurable manual Stress Acceptance workflow, but this ledger does **not** currently record a measured multi-gigabyte successful run.

A future scale claim must record at minimum:

```text
checkpoint
workflow run ID
fixture parameters
measured generated source bytes
measured output bytes
validation result
merge result
comparison result
resource observations
```

Do not label a run “multi-gigabyte” unless measured source bytes actually reach that class.

## Production gates still open

The following are intentionally **not** marked complete by the evidence above:

- human interactive clean-machine acceptance on representative Windows/macOS/Linux systems;
- representative real-world PDF/DOCX fidelity review in intended viewers/editors;
- human keyboard-only and real screen-reader accessibility acceptance;
- measured multi-gigabyte stress/resource acceptance;
- Windows production signing and SmartScreen/trust review when distributed;
- macOS Developer ID signing, hardened-runtime review where required, notarization, stapling, and Gatekeeper verification when distributed;
- acceptance of any MSI/MSIX/Inno/NSIS/DMG/PKG/AppImage/DEB/RPM or other installer/container that may later be distributed;
- final post-signing/post-notarization distribution hashes;
- physical power-loss/storage-disconnect recovery acceptance;
- network/shared-filesystem multi-host lock semantics;
- production-ready Microsoft Word or LibreOffice high-fidelity adapters;
- stable `v1.0.0` acceptance.

## Evidence maintenance rules

When a behavior materially changes, do not reuse an older run as proof for the changed behavior. Add a new checkpoint and run ID.

Keep source-level CI evidence, downloaded-artifact evidence, and human/production acceptance separate. For executable releases, retain the exact final archive hash, provenance/attestation, signing/notarization evidence where applicable, release download identity, and human acceptance record together.
