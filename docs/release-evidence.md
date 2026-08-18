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

This checkpoint predates later publication-locking, packaged-artifact, provenance, documentation-link, accessibility-preference, SBOM, and native-office fidelity hardening. Use the more specific evidence below for those behaviors.

### Documentation-link integrity

Quality run:

```text
32030103104
```

Result: PASS on Python 3.12 and 3.13 through Ruff, Black, strict mypy, repository-local Markdown link validation, and full pytest/coverage.

### Current source/accessibility checkpoint

```text
Quality run:     32033541420
Build Smoke run: 32033541402
Head checkpoint: dc624e23d07e0ce94ef345245630d153ee60091a
```

Quality passed pre-commit configuration validation, Ruff, Black, strict mypy, documentation-link integrity, and full pytest on Python 3.12 and 3.13.

Build Smoke passed on Windows, macOS, and Ubuntu, including `scripts/check_accessibility.py`. The accessibility smoke verifies representative accessible metadata/shortcuts plus deterministic theme application, text-scale bounds/round-trip, and reduced-motion preference round-trip.

This is automated offscreen preference/metadata evidence. It is **not** human screen-reader, keyboard-only end-to-end, high-contrast, localization, or full accessibility acceptance.

### Final persistence and automatic-input hardening checkpoint

Current state is intentionally recorded at the **Implemented** level only until a current-head Quality/Regression/Build/Security result is observed and reviewed.

Implemented after the source/accessibility checkpoint above:

- one shared unique-temp atomic UTF-8 text writer with flush + `fsync` + atomic replacement + residue cleanup;
- atomic persistence for project JSON, application settings, recent-project history, and diagnostics exports;
- malformed application settings recovery with strict primitive-type filtering, safe enum defaults, and UI-supported numeric clamps;
- malformed recent-project history recovery that skips invalid entries rather than preventing desktop use;
- strict publication-project JSON schema/type validation, including positive part ranges and boolean validation so strings such as `"overwrite": "false"` cannot become truthy replacement behavior;
- bounded cross-platform output basenames with a 180-byte UTF-8 ceiling and deterministic digest suffix on truncation;
- broader diagnostic secret redaction for JSON-style secrets, API keys, access/refresh tokens, client secrets, and Basic/Bearer authorization values;
- fail-safe privacy-filtered stream logging when a rotating log file cannot be opened;
- removal of an unused duplicate privacy-weaker logger;
- numbered/in-range automatic manuscript selection shared by projects, SQL preset, preflight, and direct CLI merge;
- explicit reviewed `selected_files` as the only path that can intentionally include unnumbered/out-of-range special manuscript material;
- merge-aware validation that warns about excluded files while binding zero-byte/encryption blocking checks to files that can actually reach the engine;
- explicit encryption validation for selected unnumbered PDF front matter;
- strictly nested project-output subtree exclusion from future source discovery;
- resolved-path deduplication for overlapping source roots;
- preflight ordering/conflict/storage evidence aligned with the same resolved merge-input set used by publication;
- direct CLI success output bound to the engine-returned path, including versioned `_v2` destinations;
- CLI/project password prompting limited to encrypted PDFs in the resolved merge input;
- structured CLI validation/preflight diagnostics for unnumbered/out-of-range review files;
- package-version synchronization regression between `pyproject.toml` and `docmergeforge.__version__`;
- current desktop support/contact-link regression and corrected X profile link;
- ReportLab dependency range widened to `<6` after compatibility review of the current local/generated rendering path;
- removal of the stale self-writing development-record workflow with repository write permission;
- `.editorconfig`, `.gitattributes`, expanded third-party redistribution guidance, strengthened code of conduct, and GitHub support routing.

The repository contains focused regressions for these boundaries, but no older workflow run is reused as proof after these material changes. Until a new run is actually observed, this section remains **Implemented**, not **Source/acceptance CI verified**.

### Microsoft Word native fidelity implementation checkpoint

Current state is intentionally recorded at the **Implemented** level only.

Implemented after the source checkpoint above:

- Microsoft Word native multi-document acceptance prototype using ordered `Range.InsertFile(...)` and real Word section boundaries;
- exact COM-created Word process identity using PID + `WINWORD` name + process start-time fingerprint;
- exact-instance failure/timeout cleanup with PID-reuse protection and natural-exit grace handling;
- privacy-safe visible-text, section-layout/linkage, and page-number section-semantic fingerprints;
- page-number evidence for `w:start`, `w:fmt`, `w:chapStyle`, and `w:chapSep` in one global merged section sequence;
- source-revision binding before/after expected evidence, Word automation, and output evidence;
- deterministic Word smoke sources with portrait/landscape geometry, distinct margins/header/footer distances, and decimal/upper-Roman numbering restarts;
- a controlled forced-timeout cleanup harness using the same exact Word process identity boundary;
- a dedicated manual self-hosted Windows Word workflow with capability-policy and clean pre/post `WINWORD` checks; and
- expanded Ubuntu fidelity regressions for Word parser/process/acceptance boundaries while LibreOffice remains the real external application in that general Linux fidelity job.

