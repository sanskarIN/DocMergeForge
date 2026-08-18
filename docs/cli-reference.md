# CLI Reference

The `docmergeforge` command is the automation-oriented interface to DocMergeForge. It supports discovery/validation, direct PDF and DOCX merging, DOCX fidelity capability/acceptance checks, private fidelity-corpus execution, reusable project files, the SQL Full Mastery preset, interrupted-output recovery, manuscript audit, and output comparison.

```bash
docmergeforge --help
```

## Exit codes

Common exit behavior:

- `0` — command completed successfully or requested dry-run/acceptance is ready.
- `2` — validation/preflight/recovery/acceptance/argument condition failed and user action is required.
- `130` — interactive encrypted-PDF password collection was cancelled.

Unexpected exceptions can produce a non-zero process exit according to Python/runtime behavior.

## Shared part-range syntax

Commands that accept `--parts` use an inclusive positive range:

```text
1-120
1-10
25-50
```

Invalid examples:

```text
0-120
20-10
abc
```

The default range is `1-120` where supported.

## Discovery options

`validate`, `pdf`, and `docx` support:

### `--pattern GLOB`

Optional case-insensitive filename glob filtering.

Example:

```bash
--pattern "Part *.pdf"
```

The filter is applied to discovered filenames after scanning.

### `--natural-sort` / `--no-natural-sort`

Natural part-number sorting is enabled by default.

With natural sorting:

```text
Part 1
Part 2
Part 10
```

With `--no-natural-sort`, files are ordered by case-insensitive filename text.

## `validate`

Discover and validate numbered PDF and DOCX part sets.

```bash
docmergeforge validate --input PATH [--parts START-END] [--pattern GLOB] [--natural-sort|--no-natural-sort]
```

Required:

- `--input PATH` — folder to scan.

Optional:

- `--parts START-END` — expected inclusive range; default `1-120`.
- `--pattern GLOB` — filename filter.
- `--natural-sort` / `--no-natural-sort` — ordering mode.

Example:

```bash
docmergeforge validate \
  --input "./Book" \
  --parts 1-120
```

Output is JSON with separate `pdf` and `docx` objects containing:

- `ready`;
- `missing`;
- `duplicates`;
- `found`.

The command returns exit code `2` if either checked kind is not ready.

## `pdf`

Directly merge discovered PDF parts using default PDF settings.

```bash
docmergeforge pdf \
  --input PATH \
  --output FILE.pdf \
  [--parts START-END] \
  [--pattern GLOB] \
  [--natural-sort|--no-natural-sort]
```

Example:

```bash
docmergeforge pdf \
  --input "./Book" \
  --parts 1-120 \
  --output "./Master/Book-Master.pdf"
```

Behavior:

1. scans the input location;
2. selects only PDF documents;
3. filters/orders them;
4. prompts for encrypted-PDF passwords where needed;
5. validates the complete part range;
6. refuses missing/duplicate sets;
7. runs the PDF merge engine with order preservation;
8. validates the generated output;
9. prints the output path on success.

Direct merge is intentionally simpler than a full project run and does not represent the complete publication-bundle workflow.

## `docx`

Directly merge discovered DOCX parts using default portable DOCX settings.

```bash
docmergeforge docx \
  --input PATH \
  --output FILE.docx \
  [--parts START-END] \
  [--pattern GLOB] \
  [--natural-sort|--no-natural-sort]
```

Example:

```bash
docmergeforge docx \
  --input "./Book" \
  --parts 1-120 \
  --output "./Master/Book-Master.docx"
```

The command selects only DOCX files, validates the complete part set, merges in the selected order, and validates the resulting OOXML package. It does not silently switch to LibreOffice or Word.

## `fidelity-capabilities`

Report DOCX fidelity adapter detection, automation readiness, and production readiness as separate fields.

```bash
docmergeforge fidelity-capabilities
```

Output is a JSON array with one object per mode. Fields include:

- `mode`;
- `available`;
- `production_ready`;
- `detail`;
- `automation_ready`;
- `executable`.

The portable mode is production-ready. LibreOffice/Word can be detected or automation-ready while remaining `production_ready=false`.

Do not interpret `available=true` as a universal fidelity guarantee.

## `fidelity-roundtrip`

Run an explicit external-office round-trip on one DOCX and emit measured structural/risk evidence.

```bash
docmergeforge fidelity-roundtrip \
  --input FILE.docx \
  --output FILE.docx \
  --mode libreoffice|word \
  [--timeout SECONDS]
```

Required:

- `--input` — existing DOCX source;
- `--output` — separate DOCX destination that does not already exist;
- `--mode` — `libreoffice` or `word`.

Optional:

- `--timeout` — positive native-office timeout in seconds; default `300`.

LibreOffice example:

```bash
docmergeforge fidelity-roundtrip \
  --input "./samples/representative.docx" \
  --output "./evidence/representative-libreoffice.docx" \
  --mode libreoffice \
  --timeout 300
```

