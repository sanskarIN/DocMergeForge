# DOCX Engine

DOCX is an OOXML ZIP package rather than a flat text format. DocMergeForge's current production-supported DOCX merge path uses `python-docx` and `docxcompose`, plus package-level analysis/validation, to compose ordered Word documents while surfacing fidelity risks instead of claiming universal perfect preservation.

External LibreOffice and Microsoft Word automation now exists as an explicit round-trip acceptance subsystem. That subsystem is intentionally separate from the production multi-document merge engine until native merge semantics and representative target-platform acceptance are complete.

## Responsibilities

The production DOCX merge engine handles:

- production-fidelity mode gating;
- deterministic/manual input order;
- per-input OOXML validation;
- style/numbering conflict analysis;
- portable composition with `docxcompose`;
- optional part headings/page breaks/TOC field;
- section normalization when requested;
- continuous page-numbering preparation;
- book-level headers/footers;
- cancellation through finalization;
- output package validation/reopen;
- source-integrity verification;
- atomic single-output write behavior.

A full project wraps this inside the outer multi-file publication transaction.

The separate fidelity-acceptance subsystem handles:

- LibreOffice/`soffice` detection;
- Windows PowerShell host detection for Microsoft Word COM automation;
- fail-closed native command execution with timeout/captured diagnostics;
- source-preserving one-document round trips;
- temporary-output validation before promotion;
- source SHA-256 verification before/after external processing;
- structural/risk evidence for one document;
- privacy-safe local corpus execution across representative DOCX files.

## DOCX settings

Current `DocxSettings` fields:

```text
start_each_part_on_new_page = true
preserve_sections = true
fidelity_mode = "portable"
add_part_headings = true
create_toc_field = true
style_conflict_policy = "prefer_master"
numbering_conflict_policy = "remap"
header_text = null
footer_text = null
continuous_page_numbering = true
```

Project JSON can persist these settings. Review them before production publication.

## Fidelity mode gate

Before doing document merge work, the engine calls `require_production_fidelity(settings.fidelity_mode)`.

This prevents a fidelity mode from being selected merely because an external application appears installed. A mode must be marked production-ready by the fidelity capability layer.

In the current repository:

- `portable` is available, automation-ready, and production-ready for the normal merge engine;
- `libreoffice` can become locally available/automation-ready when LibreOffice is detected, but remains `production_ready=false`;
- `word` can become locally available/automation-ready on Windows when a PowerShell host is detected, but remains `production_ready=false`; actual Word COM availability is proven only by running the adapter.

The external adapters therefore support acceptance evidence without silently replacing the portable production merge path.

Inspect the state directly with:

```bash
docmergeforge fidelity-capabilities
```

See [DOCX Fidelity Adapters and Acceptance](docx-fidelity-acceptance.md) for the certification boundary.

## Input order

Unless `preserve_order=True`, DOCX inputs sort by:

1. whether a detected part number exists;
2. numeric part number;
3. case-insensitive filename.

With a saved/reviewed project `selected_files` order, the application requests order preservation.

## Empty input

An empty DOCX list raises `ValidationError`; no empty master document is accepted as success.

## Source-integrity snapshot

The engine snapshots SHA-256 for all ordered source DOCX files before processing and verifies those hashes again after writing/validating the temporary output.

Any changed source causes a validation failure before atomic promotion.

The full application service also tracks companion/PDF sources for a broader project-integrity guarantee.

External fidelity round trips apply a second, independent source-hash check around native office automation. Their destination must be a separate path; originals are not used as in-place save targets.

## Input OOXML validation

Every source DOCX is validated before composition.

If package diagnostics contain `ERROR` or `FATAL`, the merge stops with an invalid-input error. This prevents `docxcompose` from being used as an implicit repair mechanism for structurally unacceptable source packages.

Package validation checks are documented/tested in the validation layer and include ZIP/XML/package correctness rather than only checking the `.docx` extension.

External round-trip output is also validated as a non-empty OOXML package before it can be promoted from the adapter's temporary location.

## OOXML fidelity risk review

The risk scanner is separate from basic package validity. It identifies constructs that deserve additional fidelity review, including where detected:

- macros/VBA;
- OLE/package embeddings;
- ActiveX;
- custom XML;
- comments;
- external relationships;
- tracked insertions/deletions/moves;
- content controls;
- field codes;
- Office Math;
- `altChunk` content;
- charts;
- SmartArt/diagram parts;
- markup parts skipped because they exceed the bounded risk-scan size.

Markup risk detection is namespace-aware rather than depending on a specific XML prefix or quote style.

A risk finding does not mean a document is invalid, and a clean risk list does not prove universal visual fidelity.

## Conflict analysis

