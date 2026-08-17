# Stress and Recovery Acceptance

DocMergeForge uses layered stress/recovery testing because a fast 120-part synthetic regression and a multi-gigabyte publication exercise different failure modes. The project intentionally does **not** claim a workload class until a measured run at that class has completed and its evidence is recorded.

## Goals

Stress acceptance should answer:

- Can discovery/hash/validation handle the target part count?
- Can PDF composition handle the target total page count/bytes?
- Can DOCX composition handle the target document count/payload/OOXML complexity?
- Is memory/runtime behavior acceptable on supported machines?
- Is preflight storage estimation operationally useful?
- Does cancellation remain responsive during long finalization stages?
- Does a failed/cancelled run leave no falsely published bundle?
- Can an interrupted promotion be recovered safely?
- Are reports/checksums/manifests generated at scale?
- Do output comparison/validation still complete?

## Continuous automated regression

The normal test suite and 120-Part Regression workflow continuously exercise smaller deterministic fixtures.

Coverage includes concepts such as:

- natural numbered discovery;
- complete Parts 1–120 validation;
- PDF/DOCX integration;
- transaction rollback/recovery;
- repeated cancellation cleanup;
- source-integrity enforcement;
- storage/disk-full injected failures;
- accessibility integration tests.

These are fast enough to run on normal development events.

## Repeated transaction recovery regression

The regression suite includes repeated cancelled publication transactions followed by a successful transaction. This is designed to detect:

- stale staging directories;
- accidental replacement of the last published bundle;
- cleanup problems accumulating across repeated runs;
- cancellation/recovery regressions.

Repeated tests matter because cleanup defects can remain invisible in a single isolated failure.

## Injected disk exhaustion

Unit coverage injects an `ENOSPC`-style write failure and checks that:

- the prior published file remains preserved;
- temporary atomic `.part` files are cleaned where safe.

This is valuable deterministic coverage but remains different from filling a real filesystem while a full multi-output transaction is active.

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

The generator creates for every part:

- a valid deterministic PDF;
- a valid deterministic DOCX;
- a companion ZIP kept separate from manuscript inputs.

It reports generated source bytes so acceptance records can use measured size instead of a guessed label such as “large.”

## Useful local sequence

After generation:

```bash
docmergeforge validate \
  --input fixtures/stress \
  --parts 1-120
```

Create project:

```bash
docmergeforge project-create \
  --input fixtures/stress \
  --output-dir artifacts/stress \
  --project-file stress-project.json \
  --name "Stress Fixture" \
  --parts 1-120
```

Preflight:

```bash
docmergeforge merge --project stress-project.json --dry-run
```

Merge:

```bash
docmergeforge merge --project stress-project.json
```

Compare:

```bash
docmergeforge compare \
  --input fixtures/stress \
  --pdf-output artifacts/stress/Stress_Fixture_Master.pdf \
  --docx-output artifacts/stress/Stress_Fixture_Master.docx
```

Record output file sizes and elapsed/resource observations if they matter to the acceptance target.

## Manual GitHub Actions workflow

Workflow:

```text
.github/workflows/stress.yml
```

Name:

```text
Manual Stress Acceptance
```

It is intentionally manual so large generated files do not make every PR/push expensive.

### Inputs

`parts`
: Number of numbered PDF/DOCX parts. Default `120`.

`pdf_pages`
: PDF pages generated per part. Default `5`.

`docx_paragraphs`
: DOCX paragraphs per part. Default `50`.

`paragraph_kib`
: Approximate deterministic payload KiB per DOCX paragraph. Default `1`.

The local fixture generator also supports `--pdf-lines-per-page`; the current GitHub workflow uses the generator default for that option.

## Workflow environment

Current manual stress job:

- Ubuntu latest GitHub runner;
- Python 3.12;
- maximum workflow timeout: 120 minutes;
- installs `.[dev]`.

A run that times out is not a successful acceptance result. Record it as a scale/resource limit for that runner configuration.

## Workflow steps

The workflow currently:

1. checks out source;
2. sets up Python/pip cache;
3. installs developer dependencies;
4. generates scalable fixture;
5. validates all numbered inputs using `1-<parts>`;
6. creates a generic `Stress Fixture` project;
7. runs project preflight;
8. merges the stress project;
9. compares PDF/DOCX outputs to source evidence;
10. runs `du -ah`/sort to record artifact sizes;
11. uploads `artifacts/stress`.

## Artifact retention

Manual stress output is uploaded as:

```text
docmergeforge-stress-<parts>-parts
```

with current retention:

```text
7 days
```

If a run is release-gate evidence, preserve its important measurements/hashes/run ID outside short-retention workflow artifacts.

## Scaling methodology

Increase one dimension at a time so failures are diagnosable.

### Stage 1 — part-count scaling

Keep each part small while increasing `parts`.

Measures:

- scanner/hash overhead;
- numbered validation performance;
- project/report index scale;
- relationship between part count and DOCX composition overhead.

### Stage 2 — PDF page scaling

