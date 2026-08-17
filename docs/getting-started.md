# Getting Started

This guide walks through a safe first DocMergeForge workflow: prepare numbered source files, validate discovery/order, run a dry preflight, merge, inspect evidence, and recover safely if publication is interrupted.

## 1. Prepare your source folder

Use one folder (or a project with configured source folders) containing numbered manuscript parts. Typical names include:

```text
Part 1.pdf
Part 2.pdf
Part 3.pdf
...
Part 120.pdf

Part 1.docx
Part 2.docx
Part 3.docx
...
Part 120.docx
```

The exact title text can vary. DocMergeForge extracts part numbers and uses natural numeric ordering so Part 2 sorts before Part 10.

Keep source code, examples, or companion archives independent. ZIP/source packages can be indexed as companion material but are never merged into PDF or DOCX manuscripts.

## 2. Validate discovery before merging

For a 120-part publication:

```bash
docmergeforge validate --input "./My-Series" --parts 1-120
```

The command reports separate `pdf` and `docx` readiness, including:

- expected/found parts;
- missing part numbers;
- duplicate part numbers;
- whether each manuscript kind is ready.

A validation exit code of `2` means at least one checked document kind is not ready.

If filenames need filtering:

```bash
docmergeforge validate \
  --input "./My-Series" \
  --parts 1-120 \
  --pattern "Part *.pdf"
```

Natural sorting is enabled by default. Use `--no-natural-sort` only when plain filename order is intentionally required.

## 3. Choose direct merge or project workflow

### Direct merge

Use direct commands when you need one format and simple defaults.

PDF:

```bash
docmergeforge pdf \
  --input "./My-Series" \
  --parts 1-120 \
  --output "./Master/My-Series-Master.pdf"
```

DOCX:

```bash
docmergeforge docx \
  --input "./My-Series" \
  --parts 1-120 \
  --output "./Master/My-Series-Master.docx"
```

### Reusable project

Use a project when the work should be repeatable, include both document kinds, generate publication evidence, preserve selected ordering/settings, or be opened in the desktop application.

Create a project:

```bash
docmergeforge project-create \
  --input "./My-Series" \
  --output-dir "./Master" \
  --project-file "./My-Series.json" \
  --name "My Series" \
  --parts 1-120
```

Dry-run it first:

```bash
docmergeforge merge --project "./My-Series.json" --dry-run
```

Then run it:

```bash
docmergeforge merge --project "./My-Series.json"
```

## 4. Read the dry-run/preflight output

A project dry run reports evidence including:

- PDF and DOCX counts/readiness;
- missing and duplicate parts;
- ordered PDF paths;
- ordered DOCX paths;
- expected output paths;
- DOCX conflict count;
- companion/ignored counts;
- source bytes;
- temporary bytes;
- projected output bytes;
- safe-required bytes;
- free bytes and storage sufficiency.

Do not proceed when the preflight says the available kinds are not ready or storage is insufficient.

## 5. Review order explicitly

Before publication, verify that the intended order is correct. The desktop order editor allows explicit review/reordering and preserves selected project order. In CLI workflows, discovery uses natural part order unless plain filename ordering is requested.

A safe publication should never rely on visual folder order alone.

## 6. Merge and allow validation to finish

During a project run, DocMergeForge does more than concatenate files. The high-level pipeline is:

1. discover inputs;
2. classify PDF, DOCX, companion, and ignored files;
3. validate part sets;
4. check output destination/storage;
5. capture source-integrity evidence;
6. stage PDF/DOCX outputs;
7. validate staged manuscripts;
8. generate reports/checksums/manifests/checklists;
9. revalidate source integrity;
10. transactionally promote the complete publication bundle.

The final files are not considered published until the batch promotion succeeds.

## 7. Inspect generated evidence

Depending on the project/preset/settings, the publication bundle can include:

- merged PDF;
- merged DOCX;
- checksums;
- merge manifest;
- source/companion indexes;
- Markdown/HTML reports;
- publishing checklist;
- other validation evidence.

Treat these files as part of the publication record, not disposable logs.

## 8. Compare outputs when required

To compare merged outputs with source evidence:

```bash
docmergeforge compare \
  --input "./My-Series" \
  --pdf-output "./Master/My-Series-Master.pdf" \
  --docx-output "./Master/My-Series-Master.docx"
```

You may supply only one output option if only one format is being checked.

## 9. Audit manuscript content

Run a local audit of PDF/DOCX content:

```bash
docmergeforge audit --input "./My-Series"
```

The output is JSON containing finding code, message, path, and severity.

## 10. Handle encrypted PDFs

When an encrypted PDF is encountered by a merge/project workflow, the CLI prompts for its password. Incorrect passwords can be retried. Ctrl+C cancels password collection and returns cancellation code `130`.

Passwords are held in memory for the run and cleared afterward.

## 11. Recover interrupted publication safely

If a process stops during final publication promotion, DocMergeForge can leave a hidden `.docmergeforge-staging-*` folder containing a journal and possibly rollback backups.

Do **not** delete that folder manually.

Run:

```bash
docmergeforge recover-output --output-dir "./Master"
```

The recovery command fails closed if current files conflict with the recorded transaction state. Resolve conflicts deliberately rather than deleting transaction evidence.

## 12. Use the desktop application

Start:

```bash
docmergeforge-gui
```

The desktop experience provides guided project setup, validation/preflight, document ordering, merge progress/cancellation, reports, recent projects, recovery checkpoints, audit/compare, settings, help/support, and SQL preset entry points.

See [Desktop User Guide](desktop-guide.md).

## 13. SQL Full Mastery preset

For the dedicated 120-part SQL workflow:

```bash
docmergeforge sql-preset \
  --input "./SQL-Full-Mastery" \
  --output-dir "./SQL-Full-Mastery-Master-Edition" \
  --dry-run
```

After the dry run is clean:

```bash
docmergeforge sql-preset \
  --input "./SQL-Full-Mastery" \
  --output-dir "./SQL-Full-Mastery-Master-Edition"
```

The preset requires complete Parts 1–120 for both expected manuscript kinds before a full preset run is considered ready.

## First-run safety checklist

Before trusting a production merge:

- keep independent backups of all original parts;
- validate the exact expected part range;
- resolve duplicate/missing part errors;
- review detected order;
- run project/preset dry-run;
- verify output location and free space;
- inspect DOCX conflict/risk findings;
- never mix source-code archives into a manuscript merge;
- allow final validation/reporting/promotion to complete;
- keep generated manifest/checksum/report evidence;
- use journal-aware recovery after an interrupted promotion.
