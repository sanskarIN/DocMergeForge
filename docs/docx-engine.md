# DOCX Engine

DOCX is an OOXML ZIP package rather than a flat text format. DocMergeForge's current production-supported DOCX merge path uses `python-docx` and `docxcompose`, plus package-level analysis/validation, to compose ordered Word documents while surfacing fidelity risks instead of claiming universal perfect preservation.

External-office work is intentionally separated from that production engine. LibreOffice and Microsoft Word each provide source-preserving one-document round-trip acceptance plus separate native multi-document **acceptance prototypes**. Neither external mode is production-enabled.

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
- supervised POSIX LibreOffice Writer/UNO multi-document acceptance with isolated profile/pipe/process-group boundaries;
- Windows PowerShell discovery for Microsoft Word COM automation;
- fail-closed native command execution with positive timeout/captured diagnostics;
- separate temporary output plus output package validation;
- shared fail-closed final promotion that removes a newly created destination if final validation/integrity fails;
- source SHA-256 protection around external processing;
- structural/content/risk evidence;
- privacy-safe representative corpus execution for round trips;
- explicit ordered private-manuscript native acceptance commands;
- Word-native section/page-number/source-revision evidence;
- exact Word process identity/cleanup safeguards; and
- independent real POSIX LibreOffice process-group cleanup regressions.

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

Neither native multi-document acceptance prototype bypasses this gate. Both are reached only through explicit acceptance tooling/scripts, not through the normal `docmergeforge docx` production path.

Inspect capability state with:

```bash
docmergeforge fidelity-capabilities
```

See [DOCX Fidelity Adapters and Acceptance](docx-fidelity-acceptance.md), [LibreOffice Native Multi-Document Merge Acceptance](libreoffice-native-merge-acceptance.md), and [Microsoft Word Native Merge Acceptance](word-native-merge-acceptance.md).

## Input order

Unless `preserve_order=True`, DOCX inputs sort by detected part number and case-insensitive filename. Saved/reviewed project `selected_files` order is preserved when requested.

Native acceptance commands take an explicit ordered source sequence and reject duplicate resolved paths.

## Empty input

An empty DOCX list raises `ValidationError`; no empty master document is accepted as success.

## Source-integrity snapshot

The production engine snapshots SHA-256 for all ordered source DOCX files before processing and verifies those hashes after writing/validating temporary output. Any changed source causes validation failure before atomic promotion.

External-office paths apply independent source checks around native automation. Word-native and supervised LibreOffice UNO acceptance additionally bind expected/output evidence to the same source revision.

All maintained external-office promotion now validates temporary output and source hashes immediately before promotion and validates final output/source hashes again immediately afterward. If the final check fails, the newly created acceptance destination is removed rather than left behind after failure.

## Input OOXML validation

Every production source DOCX is validated before composition. `ERROR`/`FATAL` package diagnostics stop the merge rather than using composition as an implicit repair mechanism.

External-office sources and outputs are likewise required to be non-empty and structurally valid OOXML before acceptance/promotion.

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

The native acceptance prototypes use separate working copies rather than writing to the original first source.

## Part headings and TOC

When enabled, DocMergeForge adds generated part headings. A TOC field can also be inserted. Word/office applications may still need to update that field after opening the final document; field presence is not proof of final displayed page-number correctness.

## Portable part page breaks

For later documents, the portable production engine can add a page break before generated part headings/source append when `start_each_part_on_new_page` is enabled. This is publication structure added by DocMergeForge.

Do not confuse portable publication page breaks with native-office acceptance. Word uses real Word section breaks between sources. The current supervised Writer/UNO prototype creates an insertion paragraph boundary and can request `PAGE_BEFORE`; its section/page-style equivalence is deliberately **not** part of the first acceptance rule.

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

External-office acceptance has native timeouts and process-cleanup boundaries rather than the production engine's cancellation contract. Complete application-level cancellation remains a certification gate before a native external-office mode could enter production.

## Atomic output

Direct production output is written through an atomic temporary path and promoted only after validation/source-integrity checks. In a full project, that path itself lives inside outer transaction staging.

External fidelity tools also write separate temporary outputs, refuse existing acceptance destinations, validate before promotion, verify sources around promotion, and remove a newly promoted destination if its final verification fails.

## Output validation

After portable `composer.save(temporary)`, the engine checks cancellation, validates the package, reopens it through `python-docx`, checks cancellation again, and verifies source hashes before atomic promotion.

Native-office output is validated through the shared external-output boundary rather than being trusted because the office application returned success.

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

## Supervised LibreOffice UNO native multi-document acceptance