No new run ID is recorded here for these changes. Older Quality runs are **not** reused as proof of this newer implementation.

No real controlled Microsoft Word run is recorded either. The self-hosted workflow definition is not itself acceptance evidence. `word.production_ready=false` remains required.

See [Microsoft Word Native Merge Acceptance](word-native-merge-acceptance.md) and [Microsoft Word Timeout Cleanup Acceptance](word-timeout-cleanup-acceptance.md).

### Supervised LibreOffice UNO native fidelity implementation checkpoint

Current state is also intentionally recorded at the **Implemented** level only.

Implemented at the current development head:

- one authoritative supervised POSIX Writer/UNO multi-document acceptance engine in `libreoffice_uno_merge.py`;
- a unique temporary LibreOffice user profile and unique UNO pipe for every run;
- a copied writable master so the first source is never edited in place;
- ordered Writer `insertDocumentFromURL(...)` insertion for later sources;
- an independently selected Python interpreter that must actually import the LibreOffice `uno` bridge;
- source SHA-256 binding before/after native processing and evidence construction;
- privacy-safe body paragraph/table text fingerprints plus body structure and risky-OOXML evidence;
- an explicit ordered private-manuscript acceptance command with no-overwrite evidence behavior;
- process supervision that polls/reaps the launcher while tracking the complete isolated POSIX process group;
- targeted `SIGTERM`→`SIGKILL` escalation only for that isolated group;
- real subprocess process-group regression coverage in a separate cleanup workflow;
- a real Ubuntu Writer multi-document acceptance workflow that installs `libreoffice-writer` and `python3-uno`; and
- removal of the earlier duplicate native LibreOffice prototype/workflow/tests so only the supervised UNO path remains maintained.

The first native Writer pass rule intentionally covers body structure/text/source revision/new-risk categories only. Section/page geometry, headers/footers, page numbering, floating objects, field behavior, advanced OOXML, and rendered equivalence remain later gates.

No passing current supervised UNO workflow ID or process-cleanup workflow ID is recorded here yet. A workflow definition is not external-application evidence. `libreoffice.production_ready=false` remains required.

See [LibreOffice Native Multi-Document Merge Acceptance](libreoffice-native-merge-acceptance.md).

### Native-office final promotion hardening

Current state: **Implemented**, awaiting current-head CI verification.

All maintained external-office adapters/prototypes now use one shared fail-closed promotion boundary. The temporary DOCX and tracked source hashes are verified before promotion and verified again immediately afterward. If the final destination fails package validation or a source revision changes in the final verification window, the newly created destination is removed rather than being left behind after the operation reports failure.

This applies to:

- LibreOffice one-document round trip;
- Microsoft Word one-document round trip;
- Microsoft Word native multi-document acceptance; and
- supervised LibreOffice UNO multi-document acceptance.

A regression specifically exercises removal of a promoted destination when final integrity verification fails.

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

Result: PASS on Windows, macOS, and Ubuntu for controlled `os._exit()` interruption after the first rollback backup, after the first new final promotion, and after the last new final promotion before journal commit.

The acceptance verifies restoration of the previous publication, safe staging/journal cleanup, and reacquisition of the OS-level output lock.

This does **not** prove physical power-loss behavior, storage-device removal, filesystem corruption, or multi-host network-filesystem locking semantics.

## Real filesystem exhaustion evidence

Disk Full Acceptance corrected run:

```text
32023666826
```

Result: PASS on Ubuntu using an isolated 32 MiB tmpfs filled until the kernel returned real `ENOSPC` through the production `atomic_output()` path. The previous published target remained unchanged and atomic `.part` residue was removed.

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

The GitHub artifact-container digest identifies the workflow artifact container. The actual platform archive carries its own `.sha256` sidecar and archive filename/size/SHA-256 inside the DocMergeForge provenance JSON.

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

Both workflows passed all Windows/macOS/Ubuntu build-host and fresh-runner jobs. Security migration run `32030403035` also passed CodeQL v4; dependency review correctly skipped on a push event.

Weekly Dependabot configuration is present for GitHub Actions and pip updates. It opens reviewable update pull requests and does not auto-merge them.