Before composition, the engine detects package collisions and classifies relevant style/numbering conflicts.

### Style policy

Portable mode currently supports:

```text
prefer_master
error
```

`prefer_master` uses the first/master document as the style authority where collisions occur according to the current portable composition strategy.

`error` makes detected style collisions blocking so an operator can review them before continuing.

Other style policies are rejected in portable mode rather than silently approximated.

### Numbering policy

Portable mode currently supports:

```text
remap
error
```

`remap` allows the portable composition strategy to remap numbering identifiers where supported.

`error` makes detected numbering collisions blocking.

Unsupported policies raise validation errors.

## Master-document strategy

The first ordered DOCX becomes the master `python-docx` document.

This matters because:

- base styles/theme/section behavior can originate from the first document;
- `prefer_master` style policy is meaningful only when the intended master really is first;
- manually reviewed ordering should place the correct source first.

## Part headings

When `add_part_headings` is enabled, DocMergeForge adds a generated heading for each part.

For the first document it uses the publication helper; for later parts it adds a level-1 heading before appending the source.

Heading text combines:

```text
Part label — detected title/filename stem
```

This intentionally changes paragraph/heading counts relative to raw source sums; interpret `compare docx` evidence accordingly.

## TOC field

When `create_toc_field` is enabled, a Word table-of-contents field is inserted into the master.

Word/office applications may require the TOC field to be updated after opening the final document to calculate final page numbers/entries according to the target renderer.

Do not treat presence of the field as proof that every displayed TOC entry/page number is already recalculated by `python-docx`.

## Part page breaks

For later documents, when `start_each_part_on_new_page` is enabled, a page break is added before the generated part heading/source append.

This is publication structure added by DocMergeForge, not copied from the source.

## Composition with `docxcompose`

The engine creates:

```python
Composer(master)
```

and appends later `Document` objects in order.

`docxcompose` is used because DOCX package composition involves relationships/styles/numbering/media that cannot safely be handled by naïve XML/body concatenation.

Even so, advanced OOXML fidelity requires real acceptance testing.

## Section behavior

If `preserve_sections` is false, DocMergeForge normalizes sections to the first/master document's section model through a publication helper.

If it is true, the engine leaves section-preservation behavior to the composition/package logic as supported.

Changing this option can materially affect:

- margins;
- page size/orientation;
- headers/footers;
- page numbering;
- section breaks.

Always test the chosen policy on representative manuscripts.

## Continuous page numbering

When `continuous_page_numbering` is enabled, the publication helper adjusts section page-numbering configuration so the book is prepared for continuous numbering.

Final behavior should be inspected in the target Word/LibreOffice renderer because page layout/fields are application-resolved.

## Headers and footers

The engine applies configured book-level header/footer text after composition/section policy and before saving.

These settings can intentionally replace/standardize visible running content. Review interaction with source-specific section headers/footers.

## Progress reporting

The engine can emit progress after each input document is accepted/appended:

```text
current index
total count
source path
```

The application service exposes this as a `merging-docx` stage.

## Cancellation

Cancellation is checked:

- before input validation steps;
- while iterating sources;
- before/after conflict analysis;
- before master setup;
- before appending each later source;
- before section/page-number/header/footer finalization;
- before/after save;
- before source revalidation.

Cancellation raises `MergeCancelled("DOCX merge cancelled safely.")`.

The outer project transaction then prevents a cancelled DOCX stage from publishing a partially updated mixed-format bundle.

The external round-trip acceptance adapters have their own native-command timeout. That timeout is a fail-closed process boundary and is not currently exposed as the normal merge engine's cancellation mechanism.

## Atomic output

Direct engine output is written through an atomic temporary path, then promoted after validation/source-integrity checks.

When overwrite is false, a versioned final path can be selected.

Inside a full project, this atomic path is itself located inside the outer transaction staging directory.

External fidelity adapters similarly write to a separate temporary directory beside the requested acceptance destination, validate the produced DOCX, verify the original source hash, and only then move the copy into the requested destination. They refuse to overwrite an existing acceptance destination.

## Output validation

After `composer.save(temporary)`, the production engine:

1. checks cancellation;
2. runs package validation on the temporary `.docx`;
3. rejects any `ERROR`/`FATAL` diagnostic;
4. opens it through `python-docx.Document`;
5. checks cancellation again;
6. verifies source hashes unchanged.

Only then can the atomic-output context promote the temporary engine result.

## Conflict preflight

Project preflight calls:

```text
DocxMergeEngine.analyze_conflicts(...)
```

and reports `docx_conflict_count` before the merge.

Use this as a review signal for complex books. For high-value publications, inspect representative collisions rather than accepting a large non-zero count without understanding it.

## Direct CLI DOCX merge