Microsoft Word example on Windows:

```powershell
docmergeforge fidelity-roundtrip `
  --input ".\samples\representative.docx" `
  --output ".\evidence\representative-word.docx" `
  --mode word `
  --timeout 300
```

The command prints JSON containing source/output hashes, structural snapshots, risk findings, newly introduced risk categories, and `accepted`.

`accepted=true` currently requires:

1. matching measured paragraph/table/inline-shape/section/heading counts; and
2. no new risky-construct category in the round-tripped output.

The command returns `0` for measured acceptance and `2` for a structurally valid output that does not meet those measured acceptance criteria. Native-tool launch, timeout, source-integrity, or invalid-output failures are treated as errors.

This command creates evidence; it does not enable the external adapter as the normal production merge path. See [DOCX Fidelity Adapters and Acceptance](docx-fidelity-acceptance.md).

## `fidelity-corpus`

Run explicit external-office DOCX acceptance across a private local corpus without committing the source manuscripts to the repository.

```bash
docmergeforge fidelity-corpus \
  --input-dir PATH \
  --output-dir PATH \
  --mode libreoffice|word \
  [--pattern GLOB] \
  [--recursive|--no-recursive] \
  [--timeout SECONDS] \
  [--fail-fast]
```

Required:

- `--input-dir` — private source corpus directory;
- `--output-dir` — separate evidence/output directory outside the source corpus;
- `--mode` — `libreoffice` or `word`.

Optional:

- `--pattern` — case-insensitive filename glob; default `*.docx`;
- `--recursive` / `--no-recursive` — recursive discovery is enabled by default;
- `--timeout` — positive per-document native-office timeout in seconds; default `300`;
- `--fail-fast` — stop after the first adapter/validation error. A stopped-early report is never accepted.

LibreOffice example:

```bash
docmergeforge fidelity-corpus \
  --input-dir "./private-corpus" \
  --output-dir "./private-fidelity-evidence" \
  --mode libreoffice \
  --pattern "*.docx" \
  --timeout 300
```

Microsoft Word example on Windows:

```powershell
docmergeforge fidelity-corpus `
  --input-dir ".\private-corpus" `
  --output-dir ".\private-fidelity-evidence" `
  --mode word `
  --timeout 300
```

The command refuses an output directory that is equal to or nested inside the source corpus, requires at least one matching DOCX, preserves relative subdirectory layout below `roundtrip/`, and writes:

```text
<output-dir>/roundtrip/...
<output-dir>/fidelity-corpus-<mode>-report.json
```

The JSON report contains:

- `mode`;
- `pattern`;
- `recursive`;
- `discovered_count`;
- `processed_count`;
- `accepted_count`;
- `failed_count`;
- `stopped_early`;
- overall `accepted`;
- per-document relative source/output paths, error state, and measured evidence.

The serialized corpus report rewrites source/output locations to corpus-relative paths so workstation/user directory information is not automatically embedded in the report. The generated round-trip DOCX files still contain the document content and therefore remain private unless sanitized.

The command returns `0` only when every discovered document was processed and accepted. Fail-fast partial execution, a failed item, or an acceptance mismatch returns `2`/an error as appropriate.

This command never uploads the corpus or turns an external adapter into a production merge mode. See [Private DOCX Fidelity Corpus Testing](docx-fidelity-corpus.md).

## `sql-preset`

Run the dedicated SQL Full Mastery 120-part guided workflow.

```bash
docmergeforge sql-preset \
  --input PATH \
  --output-dir PATH \
  [--dry-run]
```

Required:

- `--input` — source manuscript folder.
- `--output-dir` — publication output folder.

Optional:

- `--dry-run` — build and print preflight evidence without publishing outputs.

Dry-run example:

```bash
docmergeforge sql-preset \
  --input "./SQL-Full-Mastery" \
  --output-dir "./SQL-Master" \
  --dry-run
```

Full example:

```bash
docmergeforge sql-preset \
  --input "./SQL-Full-Mastery" \
  --output-dir "./SQL-Master"
```

The preset is stricter than a generic project: both expected manuscript kinds must be ready for Parts 1–120 for the dry run to return success.

## `project-create`

Create a reusable JSON merge project.

```bash
docmergeforge project-create \
  --input PATH \
  --output-dir PATH \
  --project-file FILE.json \
  [--name NAME] \
  [--parts START-END] \
  [--sql-preset]
```

Required:

- `--input` — source folder.
- `--output-dir` — target publication folder.
- `--project-file` — project JSON path to write.

Optional:

- `--name` — project name; default `DocMergeForge Project`.
- `--parts` — expected range; default `1-120`.
- `--sql-preset` — construct the SQL Full Mastery preset project instead of a generic project.

Generic example:

```bash
docmergeforge project-create \
  --input "./Book" \
  --output-dir "./Master" \
  --project-file "./Book.json" \
  --name "Book Master Edition" \
  --parts 1-80
```