The maintained Writer-native acceptance path is implemented in:

```text
src/docmergeforge/docx/libreoffice_uno_merge.py
src/docmergeforge/docx/libreoffice_uno_acceptance.py
scripts/check_libreoffice_uno_merge_smoke.py
scripts/check_libreoffice_uno_merge_acceptance.py
```

It uses a unique temporary Writer profile and UNO pipe, copies the first source into a writable master, inserts later documents in exact order through Writer's document insertion API, exports DOCX through the `Office Open XML Text` filter, and supervises only the isolated POSIX process group created for that run.

Its first measured acceptance rule currently covers:

- non-empty body paragraph count;
- body table count;
- inline-shape count;
- heading count;
- privacy-safe ordered body-paragraph text;
- privacy-safe ordered body-table-cell text;
- source revision hashes; and
- newly introduced risky OOXML categories.

It deliberately does not certify section/page geometry, headers/footers, page-number semantics, exact pagination, floating objects, advanced fields, charts/SmartArt, embedded objects, or font substitution yet.

Use the explicit private acceptance script by repeating `--input` in exact order. See [LibreOffice Native Multi-Document Merge Acceptance](libreoffice-native-merge-acceptance.md).

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

For local one-document round-trip corpus acceptance without committing manuscripts:

```bash
docmergeforge fidelity-corpus \
  --input-dir "./private-corpus" \
  --output-dir "./private-fidelity-evidence" \
  --mode libreoffice
```

The corpus runner preserves relative subdirectories, records relative source/output paths, and returns success only when every discovered file is processed and accepted. `--fail-fast` partial runs remain failed.

For native multi-document LibreOffice acceptance, use `scripts/check_libreoffice_uno_merge_acceptance.py` with repeated ordered `--input` arguments and private output/evidence paths.

Representative multi-document Word corpus work remains a separate controlled acceptance task using the native Word acceptance command/workflow.

## Project DOCX merge

A full normal project validates numbered sources, checks storage/writeability, snapshots tracked sources, creates transaction staging, invokes the **portable** DOCX engine, stages evidence, rechecks project integrity, and promotes the complete bundle together.

Neither external native acceptance prototype is inserted into this production project path.

## DOCX comparison

`docmergeforge compare` reports aggregate source/output paragraph, table, inline-shape, section, and heading counts. Generated publication structure can legitimately change counts, so comparison is evidence for review rather than exact semantic equality.

Native external-office acceptance uses separate, stricter evidence models described above.

## Known fidelity limits

Advanced constructs that can require special/manual review include macros, OLE/embedded objects, tracked changes/comments, complex fields, custom XML, equations, content controls, external relationships, theme/style inheritance, complex numbering/list restarts, linked section headers/footers, floating drawings/text boxes/charts/SmartArt, and application-specific layout behavior.

The risk scanner identifies many categories but cannot prove how every construct renders after merge or round trip.

## External adapter certification boundary

LibreOffice and Word remain `production_ready=false`.

LibreOffice now has supervised native multi-document **prototype semantics**, but production certification still requires current real workflow/process-cleanup evidence, broader section/page-layout and advanced-OOXML measurement, representative target-version corpora, application/project integration, large-document behavior, and human Writer/Word interoperability review where relevant.

Word has native multi-document **prototype semantics**, but production certification still requires real controlled Word normal and forced-timeout runs, representative real-document corpora, manual render/behavior review, exact Word/Windows version coverage, packaged-app integration where claimed, cancellation/cleanup acceptance, and regression evidence for discovered defects.

The general Ubuntu fidelity lane provides real LibreOffice one-document evidence and Word boundary regression coverage. The supervised UNO workflow is the separate real LibreOffice multi-document lane; it cannot certify Microsoft Word execution.

## Human acceptance

For production/high-value output, open the final DOCX in the intended application and inspect repair prompts, headings/TOC, styles/numbering, tables/images, section/page setup, headers/footers, page numbering, fields/equations/content controls, and representative boundaries.

For external-office acceptance, compare source and generated output in the exact application/version being claimed. Keep originals until acceptance is complete.

## Safety checklist for DOCX changes

Engine/fidelity changes should preserve tests for production-fidelity gating, package rejection, ordering, style/numbering policies, headings/page breaks/TOC, section policies, headers/footers/page numbering, relationships/media/package validity, risk detection, native timeout/error behavior, source immutability, fail-closed final promotion/no-overwrite behavior, corpus privacy/completion, supervised LibreOffice UNO insertion/process cleanup, Word section/page-number evidence, exact Word process cleanup, source-revision binding, cancellation, atomic cleanup, project recovery, and real-world fidelity where relevant.