```bash
docmergeforge docx \
  --input "./Book" \
  --parts 1-120 \
  --output "./Master/Book.docx"
```

The CLI validates numbered completeness before calling the engine with default portable settings.

Direct mode does not generate the full project evidence bundle and does not silently select LibreOffice/Word.

## External-office one-document acceptance

Run LibreOffice acceptance on one representative document:

```bash
docmergeforge fidelity-roundtrip \
  --input "./samples/representative.docx" \
  --output "./evidence/representative-libreoffice.docx" \
  --mode libreoffice
```

On Windows with Microsoft Word actually installed:

```powershell
docmergeforge fidelity-roundtrip `
  --input ".\samples\representative.docx" `
  --output ".\evidence\representative-word.docx" `
  --mode word
```

The evidence records source/output hashes, structural snapshots, source/output risk categories, newly introduced risks, and overall measured acceptance.

Passing this command is not a multi-document merge certification.

## Private representative corpus acceptance

For local real-world acceptance without committing manuscripts to the repository:

```bash
docmergeforge fidelity-corpus \
  --input-dir "./private-corpus" \
  --output-dir "./private-fidelity-evidence" \
  --mode libreoffice
```

The corpus runner preserves relative subdirectories below `roundtrip/`, records a JSON report with relative source/output paths, and returns success only when every discovered file is processed and accepted. `--fail-fast` partial runs remain failed rather than appearing complete.

See [Private DOCX Fidelity Corpus Testing](docx-fidelity-corpus.md).

## Project DOCX merge

A full project:

1. validates the DOCX numbered set;
2. checks storage/writeability;
3. snapshots tracked project sources;
4. creates transaction staging path;
5. invokes the portable DOCX engine;
6. stages reports/manifest/checksums/index/checklist;
7. rechecks project source integrity;
8. promotes the complete bundle together.

If PDF was staged first and DOCX fails, the staged PDF is not promoted as a new final publication.

## DOCX comparison

After publication:

```bash
docmergeforge compare --input "./Book" --docx-output "./Master/Book.docx"
```

Comparison reports aggregate source/output counts for:

- paragraphs;
- tables;
- inline shapes;
- sections;
- headings.

Generated headings/page structure can legitimately change counts, so comparison is evidence for review rather than exact semantic equality.

The same structural dimensions are used by current external-office round-trip acceptance. They are intentionally narrower than pixel-perfect/rendered-page equivalence.

## Known fidelity limits

Advanced constructs that may require special/manual review or future certified native multi-document adapter handling include:

- macros/legacy macro-enabled packages;
- OLE/embedded objects;
- tracked changes/comments behavior;
- complex fields;
- custom XML;
- equations;
- content controls;
- unusual external relationships;
- theme/style inheritance edge cases;
- complex numbering/list restarts;
- section-linked headers/footers;
- floating drawings/text boxes/charts/SmartArt;
- application-specific rendering/layout behavior.

The risk scanner identifies many of these categories but does not prove how every construct renders after a merge or external round trip.

## External adapter certification boundary

LibreOffice and Word remain `production_ready=false` until all required external-adapter release gates are satisfied. Those gates include at least:

- complete true multi-document merge semantics in the target application;
- deterministic source-preserving behavior;
- cleanup/timeout/cancellation failure handling;
- representative corpus automation;
- target operating-system and office-suite version coverage;
- manual render/behavior review;
- regression tests for discovered defects;
- packaged-app acceptance where that external mode is claimed;
- release evidence tied to exact commits/tool versions.

The Ubuntu LibreOffice Actions lane provides useful real external-process smoke evidence once a run passes, but it cannot certify Microsoft Word or every LibreOffice platform/version.

## Human acceptance

For production/high-value output, open the final DOCX in the intended application and inspect:

- repair prompts (there should be none);
- headings/TOC;
- styles/numbering;
- tables/images;
- section/page setup;
- headers/footers;
- page numbering;
- fields/equations/content controls;
- first/last/part boundaries.

For external-adapter acceptance, also compare the source and generated round-trip/merged output in the exact application/version being claimed.

Keep originals until acceptance is complete.

## Safety checklist for DOCX changes

Engine/fidelity changes should preserve tests for:

- production-fidelity gating;
- input package rejection;
- automatic/manual ordering;
- style/numbering policies;
- headings/page breaks/TOC;
- section policies;
- headers/footers/page numbering;
- relationship/media/package validity;
- namespace-aware fidelity risk detection;
- native command timeout/error handling;
- external-adapter source immutability;
- external-adapter output validation/no-overwrite behavior;
- corpus completion/privacy accounting;
- cancellation through production finalization;
- source-integrity changes;
- atomic cleanup;
- project transaction rollback/recovery;
- real-world fidelity corpus where relevant.
