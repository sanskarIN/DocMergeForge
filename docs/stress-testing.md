# Stress and Recovery Acceptance

DocMergeForge uses layered stress/recovery testing because a fast 120-part synthetic regression, filesystem failure tests, and a multi-gigabyte publication exercise different failure modes. The project intentionally does **not** claim a workload class until a measured run at that class has completed and its evidence is recorded.

## Goals

Stress acceptance should answer whether discovery/hash/validation, PDF/DOCX composition, storage planning, cancellation, transactional publication, recovery, reporting, comparison, and resource usage remain acceptable at the claimed scale.

## Continuous automated regression

The normal test suite and 120-Part Regression workflow continuously exercise smaller deterministic fixtures. Coverage includes natural numbered discovery, Parts 1–120 validation, PDF/DOCX integration, transaction rollback/recovery, repeated cancellation cleanup, source-integrity enforcement, disk-full paths, and accessibility integration tests.

## Cross-platform controlled crash recovery

Recovery is no longer represented only by simulated journal states.

Workflow:

```text
.github/workflows/recovery-acceptance.yml
```

Name:

```text
Recovery Acceptance
```

The workflow runs a real child Python process on Windows, macOS, and Ubuntu. The child owns an `OutputTransaction` and terminates with `os._exit()` at one of three controlled promotion boundaries, bypassing normal Python context-manager cleanup:

1. after the first existing final output is moved to its rollback backup;
2. after the first new output is promoted to its final path;
3. after the last new output is promoted but before the journal can be marked `committed`.

The parent test then verifies:

- the expected abrupt exit occurred;
- a pending `promoting` journal remains;
- public recovery acquires the released OS-level output lock;
- the previous PDF/report publication is restored coherently;
- pending transaction evidence is removed after successful rollback;
- the output-directory lock can be acquired again.

Recovery Acceptance run `32022863454` passed all three crash phases on Windows, macOS, and Ubuntu.

This is real controlled process-termination acceptance on local GitHub-hosted filesystems. It does **not** simulate physical power failure, storage-controller/device removal, filesystem corruption, or multi-host network-lock behavior.

## Real Linux filesystem exhaustion

The project also has real filesystem exhaustion evidence rather than only an injected exception.

Workflow:

```text
.github/workflows/disk-full-acceptance.yml
```

Name:

```text
Disk Full Acceptance
```

On Ubuntu, the workflow mounts an isolated 32 MiB `tmpfs` under the runner temporary directory. `scripts/check_disk_full_recovery.py` has a safety guard that refuses intentional filling when the target filesystem has more than 128 MiB free. On the isolated tmpfs it:

1. writes a known previous published target;
2. enters the real `atomic_output()` path;
3. writes, flushes, and fsyncs 1 MiB chunks until the kernel returns `errno.ENOSPC`;
4. verifies the previous published target is unchanged;
5. verifies no atomic `.part` residue remains.

Corrected Disk Full Acceptance run `32023666826` passed at checkpoint `54389ad98cb0725a78d820ca58d9fe58b331ecd5`.

This proves real Linux tmpfs exhaustion behavior for the atomic-output path. It does not automatically prove NTFS, APFS, removable storage, network shares, or every Linux filesystem.

## Injected disk exhaustion still matters

Unit coverage also injects an `ENOSPC`-style write failure. Deterministic fault injection remains useful because it is fast and can target exact exception paths on every normal test run. The real tmpfs workflow complements rather than replaces those unit tests.

## Generate a scalable synthetic fixture locally

Use:

```bash
python scripts/generate_stress_fixture.py fixtures/stress \
  --parts 120 \
  --pdf-pages 5 \
  --pdf-lines-per-page 40 \
  --docx-paragraphs 50 \
  --paragraph-kib 1
```

The generator creates a valid deterministic PDF, valid deterministic DOCX, and separate companion ZIP for every part. It reports generated source bytes so acceptance records use measured size rather than a guessed “large” label.

## Useful local stress sequence

```bash
docmergeforge validate --input fixtures/stress --parts 1-120

docmergeforge project-create \
  --input fixtures/stress \
  --output-dir artifacts/stress \
  --project-file stress-project.json \
  --name "Stress Fixture" \
  --parts 1-120

docmergeforge merge --project stress-project.json --dry-run
docmergeforge merge --project stress-project.json

docmergeforge compare \
  --input fixtures/stress \
  --pdf-output artifacts/stress/Stress_Fixture_Master.pdf \
  --docx-output artifacts/stress/Stress_Fixture_Master.docx
```

Record output sizes plus elapsed/resource observations when they matter to the acceptance target.

## GitHub Actions Stress Acceptance workflow

Workflow:

```text
.github/workflows/stress.yml
```

Name:

```text
Stress Acceptance
```

The workflow supports two execution modes:

1. **automatic default baseline** — runs on `main` when the stress workflow or stress-fixture generator changes, using 120 parts, 5 PDF pages per part, 50 DOCX paragraphs per part, and 1 KiB synthetic paragraph payload;
2. **manual configurable scale** — `workflow_dispatch` retains explicit `parts`, `pdf_pages`, `docx_paragraphs`, and `paragraph_kib` inputs for intentionally larger acceptance runs.

Current environment is Ubuntu latest, Python 3.12, maximum 120-minute job timeout, with `.[dev]` installed.

Every run generates the fixture, validates numbered inputs, creates a project, runs preflight/merge/compare, writes machine-readable and Markdown measured evidence, records artifact sizes, and uploads `docmergeforge-stress-<parts>-parts` for short-term inspection.

Evidence files:

