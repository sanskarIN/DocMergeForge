# LibreOffice Native Multi-Document Merge Acceptance

DocMergeForge includes a separate LibreOffice Writer UNO multi-document merge **acceptance prototype**. It is not connected to the normal production DOCX engine and does not make `libreoffice` production-ready.

The prototype exists to measure real LibreOffice Writer document insertion before any native LibreOffice production claim is considered.

## Current status

```text
source-preserving one-document LibreOffice round trip: implemented
POSIX UNO multi-document merge prototype: implemented
isolated LibreOffice user profile: implemented
unique UNO pipe per merge: implemented
isolated POSIX process-group cleanup: implemented
body structure/text acceptance: implemented
new-risk-category acceptance: implemented
real Ubuntu UNO acceptance workflow: implemented
section/page-layout certification: still required
representative private corpus: still required
Windows native LibreOffice acceptance: still required if claimed
production LibreOffice merge mode: disabled
```

The normal `docmergeforge docx` command continues to use portable OOXML composition.

## Official LibreOffice interfaces used

The prototype follows LibreOffice's UNO/Writer API model:

- `com.sun.star.bridge.UnoUrlResolver` resolves an isolated UNO connection;
- Writer's document text cursor exposes `XDocumentInsertable.insertDocumentFromURL(...)` for inserting another document at the cursor position;
- `com.sun.star.text.ControlCharacter.PARAGRAPH_BREAK` creates the insertion paragraph boundary;
- `com.sun.star.style.BreakType.PAGE_BEFORE` requests a page break before a later source when configured;
- `XStorable.storeAsURL(...)` writes the merged document;
- the DOCX export filter is `Office Open XML Text`.

These are native LibreOffice APIs. Their use does not by itself prove that every Microsoft Word-specific construct survives insertion/export identically.

## Implementation

```text
src/docmergeforge/docx/libreoffice_merge.py
src/docmergeforge/docx/libreoffice_merge_acceptance.py
scripts/check_libreoffice_native_merge_smoke.py
```

## Process isolation

Every native acceptance run uses:

1. a unique temporary LibreOffice user-profile directory;
2. a unique UNO pipe name;
3. `--headless`, `--nologo`, `--nodefault`, `--nofirststartwizard`, and `--norestore`;
4. a new POSIX process session/process group;
5. a separate Python UNO worker; and
6. cleanup targeted only at the process group created for that acceptance run.

The prototype does not reuse the operator's normal LibreOffice profile and does not issue broad process-name kills.

This implementation is currently limited to POSIX process-group semantics. Windows native LibreOffice acceptance remains a separate implementation/verification gate if Windows LibreOffice native mode is ever claimed.

## Python UNO bridge

The application Python environment is not assumed to contain LibreOffice's `uno` module.

The prototype searches for a Python interpreter that can actually execute:

```text
import uno
```

The environment variable below can explicitly select that interpreter:

```text
DOCMERGEFORGE_UNO_PYTHON
```

On the Ubuntu acceptance workflow, `python3-uno` is installed and `/usr/bin/python3` is verified before the native merge is executed.

## Source safety

Before starting LibreOffice, DocMergeForge:

- requires at least one DOCX source;
- requires a separate `.docx` output path;
- rejects duplicate resolved source paths;
- refuses to overwrite an existing destination;
- validates every source DOCX/OOXML package; and
- records source SHA-256 hashes.

The first source is copied to an isolated temporary master working copy before Writer opens it for editing. Later source files are inserted by URL and are not selected as the writable master.

Source hashes are checked before/after native processing. The result is written to a temporary DOCX, validated, promoted to the requested output, validated again, and source hashes are rechecked.

## Worker timeout and process-group cleanup

The UNO worker is given a positive timeout. If it exceeds that timeout:

1. only the worker process is killed first;
2. the isolated LibreOffice process group receives `SIGTERM`;
3. DocMergeForge waits for the complete group to disappear;
4. if necessary, that same isolated group receives `SIGKILL`; and
5. acceptance fails if the isolated group still cannot be proven gone.

The cleanup waits on the **process group**, not merely the LibreOffice launcher PID, so a surviving `soffice.bin` child cannot be ignored because its launcher exited.