SQL preset project example:

```bash
docmergeforge project-create \
  --input "./SQL-Full-Mastery" \
  --output-dir "./SQL-Master" \
  --project-file "./sql-full-mastery.json" \
  --sql-preset
```

## `merge`

Run or preflight a reusable project.

```bash
docmergeforge merge --project FILE.json [--dry-run]
```

Example dry run:

```bash
docmergeforge merge --project "./Book.json" --dry-run
```

Dry-run JSON contains:

- PDF/DOCX counts and readiness;
- missing/duplicate parts;
- `ready_for_available_kinds`;
- companion and ignored counts;
- storage estimates/free-space status;
- ordered PDF/DOCX paths;
- expected output paths;
- DOCX conflict count.

Full run:

```bash
docmergeforge merge --project "./Book.json"
```

Encrypted PDF passwords are collected interactively before preflight/full project execution when needed.

## `recover-output`

Recover interrupted journaled publication transactions.

```bash
docmergeforge recover-output --output-dir PATH
```

Example:

```bash
docmergeforge recover-output --output-dir "./Master"
```

Successful output is JSON containing:

- `recovered: true`;
- output directory;
- zero or more transaction results;
- transaction folder;
- recovery status;
- restored paths;
- removed paths.

If a journal is corrupt or the filesystem no longer matches a safe recovery assumption, recovery returns JSON with `recovered: false`, the error, and exit code `2`.

Never delete a `.docmergeforge-staging-*` directory before understanding whether it contains a rollback backup.

## `audit`

Audit PDF/DOCX manuscript content locally.

```bash
docmergeforge audit --input PATH
```

Example:

```bash
docmergeforge audit --input "./Book"
```

Output is a JSON array. Each finding contains:

- `code`;
- `message`;
- `path`;
- `severity`.

The audit command reports findings; it does not silently modify manuscript files.

## `compare`

Compare merged output evidence with discovered source manuscripts.

```bash
docmergeforge compare \
  --input PATH \
  [--pdf-output FILE.pdf] \
  [--docx-output FILE.docx]
```

At least one output option is required.

PDF only:

```bash
docmergeforge compare \
  --input "./Book" \
  --pdf-output "./Master/Book-Master.pdf"
```

DOCX only:

```bash
docmergeforge compare \
  --input "./Book" \
  --docx-output "./Master/Book-Master.docx"
```

Both:

```bash
docmergeforge compare \
  --input "./Book" \
  --pdf-output "./Master/Book-Master.pdf" \
  --docx-output "./Master/Book-Master.docx"
```

The command scans the source folder, selects source documents by kind, performs the relevant comparison, and prints JSON evidence.

## Encrypted-PDF interaction

For commands that execute a PDF merge/project run, each encrypted PDF is prompted separately:

```text
Password for encrypted PDF <path>:
```

A wrong password produces a retry message. Password input is hidden by the terminal. Ctrl+C cancels the operation. Password dictionaries are cleared at the end of command execution.

The plain `validate` command does not collect passwords and therefore does not treat encrypted PDFs as unlocked.

## Automation guidance

For reliable scripting:

- use `--dry-run` before project publication;
- inspect exit codes, not only stdout text;
- parse JSON for `validate`, project dry runs, `fidelity-capabilities`, `fidelity-roundtrip`, `fidelity-corpus`, `recover-output`, `audit`, and `compare`;
- avoid depending on filesystem directory listing order;
- preserve project files and publication/fidelity evidence with release artifacts;
- keep private fidelity corpus sources/evidence outside public source control unless intentionally sanitized;
- do not auto-delete transaction folders on error;
- keep encrypted-PDF workflows interactive unless a future supported secret-provider interface is implemented;
- never promote an external DOCX fidelity mode to production based only on a successful single-file or corpus round-trip.

## Shell path examples

Quote paths containing spaces.

Windows PowerShell:

```powershell
docmergeforge validate --input "C:\Books\My Series" --parts 1-120
```

macOS/Linux:

```bash
docmergeforge validate --input "/home/user/Books/My Series" --parts 1-120
```

## Command summary

| Command | Purpose |
|---|---|
| `validate` | Discover and validate expected numbered parts |
| `pdf` | Direct PDF merge |
| `docx` | Direct portable DOCX merge |
| `fidelity-capabilities` | Report fidelity detection/automation/production states |
| `fidelity-roundtrip` | Run explicit one-file LibreOffice/Word DOCX acceptance evidence |
| `fidelity-corpus` | Run privacy-safe local external-office acceptance across a DOCX corpus |
| `sql-preset` | Guided SQL Full Mastery 120-part publication |
| `project-create` | Create reusable JSON project |
| `merge` | Dry-run or execute project |
| `recover-output` | Recover interrupted journaled publication |
| `audit` | Local manuscript audit |
| `compare` | Compare merged output with source evidence |
