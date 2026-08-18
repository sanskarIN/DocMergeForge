# DOCX Engine

DOCX is an OOXML ZIP package rather than a flat text format. DocMergeForge's current production-supported DOCX merge path uses `python-docx` and `docxcompose`, plus package-level analysis/validation, to compose ordered Word documents while surfacing fidelity risks instead of claiming universal perfect preservation.

External-office work is intentionally separated from that production engine. LibreOffice currently provides source-preserving round-trip acceptance. Microsoft Word provides both source-preserving round-trip acceptance and a separate native multi-document **acceptance prototype**. Neither external mode is production-enabled.

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

The external fidelity subsystem handles:

- LibreOffice/`soffice` detection and source-preserving one-document round trips;
- Windows PowerShell discovery for Microsoft Word COM automation;
- fail-closed native command execution with positive timeout/captured diagnostics;
- separate temporary output plus output package validation;
- source SHA-256 protection around external processing;
- structural/content/risk evidence;
- privacy-safe representative corpus execution for round trips;
- a separate Word-native multi-document acceptance prototype;
- Word-native section/page-number/source-revision evidence; and
- exact Word process identity/cleanup safeguards.

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

Before doing normal document merge work, the engine calls `require_production_fidelity(settings.fidelity_mode)`.

This prevents a fidelity mode from being selected merely because an external application appears installed. A mode must be explicitly production-ready.

Current state:

- `portable` is available, automation-ready, and production-ready for the normal merge engine;
- `libreoffice` may be locally available/automation-ready but remains `production_ready=false`;
- `word` may be locally available/automation-ready on Windows but remains `production_ready=false`.

Microsoft Word's native multi-document acceptance prototype does **not** bypass this gate. It is reached only through explicit acceptance tooling/scripts, not through the normal `docmergeforge docx` production path.

Inspect capability state with:

```bash
docmergeforge fidelity-capabilities
```

See [DOCX Fidelity Adapters and Acceptance](docx-fidelity-acceptance.md) and [Microsoft Word Native Merge Acceptance](word-native-merge-acceptance.md).

## Input order

Unless `preserve_order=True`, DOCX inputs sort by detected part number and case-insensitive filename. Saved/reviewed project `selected_files` order is preserved when requested.

## Empty input

An empty DOCX list raises `ValidationError`; no empty master document is accepted as success.

## Source-integrity snapshot

The production engine snapshots SHA-256 for all ordered source DOCX files before processing and verifies those hashes after writing/validating temporary output. Any changed source causes validation failure before atomic promotion.

External round trips apply independent source checks around native office automation. Word-native multi-document acceptance strengthens this further by capturing source hashes before expected evidence construction and rechecking them after expected evidence, after Word execution, and after output evidence.

## Input OOXML validation

Every production source DOCX is validated before composition. `ERROR`/`FATAL` package diagnostics stop the merge rather than using composition as an implicit repair mechanism.

External-office outputs are likewise required to be non-empty and structurally valid OOXML before acceptance/promotion.

## OOXML fidelity risk review

The risk scanner is separate from basic package validity. It identifies constructs that deserve additional fidelity review, including macros/VBA, OLE/package embeddings, ActiveX, custom XML, comments, external relationships, tracked changes/moves, content controls, fields, Office Math, `altChunk`, charts, SmartArt/diagram parts, and oversized XML parts skipped by the bounded scanner.

A risk finding does not mean the document is invalid, and a clean risk list does not prove universal visual fidelity.

## Conflict analysis

Portable mode analyzes package collisions and relevant style/numbering conflicts.

### Style policy

```text
prefer_master
error
```

`prefer_master` uses the first/master document as the style authority where collisions occur according to the current portable strategy. `error` makes detected style collisions blocking.

### Numbering policy

```text
remap
error
```

`remap` allows supported numbering-ID remapping; `error` blocks detected numbering collisions.

Unsupported policies raise validation errors instead of being silently approximated.

## Master-document strategy

