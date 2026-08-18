# LibreOffice Native Multi-Document Merge Acceptance

DocMergeForge includes a separate, supervised LibreOffice Writer UNO multi-document merge **acceptance prototype**. It is intentionally not connected to the normal production DOCX engine and it does not make `libreoffice` production-ready.

The goal is to measure real Writer document insertion safely and reproducibly before any native LibreOffice production claim is considered.

## Current status

```text
source-preserving one-document LibreOffice round trip: implemented
supervised POSIX UNO multi-document merge prototype: implemented
isolated LibreOffice user profile: implemented
unique UNO pipe per merge: implemented
isolated POSIX process-group cleanup: implemented
real subprocess cleanup regressions: implemented
body structure/text acceptance: implemented
new-risk-category acceptance: implemented
explicit ordered private-manuscript acceptance command: implemented
real Ubuntu UNO acceptance workflow: implemented
separate process-group cleanup workflow: implemented
section/page-layout certification: still required
representative private corpus acceptance: still required
Windows native LibreOffice acceptance: still required if claimed
production LibreOffice merge mode: disabled
```

The normal `docmergeforge docx` command continues to use portable OOXML composition.

## Authoritative implementation

```text
src/docmergeforge/docx/libreoffice.py
src/docmergeforge/docx/libreoffice_uno_merge.py
src/docmergeforge/docx/libreoffice_uno_acceptance.py
scripts/check_libreoffice_uno_merge_smoke.py
scripts/check_libreoffice_uno_merge_acceptance.py
.github/workflows/libreoffice-uno-acceptance.yml
.github/workflows/libreoffice-uno-process-cleanup.yml
```

There is only one maintained native multi-document LibreOffice acceptance path. Superseded prototype files are not part of the supported acceptance surface.

## LibreOffice interfaces used

The supervised worker uses LibreOffice's UNO/Writer API model:

- `com.sun.star.bridge.UnoUrlResolver` resolves a unique local UNO pipe;
- the external process exposes `StarOffice.ServiceManager` and the worker resolves `StarOffice.ComponentContext`;
- Writer's document cursor uses `XDocumentInsertable.insertDocumentFromURL(...)` to insert later source documents in order;
- `com.sun.star.text.ControlCharacter.PARAGRAPH_BREAK` creates the insertion boundary;
- `com.sun.star.style.BreakType.PAGE_BEFORE` requests a page start for later sources when enabled;
- `XStorable.storeAsURL(...)` writes the temporary merged document; and
- DOCX export uses the `Office Open XML Text` filter.

Using native APIs is implementation evidence, not proof that every Microsoft Word-specific construct survives Writer insertion/export identically.

## Process and profile isolation

Every supervised acceptance run uses:

1. a unique temporary LibreOffice user-profile directory;
2. a unique UNO pipe name;
3. `--headless`, `--nologo`, `--nodefault`, `--nofirststartwizard`, and `--norestore`;
4. a new POSIX process session/process group;
5. a separate Python UNO worker; and
6. cleanup targeted only at the process group created for that acceptance run.

The implementation does not reuse the operator's normal LibreOffice profile and does not kill processes by a broad `soffice`/`libreoffice` name match.

The launcher is polled/reaped while group existence is checked. This prevents an exited launcher from remaining a zombie and being mistaken for a live office group while still allowing a surviving `soffice.bin` child to be detected.

The current cleanup implementation relies on POSIX process-group semantics. Other operating-system process-supervision models remain separate work if native LibreOffice mode is claimed there.

## Python UNO bridge

The normal DocMergeForge Python environment is not assumed to contain LibreOffice's `uno` module. The prototype searches candidate interpreters and accepts only one that successfully executes:

```text
import uno
```

An operator can explicitly choose the UNO-capable interpreter with:

```text
DOCMERGEFORGE_UNO_PYTHON
```

The Ubuntu acceptance workflow installs `python3-uno` and verifies `/usr/bin/python3` can import `uno` before starting Writer.

## Input and source safety

Before Writer starts, DocMergeForge:

- requires at least one source;
- accepts DOCX sources only;
- requires a separate `.docx` destination;
- rejects duplicate resolved source paths;
- refuses an existing destination;
- validates every source OOXML package;
- requires a positive timeout; and
- records source SHA-256 hashes.

The first source is copied to an isolated temporary master working copy. Writer edits that copy rather than the original. Later sources are inserted by URL in the exact supplied order.

Source hashes are rechecked around native processing and evidence construction. The native result is written to a temporary DOCX, structurally validated, promoted only after checks pass, validated again at the final path, and source integrity is checked again.

## Timeout and process-group cleanup

If the UNO worker exceeds its timeout:

1. the worker process is terminated;
2. the isolated LibreOffice group receives `SIGTERM`;
3. DocMergeForge waits for the complete process group to disappear while polling/reaping its launcher;
4. if the group remains, that same isolated group receives `SIGKILL`; and
5. the operation fails if group termination cannot be proven.

This cleanup is independently regression-tested with real POSIX subprocesses in:

```text
tests/integration/test_lo_uno_process_group.py
.github/workflows/libreoffice-uno-process-cleanup.yml
```

That lane exercises process supervision without depending on document fidelity, so a cleanup regression cannot be hidden by a Writer-document result.

## Current measured acceptance

`src/docmergeforge/docx/libreoffice_uno_acceptance.py` deliberately starts with a narrow, measurable first gate.