```text
Stress_Acceptance_Evidence.json
Stress_Acceptance_Evidence.md
```

They record the exact commit, workflow run, fixture parameters, measured generated source bytes, and measured output bytes before the evidence files themselves are added.

## Verified default 120-part baseline

Stress Acceptance run `32030895119` at checkpoint `ad5d8e354efefc745a454b799632359fafd29658` passed.

Profile:

| Metric | Value |
|---|---:|
| PDF parts | 120 |
| DOCX parts | 120 |
| Companion ZIPs | 120 |
| PDF pages per part | 5 |
| Total source PDF pages | 600 |
| DOCX paragraphs per part | 50 |
| Synthetic paragraph payload | 1 KiB |
| Measured generated source bytes | `9,881,006` |
| Measured output bytes before evidence files | `5,421,739` |

The run passed Parts 1–120 validation, project creation, storage/preflight checks, mixed PDF+DOCX merge, and output comparison. PDF comparison reported exactly 600 source and 600 output pages.

Uploaded workflow artifact:

```text
Artifact ID: 9288923591
Uploaded size: 4,785,305 bytes
GitHub artifact-container digest:
sha256:f552c3007dc6121f77145e9335f4ca39a7a3809bb4a97eb98c4118f2f2529189
```

This is a measured functional/resource baseline for a 120-part mixed publication. The generated source data is approximately 9.9 MB, so this run is explicitly **not** multi-gigabyte acceptance.

See [Release Evidence Ledger](release-evidence.md) for the canonical verification record.

## Current multi-gigabyte status

No measured multi-gigabyte Stress Acceptance result is currently claimed.

The workflow is now capable of running automatically at the default baseline and manually at larger configured profiles. To claim multi-gigabyte acceptance, use parameters whose **reported generated source byte total** actually reaches the intended class and record the successful evidence.

## Scaling methodology

Increase one dimension at a time so failures remain diagnosable:

1. **part-count scaling** — scanner/hash/validation/report overhead;
2. **PDF page scaling** — page append/overlay/compression/validation;
3. **DOCX paragraph scaling** — composition/structure overhead;
4. **DOCX byte-payload scaling** — ZIP/XML memory/save/reopen pressure;
5. **combined target class** — realistic release workload.

Do not jump directly to an extreme combination without knowing which dimension creates the bottleneck.

## Multi-gigabyte evidence record

Record at minimum:

```text
Date
Commit SHA
Workflow/local environment
OS/runner
Python version
parts
pdf_pages
docx_paragraphs
paragraph_kib
reported source bytes
free bytes before run
final PDF size
final DOCX size
validation result
compare result
runtime/resource observations
workflow run ID
artifact hashes
```

“120 parts” alone is not evidence of multi-gigabyte scale because each part can be tiny.

## Real-world fidelity stress corpus

Synthetic repeated text does not exercise real OOXML/PDF complexity. A privacy-safe fidelity corpus should combine large images, tables, numbering/styles, multiple sections/page geometries, headers/footers, links, fields/TOC, equations/content controls/custom XML where applicable, and PDF annotations/forms when publication requires preservation.

A stable release should have both scale stress and structural fidelity evidence.

## Cancellation stress

Test cancellation during discovery/validation, PDF append/finalization, DOCX append/finalization, report generation, and immediately before transaction promotion.

After cancellation, verify the previous final publication remains unchanged, no partial final bundle appears, ordinary staging is cleaned where safe, no unresolved journal exists unless promotion actually began, and a later fresh run succeeds.

## Remaining physical/environmental recovery tests

Controlled `os._exit()` recovery is now verified, but separate tests remain appropriate where support claims require them:

- machine/power loss during storage flush;
- storage-device disconnect;
- filesystem corruption or unavailable mount;
- SMB/NAS/cloud-mounted behavior;
- multi-host advisory locking semantics;
- Windows/macOS-specific real filesystem exhaustion.

Use only disposable or fully backed-up fixtures for destructive environmental tests.

## Network/removable-storage acceptance

If direct publication to SMB/NAS/removable/cloud-mounted filesystems is intended, test those environments explicitly. Rename/replace/locking semantics and interruption behavior can differ from local disk.

A safer operational recommendation remains: merge on local disk and copy verified final artifacts afterward unless direct-network acceptance is documented.

## Memory/resource observations

The current Stress Acceptance workflow records exact source/output sizes but does not yet publish a formal peak-memory/CPU benchmark report. Performance claims should use measured instrumentation such as peak RSS, elapsed time by stage, CPU utilization, bytes read/written, and temporary peak disk usage, tied to exact runner/hardware context.

## Stress pass criteria

A target scale run passes only when fixture generation, expected numbered validation, preflight, merge transaction, output reopen/validation, compare evidence, publication evidence, and staging cleanup all succeed and the measured bytes actually meet the claimed workload class. Real-world fidelity runs additionally require human review.

## Release evidence

Record significant successful/failed acceptance results in `what_changed.md` and [Release Evidence Ledger](release-evidence.md) without overstating what each run proves.

Good:

> “Synthetic stress run generated 3.4 GiB of source data on Ubuntu runner and completed validation/merge/compare.”

Unsupported without evidence:

> “DocMergeForge handles unlimited file sizes.”

## Acceptance categories to keep separate

- synthetic regression;
- scalable synthetic stress;
- real-world fidelity corpus;
- graceful cancellation;
- injected disk-full;
- real filesystem exhaustion;
- simulated interrupted promotion;
- controlled real process termination;
- physical/storage-disconnect recovery;
- packaged-app stress.

A stable release record should state exactly which categories were performed for each support/workload claim.