## Artifact attestation evidence

### Default onedir

```text
Run:        32030972195
Checkpoint: b0e112b0fecf9b6c70fcaeffd0551222dd2ed7aa
```

Result: PASS for all Windows/macOS/Ubuntu build-host and fresh-runner jobs.

Each archive is attested with `actions/attest@v4` using job-scoped `id-token`, `attestations`, and `artifact-metadata` write permissions. Each fresh runner verifies the downloaded archive with `gh attestation verify` before JSON provenance, checksum, extraction, and packaged smoke.

Attestation-era artifact containers:

| Platform | Artifact ID | GitHub artifact-container digest |
|---|---:|---|
| Windows | `9288984074` | `sha256:a169001b7c76777acc6c30f246498b50c8a735c0fafca9657f7738d50f330ed1` |
| macOS | `9288934609` | `sha256:e5aff9fc17eec544e395947afe553d5732b8e2af7de9fbfa78ff095a5d92d7f2` |
| Linux | `9289011135` | `sha256:2e560f8fb8e3869320c998d3967890b8b22d51c98b7cd308e1063af124662008` |

### Optional onefile

```text
Run:        32031798935
Checkpoint: c42c3cab4083e51255d78730b613af735235494f
```

Result: PASS for all Windows/macOS/Ubuntu build-host and fresh-runner jobs using the same least-privilege attestation and fresh-runner verification model.

Attestation-era onefile artifact containers:

| Platform | Artifact ID | GitHub artifact-container digest |
|---|---:|---|
| Windows | `9289300227` | `sha256:58c0b60c67599181463c33f6efb5e77c86fdd29dbf8f98f3c4af3f91ee28867e` |
| macOS | `9289251930` | `sha256:ac3e41a5e85891d095053e7d0be5c75a519502c8d0100ea61bfa7614b836cab1` |
| Linux | `9289257661` | `sha256:d698e261487e756adf5eabbb4e169e99467d16842753a1a0f56341fdd02c1b3b` |

A GitHub/Sigstore build-provenance attestation does **not** make the Windows executable Authenticode-signed or the macOS application Developer ID signed/notarized. Platform distribution trust remains a separate production gate.

## CycloneDX SBOM attestation evidence

CycloneDX generator version is pinned in the build extra as `cyclonedx-bom==7.3.1`. Packaging uses `cyclonedx-py environment` to produce validated CycloneDX 1.6 JSON from the exact Python build environment used for PyInstaller.

This is a **build-environment dependency SBOM**. It can include packaging/build dependencies and should not be represented as a byte-perfect inventory of every component embedded in the final PyInstaller executable.

Each archive receives a second `actions/attest@v4` predicate using its generated SBOM. Fresh runners require the specific CycloneDX predicate independently:

```text
gh attestation verify <downloaded-archive> \
  --repo sanskarIN/DocMergeForge \
  --predicate-type https://cyclonedx.org/bom
```

### Onedir SBOM acceptance

```text
Run:        32033135355
Checkpoint: 59dc14bbf1d4301177e475ac350694bdd9d90ada
```

Result: PASS for all three build-host and all three fresh-runner jobs. Every platform generated the CycloneDX JSON, created both default build-provenance and CycloneDX SBOM attestations, uploaded archive/checksum/provenance/SBOM, then independently verified both predicates before normal provenance/checksum/extract/smoke.

SBOM-era artifact containers:

| Platform | Artifact ID | GitHub artifact-container digest |
|---|---:|---|
| Windows | `9289721065` | `sha256:f00410bd8016ca05243a0be114dbe3ab336529f7a2b2251968b42922cc67e37d` |
| macOS | `9289679866` | `sha256:c9ffec38d0c70b50e24bbd54e74c29d69b52206540b1402c9a76cbf535e54539` |
| Linux | `9289686689` | `sha256:30b851a609ae3394174015f4f80fce52b356069131395978039c5ad82122a143` |

### Onefile SBOM acceptance

```text
Run:        32033541414
Checkpoint: dc624e23d07e0ce94ef345245630d153ee60091a
```

Result: PASS for all three build-host and all three fresh-runner jobs with the same two-predicate verification model.

SBOM-era onefile artifact containers:

| Platform | Artifact ID | GitHub artifact-container digest |
|---|---:|---|
| Windows | `9289869031` | `sha256:23082e8dce64e5225aa8234d0054f1c7c731dacd9810816a7d7a499759b5ebb6` |
| macOS | `9289825286` | `sha256:474cc73883e67fd0bbc074ef3fdbccd9de709a8a5f1a220582c53a25c662c35c` |
| Linux | `9289846554` | `sha256:44aba02321c0c09103987b1dc18eea5553ba16b00162ca9fed3af4420835bbda` |