### Structure

- non-empty body paragraph count;
- body table count;
- inline-shape count;
- heading count.

### Privacy-safe content

- ordered non-empty body paragraph text SHA-256;
- ordered body-table-cell text SHA-256.

Text records are length-delimited before hashing. Plain manuscript text is not serialized into the JSON evidence.

### OOXML risk categories

The acceptance compares the union of risky source OOXML categories with the output and rejects newly introduced risk categories.

### Source-revision binding

Source hashes are captured before expected evidence is built and checked again before native execution, after Writer processing, and after output evidence is measured. Evidence from mixed source revisions therefore fails closed.

### Acceptance rule

The first supervised UNO gate accepts only when:

1. expected and output measured structures match;
2. ordered body-text/table-cell fingerprints match; and
3. no new risky OOXML category appears in the merged output.

This rule is intentionally narrower than universal layout fidelity.

## Deliberately excluded from the current pass rule

The current supervised UNO pass does **not** certify:

- section count/equivalence;
- page orientation, size, or margins;
- gutter/header/footer distances;
- header/footer content and linked-to-previous semantics;
- page-number restart/format/chapter semantics;
- exact line wrapping or pagination;
- floating-object coordinates;
- fields/TOC/bookmark/hyperlink recalculation or rendering;
- charts/SmartArt appearance;
- comments/tracked-change behavior;
- content controls;
- embedded objects/custom XML;
- font availability or substitution.

Those remain explicit later acceptance gates.

## Synthetic real-Writer smoke

On a POSIX host with LibreOffice Writer and a working Python UNO bridge:

```bash
python scripts/check_libreoffice_uno_merge_smoke.py \
  --output-dir libreoffice-uno-evidence \
  --timeout 300
```

The smoke creates two distinct DOCX sources, executes the real supervised Writer insertion path, and writes the merged DOCX plus privacy-safe measured JSON evidence. Existing artifacts are not overwritten.

## Explicit ordered acceptance command

For private representative manuscripts, repeat `--input` in the exact intended merge order:

```bash
python scripts/check_libreoffice_uno_merge_acceptance.py \
  --input "./private-corpus/Part 1.docx" \
  --input "./private-corpus/Part 2.docx" \
  --output "./private-evidence/merged.docx" \
  --evidence "./private-evidence/libreoffice-uno-evidence.json" \
  --timeout 300
```

Use `--no-start-each-on-new-page` only when the acceptance scenario intentionally requires continuous insertion boundaries.

Exit behavior:

- `0` — the measured acceptance rule passed;
- `2` — a result/evidence record was produced but measured acceptance failed;
- other non-zero/error — input, capability, UNO, timeout, cleanup, source-integrity, output-validation, or output-safety failure.

Existing evidence is not overwritten. Keep private input/output DOCX files outside public workflow artifacts unless their disclosure is intentional.

## GitHub Actions acceptance

`.github/workflows/libreoffice-uno-acceptance.yml` runs on relevant `main` changes and manual dispatch. Its Ubuntu job:

1. installs LibreOffice Writer and `python3-uno`;
2. installs DocMergeForge development dependencies;
3. reports fidelity capability separation;
4. verifies `/usr/bin/python3` can import `uno`;
5. runs the supervised merge, evidence, workflow-policy, smoke, and explicit-command regression surface;
6. executes a real two-document Writer UNO merge;
7. displays measured evidence when available; and
8. uploads the synthetic source/output/evidence bundle.

`.github/workflows/libreoffice-uno-process-cleanup.yml` independently executes the real process-group cleanup regressions.

A workflow definition is not passing evidence. A concrete completed run and its artifacts must be reviewed before citing external LibreOffice acceptance.

## Production policy

Even after the first real supervised Writer smoke passes:

```text
libreoffice.production_ready = false
```

must remain unchanged until the complete supported application contract is certified.

Production certification still requires representative real-world corpora, section/page-layout fidelity, advanced OOXML constructs, target-platform/version coverage, large-document behavior, cancellation/process cleanup, packaged-app integration if distributed, and human rendering/interoperability review.

## Remaining LibreOffice release gates

Before native LibreOffice production mode can be considered:

1. obtain and review a passing real supervised UNO multi-document workflow run;
2. obtain and review the real process-group cleanup workflow evidence;
3. expand measured evidence to sections/page styles/headers/footers/page numbering;
4. test complex styles/themes/list numbering;
5. test images/drawings/text boxes;
6. test fields/TOC/bookmarks/hyperlinks;
7. test comments/tracked changes/content controls;
8. test equations/charts/SmartArt/embedded objects/custom XML;
9. test non-Latin text and representative fonts;
10. test very large and long-running documents;
11. run representative private multi-document corpora;
12. perform manual LibreOffice Writer and Microsoft Word interoperability review where relevant;
13. implement/verify non-POSIX process isolation if additional operating systems are claimed;
14. integrate the native path into the full application/project transaction contract only after certification; and
15. preserve every discovered fidelity defect as a reproducible regression.

See also:

- [DOCX Fidelity Adapters and Acceptance](docx-fidelity-acceptance.md)
- [DOCX Engine](docx-engine.md)
- [Private DOCX Fidelity Corpus Testing](docx-fidelity-corpus.md)
- [Known Limitations](known-limitations.md)
- [Testing and CI](testing-and-ci.md)
- [Release Evidence Ledger](release-evidence.md)