Keep DOCX payload modest while increasing `pdf_pages`.

Measures:

- PDF writer page count;
- overlay/compression finalization loops;
- cancellation responsiveness;
- output validation time.

### Stage 3 — DOCX paragraph scaling

Increase `docx_paragraphs` while keeping each paragraph small.

Measures:

- document XML/paragraph composition scale;
- generated heading/page-break overhead;
- structural comparison time.

### Stage 4 — DOCX byte-payload scaling

Increase `paragraph_kib`.

Measures:

- ZIP/XML size;
- memory pressure;
- save/reopen behavior;
- hash/storage/report overhead.

### Stage 5 — combined target class

Run the intended release workload class with realistic combined values.

Do not jump straight to an extreme combination without knowing which dimension creates the bottleneck.

## Multi-gigabyte claims

To claim multi-gigabyte acceptance, record an actual run whose **generated source byte total** meets the stated scale and successfully completes the relevant workflow.

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
report/evidence sizes
validation result
compare result
runtime/resource observations
workflow run ID
artifact hashes
```

“120 parts” alone is not evidence of multi-gigabyte scale because each part can be tiny.

## Real-world fidelity stress corpus

Synthetic repeated text does not exercise real OOXML/PDF complexity.

Maintain a privacy-safe corpus containing combinations such as:

- large images;
- many tables;
- nested/complex numbering;
- many styles;
- sections with different page size/orientation;
- headers/footers;
- hyperlinks;
- footnotes/endnotes;
- fields/TOC;
- equations;
- content controls/custom XML where applicable;
- large PDF page trees;
- mixed PDF page geometries;
- annotations/forms where publication requires preservation.

A stable release should have both scale stress and structural fidelity stress evidence.

## Cancellation stress

Test cancellation at different phases:

- early discovery/validation;
- midway through PDF source append;
- PDF overlay/finalization loop;
- midway through DOCX append;
- DOCX finalization/save;
- report generation;
- immediately before final transaction promotion.

After each cancellation:

- previous final publication remains unchanged;
- no new partial final bundle appears;
- ordinary staging is cleaned where safe;
- no unresolved journal is created unless promotion actually began;
- a subsequent fresh run succeeds.

## Real abrupt-termination recovery

Automated tests simulate interrupted journal states, but release acceptance should also include real process termination on disposable data.

Example test plan:

1. create an output folder with known previous PDF/DOCX/report bundle;
2. start a sufficiently large overwrite publication;
3. terminate the process during final promotion (using controlled instrumentation/test hook if needed to make timing reproducible);
4. restart/inspect output folder;
5. confirm pending transaction detection blocks a new merge;
6. run `recover-output`;
7. verify previous bundle hashes are restored coherently;
8. rerun publication successfully.

Do this only on synthetic/backed-up fixtures.

## Real filesystem-full acceptance

A real low-space test should use a disposable filesystem/container/volume rather than risking the developer's main disk.

Verify:

- preflight blocks obviously insufficient space;
- if free space disappears after preflight, the merge fails safely;
- previous final outputs are preserved/restorable;
- transaction evidence is not lost;
- recovery succeeds after space is restored;
- no false success is reported.

## Network/removable-storage acceptance

If the product intends to support publishing directly to SMB/NAS/removable/cloud-mounted filesystems, test those explicitly.

Filesystem rename/replace/locking semantics and interruption behavior can differ from local disk.

A safer operational recommendation is to merge on local disk and copy verified final artifacts afterward unless network/filesystem acceptance is documented.

## Memory/resource observations

The current workflow records file sizes but does not automatically publish a formal memory/CPU benchmark report.

For performance claims, add measured instrumentation rather than estimating. Possible metrics:

- peak RSS;
- elapsed time by stage;
- CPU utilization;
- bytes read/written;
- temporary peak disk usage.

Performance metrics should be tied to exact hardware/runner/environment.

## Stress pass criteria

A target stress run passes only when:

- fixture generation completes;
- expected numbered validation passes;
- preflight passes;
- merge completes without timeout/uncaught failure;
- project transaction commits;
- outputs reopen/validate;
- compare evidence is reviewed/acceptable;
- publication evidence exists;
- no stale transaction directory remains;
- reported bytes meet the claimed workload class;
- human fidelity checks pass for real-world corpus runs.

## Release evidence

Add significant successful/failed acceptance results to the release-development record (`what_changed.md`) without overstating what the run proves.

Examples:

Good:

> “Synthetic stress run generated 3.4 GiB of source data on Ubuntu runner and completed validation/merge/compare.”

Not supported without evidence:

> “DocMergeForge handles unlimited file sizes.”

## Remaining acceptance distinction

Keep these separate:

- synthetic regression;
- scalable synthetic stress;
- real-world fidelity corpus;
- graceful cancellation;
- injected disk-full;
- real filesystem exhaustion;
- simulated interrupted promotion;
- real process termination;
- packaged-app stress.

A stable release should record which of these were actually performed for the supported platform/workload claims.