The first ordered DOCX becomes the portable master `python-docx` document. Base styles/theme/section behavior can therefore originate from the first document, and the intended master must be placed first.

## Part headings and TOC

When enabled, DocMergeForge adds generated part headings. A TOC field can also be inserted. Word/office applications may still need to update that field after opening the final document; field presence is not proof of final displayed page-number correctness.

## Portable part page breaks

For later documents, the portable production engine can add a page break before generated part headings/source append when `start_each_part_on_new_page` is enabled. This is publication structure added by DocMergeForge.

Do not confuse that portable publication page-break behavior with the Word-native acceptance prototype: the Word prototype uses **real Word section breaks** between source documents so section-specific properties have an explicit boundary.

## Composition with `docxcompose`

The portable engine creates `Composer(master)` and appends later `Document` objects in order. `docxcompose` is used because DOCX relationships/styles/numbering/media cannot safely be handled by naïve XML/body concatenation.

Advanced OOXML fidelity still requires real acceptance testing.

## Portable section behavior

If `preserve_sections` is false, the portable engine normalizes sections to the first/master section model through publication helpers. If true, section preservation is left to the supported composition/package behavior.

This setting can materially affect margins, page size/orientation, headers/footers, page numbering, and section breaks.

## Continuous page numbering

When `continuous_page_numbering` is enabled, publication helpers prepare section numbering for continuity. Final behavior should be inspected in the target renderer because page layout/fields are application-resolved.

## Headers and footers

Configured book-level header/footer text is applied after composition/section policy and before saving. These settings can intentionally replace/standardize source running content.

## Progress and cancellation

The portable engine can emit progress for each accepted/appended source. Cancellation is checked through validation, conflict analysis, master setup, append/finalization/save/source revalidation and raises `MergeCancelled("DOCX merge cancelled safely.")`.

The outer transaction prevents cancelled DOCX work from partially publishing a mixed-format bundle.

External-office acceptance has its own native command timeout. Word-native acceptance additionally has exact Word-process cleanup logic; this remains separate from normal portable-engine cancellation.

## Atomic output

Direct production output is written through an atomic temporary path and promoted only after validation/source-integrity checks. In a full project, that path itself lives inside outer transaction staging.

External fidelity tools also write separate temporary outputs and refuse to overwrite existing acceptance destinations.

## Output validation

After portable `composer.save(temporary)`, the engine checks cancellation, validates the package, reopens it through `python-docx`, checks cancellation again, and verifies source hashes before atomic promotion.

## Conflict preflight

Project preflight calls `DocxMergeEngine.analyze_conflicts(...)` and reports `docx_conflict_count` before merge. Treat non-zero counts as review signals for complex books.

## Direct CLI DOCX merge

```bash
docmergeforge docx \
  --input "./Book" \
  --parts 1-120 \
  --output "./Master/Book.docx"
```

Direct mode validates numbered completeness and calls the normal portable engine. It does not silently select LibreOffice or Word.

## External-office one-document acceptance

LibreOffice example:

```bash
docmergeforge fidelity-roundtrip \
  --input "./samples/representative.docx" \
  --output "./evidence/representative-libreoffice.docx" \
  --mode libreoffice
```

Microsoft Word example on Windows with Word actually installed:

```powershell
docmergeforge fidelity-roundtrip `
  --input ".\samples\representative.docx" `
  --output ".\evidence\representative-word.docx" `
  --mode word