Both supported PyInstaller modes therefore have archive checksums, privacy-safe archive-bound JSON provenance, signed SLSA-style GitHub/Sigstore build provenance, CycloneDX build-environment dependency SBOMs, signed SBOM predicates, and independent fresh-runner verification of the downloaded bytes before packaged mixed-document execution.

## Stress evidence

### Measured default 120-part baseline

```text
Run:        32030895119
Checkpoint: ad5d8e354efefc745a454b799632359fafd29658
Artifact:   9288923591
```

Result: PASS on Ubuntu for the automated default stress profile with 120 PDF + 120 DOCX parts, 600 total source PDF pages, 50 DOCX paragraphs per part, 1 KiB paragraph payload, `9,881,006` generated source bytes, and `5,421,739` output bytes before evidence files.

Artifact container digest: `sha256:f552c3007dc6121f77145e9335f4ca39a7a3809bb4a97eb98c4118f2f2529189`.

### Formatter-clean merge resource telemetry

```text
Run:        32032403859
Checkpoint: 73a79a763ef7c363964b1808ddb9e3156785e2f9
Artifact:   9289427729
```

Result: PASS through generation, Parts 1–120 validation, preflight, measured mixed merge, comparison, evidence generation, and upload.

Measured merge telemetry:

| Metric | Value |
|---|---:|
| Generated source bytes | `9,881,006` |
| Output bytes before acceptance evidence | `5,422,356` |
| Elapsed seconds | `16.744248664` |
| User CPU seconds | `16.562235` |
| System CPU seconds | `0.17077` |
| Peak RSS | `169,193,472` bytes (~161.4 MiB) |
| Minor page faults | `39,178` |
| Major page faults | `1` |
| Filesystem input blocks | `536` |
| Filesystem output blocks | `10,704` |
| Disk free before merge | `91,322,392,576` bytes |
| Disk free after merge | `91,317,059,584` bytes |
| Free-space delta | `5,332,992` bytes |

Workflow-artifact size was `4,786,316` bytes with container digest `sha256:3bed43be22932c470e062aaf2b7e38fcfeeb168e4c3ff90aa9f0da0c314454c8`.

The telemetry runner records privacy-safe counters and does not serialize the full command arguments or environment. These measurements describe this exact synthetic profile and runner execution and are not universal performance guarantees.

The verified stress source is approximately 9.9 MB, so this evidence remains explicitly **not multi-gigabyte acceptance**.

## Production gates still open

The following are intentionally **not** marked complete by the evidence above:

- a current-head Quality/Regression/Build/Security checkpoint for the final persistence/input-safety hardening;
- human interactive clean-machine acceptance on representative Windows/macOS/Linux systems;
- representative real-world PDF/DOCX fidelity review in intended viewers/editors;
- human keyboard-only and real screen-reader accessibility acceptance;
- real OS high-contrast/display-scaling/localization acceptance;
- measured multi-gigabyte stress/resource acceptance;
- Windows production signing and SmartScreen/trust review when distributed;
- macOS Developer ID signing, hardened-runtime review where required, notarization, stapling, and Gatekeeper verification when distributed;
- acceptance of any MSI/MSIX/Inno/NSIS/DMG/PKG/AppImage/DEB/RPM or other installer/container that may later be distributed;
- final post-signing/post-notarization distribution hashes;
- physical power-loss/storage-disconnect recovery acceptance;
- network/shared-filesystem multi-host lock semantics;
- current-head supervised LibreOffice UNO multi-document workflow evidence and process-cleanup workflow evidence;
- representative private LibreOffice multi-document corpora, expanded section/page-layout fidelity, target-version coverage, and human interoperability review;
- real controlled Microsoft Word native normal and forced-timeout acceptance;
- representative private multi-document Word corpus plus manual rendering/behavior review;
- production-ready Microsoft Word or LibreOffice high-fidelity modes;
- exact post-PyInstaller binary-component SBOM/content inventory if that stronger claim is required;
- stable `v1.0.0` acceptance.

## Evidence maintenance rules

When a behavior materially changes, do not reuse an older run as proof for the changed behavior. Add a new checkpoint and run ID.

Keep source-level CI evidence, downloaded-artifact evidence, external-application measured evidence, and human/production acceptance separate. For executable releases, retain the exact final archive hash, provenance/attestation/SBOM evidence, signing/notarization evidence where applicable, release download identity, and human acceptance record together.