This is an acceptance safety boundary, not a claim about every possible OS/process failure.

## Current measured acceptance

`src/docmergeforge/docx/libreoffice_merge_acceptance.py` currently measures the parts of multi-document insertion that are expected to be stable enough for the first external gate:

### Structure

- non-empty body paragraph count;
- body table count;
- inline-shape count;
- heading count.

### Privacy-safe content

- ordered non-empty body paragraph text SHA-256;
- ordered body-table-cell text SHA-256.

Length-delimited UTF-8 records are hashed; plain manuscript text is not serialized into acceptance JSON.

### OOXML risk categories

The acceptance compares the union of risky source OOXML categories with the output and rejects newly introduced risk categories.

### Source revision binding

Source hashes are captured before expected evidence is built and rechecked before native execution, after native execution, and after output evidence is calculated.

## Deliberately excluded from the current pass rule

The first native LibreOffice multi-document gate does **not** yet treat the following as certified pass criteria:

- section count/equivalence;
- page orientation and page size;
- margins/gutter;
- header/footer linkage;
- page-number restart/format semantics;
- exact line wrapping/pagination;
- floating-object coordinates;
- fields/TOC recalculation;
- chart/SmartArt appearance;
- tracked-change/comment display;
- content controls;
- embedded objects/custom XML;
- font substitution.

Those remain explicit later acceptance gates rather than being silently assumed from body-text success.

## Synthetic real-Writer smoke

Run on a POSIX host with LibreOffice Writer and a working Python UNO bridge:

```bash
python scripts/check_libreoffice_native_merge_smoke.py \
  --output-dir libreoffice-native-evidence \
  --timeout 300
```

The smoke creates two separate DOCX inputs with distinct paragraphs and tables, executes the real UNO insertion path, and writes:

```text
libreoffice-merge-source-01.docx
libreoffice-merge-source-02.docx
libreoffice-native-merged.docx
libreoffice-native-merge-evidence.json
```

Existing smoke artifacts are never overwritten.

## GitHub Actions acceptance

`.github/workflows/libreoffice-native-acceptance.yml` runs on relevant `main` changes and manual dispatch.

The Ubuntu job:

1. installs LibreOffice Writer and `python3-uno`;
2. installs DocMergeForge developer dependencies;
3. records normal fidelity capability separation;
4. verifies `/usr/bin/python3` can import `uno`;
5. runs LibreOffice round-trip/native-merge/acceptance/smoke boundary tests;
6. executes the real Writer UNO multi-document smoke;
7. displays measured JSON evidence when available; and
8. uploads the generated source/output/evidence bundle even when later investigation is required.

A workflow definition is not acceptance evidence. Record a concrete passing run ID before citing this gate externally.

## Production policy

Even after a passing first native Writer smoke:

```text
libreoffice.production_ready = false
```

must remain unchanged.

Production certification still requires representative real-world corpora, section/page-layout fidelity, advanced OOXML constructs, target-platform/version coverage, large-document behavior, cancellation/cleanup acceptance, packaged application integration if distributed, and human rendering/behavior review.

## Remaining LibreOffice work

Before native LibreOffice production mode can be considered:

1. obtain and review a passing real UNO multi-document acceptance run;
2. expand measured evidence to section/page-style/header/footer/page-number behavior;
3. test complex styles/themes/list numbering;
4. test images/drawings/text boxes;
5. test fields/TOC/bookmarks/hyperlinks;
6. test comments/tracked changes/content controls;
7. test equations/charts/embedded objects/custom XML;
8. test non-Latin text and representative fonts;
9. test very large/long-running documents;
10. run representative private manuscript corpora;
11. perform manual Writer and Microsoft Word interoperability review where relevant;
12. implement/verify other OS process-isolation semantics if those platforms are claimed; and
13. keep every discovered fidelity defect as a reproducible regression.

See also:

- [DOCX Fidelity Adapters and Acceptance](docx-fidelity-acceptance.md)
- [DOCX Engine](docx-engine.md)
- [Private DOCX Fidelity Corpus Testing](docx-fidelity-corpus.md)
- [Known Limitations](known-limitations.md)
- [Testing and CI](testing-and-ci.md)
- [Release Evidence Ledger](release-evidence.md)