```

Passing one-document round-trip evidence is not multi-document certification.

## Microsoft Word native multi-document acceptance

The explicit Word acceptance prototype is implemented in:

```text
src/docmergeforge/docx/word_merge.py
src/docmergeforge/docx/word_merge_acceptance.py
src/docmergeforge/docx/section_evidence.py
src/docmergeforge/docx/word_process.py
```

It uses ordered `Range.InsertFile(...)` plus `wdSectionBreakNextPage` or `wdSectionBreakContinuous`, writes a separate validated output, and measures:

- aggregate structure;
- privacy-safe body/table/header/footer visible text;
- ordered section start/layout/header-footer linkage;
- ordered page-number section semantics (`w:start`, `w:fmt`, `w:chapStyle`, `w:chapSep`);
- source revision hashes; and
- risky OOXML categories.

Page-number and section fingerprints use a **global merged section sequence**, not source-document indices, so multiple source documents can compare correctly with one output document while order remains significant.

The Word merge records the exact COM-created Word process as PID + `WINWORD` name + process start-time fingerprint. Failure/timeout cleanup may terminate only that still-matching process; unrelated Word processes are not broad-killed. If nominal success still requires forced Word termination, the merge is rejected.

The deterministic Word smoke uses different portrait/landscape geometry, margins/header/footer distances, and page-number restart/format rules so those signals are actually exercised.

See [Microsoft Word Native Merge Acceptance](word-native-merge-acceptance.md) for the controlled self-hosted workflow and remaining gates.

## Private representative corpus acceptance

For local round-trip corpus acceptance without committing manuscripts:

```bash
docmergeforge fidelity-corpus \
  --input-dir "./private-corpus" \
  --output-dir "./private-fidelity-evidence" \
  --mode libreoffice
```

The corpus runner preserves relative subdirectories, records relative source/output paths, and returns success only when every discovered file is processed and accepted. `--fail-fast` partial runs remain failed.

Representative multi-document Word corpus work remains a separate controlled acceptance task using the native Word acceptance command/workflow.

## Project DOCX merge

A full normal project validates numbered sources, checks storage/writeability, snapshots tracked sources, creates transaction staging, invokes the **portable** DOCX engine, stages evidence, rechecks project integrity, and promotes the complete bundle together.

The Word native acceptance prototype is not inserted into this production project path.

## DOCX comparison

`docmergeforge compare` reports aggregate source/output paragraph, table, inline-shape, section, and heading counts. Generated publication structure can legitimately change counts, so comparison is evidence for review rather than exact semantic equality.

Word-native acceptance uses a separate stricter evidence model described above.

## Known fidelity limits

Advanced constructs that can require special/manual review include macros, OLE/embedded objects, tracked changes/comments, complex fields, custom XML, equations, content controls, external relationships, theme/style inheritance, complex numbering/list restarts, linked section headers/footers, floating drawings/text boxes/charts/SmartArt, and application-specific layout behavior.

The risk scanner identifies many categories but cannot prove how every construct renders after merge or round trip.

## External adapter certification boundary

LibreOffice and Word remain `production_ready=false`.

LibreOffice still requires complete native multi-document semantics plus representative target-platform acceptance before any native production claim.

Word now has multi-document **prototype semantics**, but production certification still requires real controlled Word normal and forced-timeout runs, representative real-document corpora, manual render/behavior review, exact Word/Windows version coverage, packaged-app integration where claimed, cancellation/cleanup acceptance, and regression evidence for discovered defects.

The Ubuntu fidelity lane provides real LibreOffice Writer evidence and Word boundary regression coverage; it cannot certify Microsoft Word execution.

## Human acceptance

For production/high-value output, open the final DOCX in the intended application and inspect repair prompts, headings/TOC, styles/numbering, tables/images, section/page setup, headers/footers, page numbering, fields/equations/content controls, and representative boundaries.

For external-office acceptance, compare source and generated output in the exact application/version being claimed. Keep originals until acceptance is complete.

## Safety checklist for DOCX changes

Engine/fidelity changes should preserve tests for production-fidelity gating, package rejection, ordering, style/numbering policies, headings/page breaks/TOC, section policies, headers/footers/page numbering, relationships/media/package validity, risk detection, native timeout/error behavior, source immutability, output validation/no-overwrite behavior, corpus privacy/completion, Word section/page-number evidence, exact Word process cleanup, source-revision binding, cancellation, atomic cleanup, project recovery, and real-world fidelity where relevant.
