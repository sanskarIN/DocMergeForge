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

### Documentation-link integrity

Quality run:

```text
32030103104
```

Result: PASS on Python 3.12 and 3.13 through Ruff, Black, strict mypy, repository-local Markdown link validation, and full pytest/coverage.

This is the first recorded run that proves the repository documentation-link checker itself executes successfully against the current Markdown set rather than merely existing in source.

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

## GitHub Actions generation migration

The repository uses the current Node 24-era major generations verified during this phase:

- `actions/checkout@v7`;
- `actions/setup-python@v7`;
- `actions/upload-artifact@v7`;
- `actions/download-artifact@v8`;
- `actions/dependency-review-action@v5`;
- `github/codeql-action@v4`.

Executable workflow verification:

```text
Package Desktop migration run: 32030446110
Checkpoint:                    29c6ed8a480731094bb5c629a22f889b9fd9cacd
Onefile Acceptance run:        32030487166
Checkpoint:                    24674b776216e6da73c257b30149f46605eb1b77
```

Result: both workflows passed all Windows/macOS/Ubuntu build-host and fresh-runner jobs. This verifies checkout/setup v7, artifact upload v7, artifact download v8, archive-bound provenance validation, checksum validation, extraction, and packaged mixed-document execution across both supported PyInstaller distribution modes.

Quality, Regression, Build Smoke, Recovery Acceptance, Disk Full Acceptance, Stress Acceptance, and Security workflow definitions were also migrated to their corresponding current action majors. Their individual behavior should continue to be recorded at the run level when materially relevant.

Weekly Dependabot configuration is present for GitHub Actions and pip updates. It opens reviewable update pull requests and does not auto-merge them.

## Artifact attestation evidence

### Default onedir

```text
Run:        32030972195
Checkpoint: b0e112b0fecf9b6c70fcaeffd0551222dd2ed7aa
```

Result: PASS for all Windows/macOS/Ubuntu build-host and fresh-runner jobs.

Each native archive is attested with `actions/attest@v4` using job-scoped `id-token`, `attestations`, and `artifact-metadata` write permissions. The generated GitHub Artifact Attestation is signed through GitHub/Sigstore provenance infrastructure and is bound to the exact archive bytes.

Every separate fresh runner downloads the named workflow artifact and runs:

```text
gh attestation verify <downloaded-archive> --repo sanskarIN/DocMergeForge
```

before the existing archive-bound JSON provenance validation, `.sha256` verification, extraction, and packaged mixed PDF+DOCX smoke. All three platforms passed every step.

This is cryptographic build-provenance evidence for the current **unsigned development archive**. It does not mean the Windows executable is Authenticode-signed or the macOS application is Developer ID signed/notarized; platform distribution trust remains a separate production gate.

### Optional onefile

Onefile Artifact Attestations are implemented at checkpoint `c42c3cab4083e51255d78730b613af735235494f` using the same least-privilege permissions and fresh-runner `gh attestation verify` model.

The onefile attestation workflow is **not recorded as accepted here yet**. Record its run only after all Windows/macOS/Ubuntu build-host and fresh-runner jobs complete successfully.

## Stress evidence

### Measured default 120-part baseline

```text
Run:        32030895119
Checkpoint: ad5d8e354efefc745a454b799632359fafd29658
Artifact:   9288923591
```

Result: PASS on Ubuntu for the automated default stress profile.

Measured profile and evidence:

| Metric | Value |
|---|---:|
| Numbered PDF parts | 120 |
| Numbered DOCX parts | 120 |
| Companion archives | 120 |
| PDF pages per part | 5 |
| Total source PDF pages | 600 |
| DOCX paragraphs per part | 50 |
| Synthetic paragraph payload | 1 KiB |
| Measured generated source bytes | `9,881,006` |
| Measured output bytes before evidence files | `5,421,739` |
| Uploaded workflow-artifact bytes | `4,785,305` |
| GitHub artifact-container digest | `sha256:f552c3007dc6121f77145e9335f4ca39a7a3809bb4a97eb98c4118f2f2529189` |

The run successfully completed fixture generation, Parts 1–120 PDF/DOCX validation, project creation, preflight/dry-run, mixed PDF+DOCX merge, output comparison, evidence generation, artifact-size recording, and artifact upload. PDF comparison reported 600 source pages and 600 output pages with matching page count.

The generated evidence is stored in `Stress_Acceptance_Evidence.json` and `Stress_Acceptance_Evidence.md` inside the workflow artifact.

This baseline is approximately 9.9 MB of generated source data. It is useful 120-part functional/resource evidence but is explicitly **not multi-gigabyte acceptance**.

The workflow retains configurable manual inputs for deliberately larger runs. A future scale claim must record at minimum:

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
