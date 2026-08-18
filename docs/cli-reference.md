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

## Automatic direct-merge input rule

Direct `pdf`/`docx` commands intentionally distinguish **discovered files** from **files allowed to reach the merge engine**.

After scanning, optional pattern filtering, and ordering, an automatic merge input must:

1. match the requested document kind;
2. have a detected part number; and
3. have that number inside the configured inclusive `--parts` range.

For `--parts 1-120`, files such as `Part 121.pdf`, `Book Master.pdf`, and unnumbered `notes.pdf` remain available to validation diagnostics but are not silently appended to the manuscript. Use a reviewed project `selected_files` workflow when intentional unnumbered front/back matter must participate.

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
- `found`;
- `diagnostics` — structured `INFO`/`WARNING`/`ERROR`/`FATAL` findings, including unnumbered and out-of-range review signals.

Blocking file-specific checks such as zero-byte/encrypted-source failures are bound to the resolved automatic merge candidates for the requested range. An unrelated out-of-range file can therefore warn without falsely blocking an otherwise safe numbered merge.

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
2. selects PDF documents for discovery/diagnostics;
3. filters/orders them;
4. resolves only numbered PDFs inside the configured part range as merge inputs;
5. prompts only for encrypted PDFs that can actually reach the engine;
6. validates the complete expected part range while retaining warnings for excluded PDF-like files;
7. refuses missing/duplicate or selected-input safety failures;
8. runs the PDF merge engine with the resolved order;
9. validates the generated output; and
10. prints the **actual output path returned by the engine**.

When overwrite is disabled and the requested destination already exists, the engine can create a versioned path such as `Book-Master_v2.pdf`. The CLI prints that real path rather than claiming the originally requested file was written.

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

The command discovers DOCX files for diagnostics, passes only numbered files inside the configured range to the automatic merge engine, validates the complete expected part set, merges in the resolved order, validates the resulting OOXML package, and prints the actual output path returned by the engine. It does not silently switch to LibreOffice or Word.

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

Run an explicit external-office round-trip on one DOCX and emit measured structural/content/risk evidence.

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

The command prints JSON containing source/output file hashes, structural snapshots, privacy-safe visible-text fingerprints, risk findings, newly introduced risk categories, `structure_matches`, `content_matches`, and `accepted`.

The structural snapshot currently covers body paragraph/table counts, inline shapes, sections, headings, and header/footer paragraph/table counts. Content evidence contains SHA-256 fingerprints for visible body paragraph text, body table-cell text, header text, and footer text; the visible manuscript text itself is not serialized in the evidence.

`accepted=true` currently requires:

1. matching measured structural snapshots;
2. matching measured visible-text content fingerprints; and
3. no new risky-construct category in the round-tripped output.

The command returns `0` for measured acceptance and `2` for a structurally valid output that does not meet those measured structural/content/risk criteria. Native-tool launch, timeout, source-integrity, or invalid-output failures are treated as errors.

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
- per-document relative source/output paths, error state, file hashes, structural snapshots, visible-text fingerprints, risk findings, and measured acceptance evidence.

The serialized corpus report rewrites source/output locations to corpus-relative paths so workstation/user directory information is not automatically embedded in the report. Known corpus/output roots in recorded per-item errors are also replaced with `<corpus>`/`<evidence>` placeholders. Third-party error text can still contain other sensitive information and should be reviewed before sharing.

The generated round-trip DOCX files still contain the document content and therefore remain private unless sanitized. Hashes/fingerprints are identifiers derived from the content and should also be shared intentionally.

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

The preset is stricter than a generic project: both expected manuscript kinds must be ready for Parts 1–120 for the dry run to return success. Automatic manuscript input still follows the same numbered/in-range rule, so unrelated PDF/DOCX files are not appended merely because they live under the source tree.

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

Project JSON is saved atomically. When later loaded, publication-sensitive field types and policy values are validated; for example a string value such as `"overwrite": "false"` is rejected rather than being interpreted as truthy Python data.

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

- PDF/DOCX **resolved merge-input** counts and readiness;
- missing/duplicate parts;
- `ready_for_available_kinds`;
- companion and ignored counts;
- storage estimates/free-space status;
- ordered PDF/DOCX merge-input paths;
- expected output paths;
- DOCX conflict count;
- `pdf_diagnostics` and `docx_diagnostics`, including warnings for discovered-but-excluded unnumbered/out-of-range material.

If the project output folder is strictly nested under a configured source root, that output subtree is excluded from project discovery so prior publications/staging files are not fed back into a later run.

When `selected_files` is populated, the persisted reviewed selection/order is authoritative and can intentionally contain unnumbered front/back matter. Those explicitly selected files remain subject to zero-byte, encryption, source-integrity, and engine validation checks.

Full run:

```bash
docmergeforge merge --project "./Book.json"
```

Encrypted PDF passwords are collected interactively only for PDFs that are part of the resolved project merge input. Excluded old/out-of-range encrypted PDFs do not trigger unnecessary password prompts.

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

The command scans the source folder, selects source documents by kind, performs the relevant comparison, and prints JSON evidence. Comparison is a review tool rather than the automatic merge-input resolver; interpret its broad source evidence accordingly.

## Encrypted-PDF interaction

For commands that execute a PDF merge/project run, each encrypted PDF that can actually reach the merge engine is prompted separately:

```text
Password for encrypted PDF <path>:
```

A wrong password produces a retry message. Password input is hidden by the terminal. Ctrl+C cancels the operation. Password dictionaries are cleared at the end of command execution.

The plain `validate` command does not collect passwords. A selected/automatic encrypted PDF inside the requested part range is therefore reported as not ready; an encrypted file excluded from automatic merge input can remain a non-blocking review warning instead of demanding an irrelevant password.

## Automation guidance

For reliable scripting:

- use `--dry-run` before project publication;
- inspect exit codes, not only stdout text;
- parse JSON for `validate`, project dry runs, `fidelity-capabilities`, `fidelity-roundtrip`, `fidelity-corpus`, `recover-output`, `audit`, and `compare`;
- review `diagnostics`/`pdf_diagnostics`/`docx_diagnostics`, especially unnumbered/out-of-range warnings;
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
| `validate` | Discover and validate expected numbered parts plus diagnostics |
| `pdf` | Direct numbered/in-range PDF merge |
| `docx` | Direct numbered/in-range portable DOCX merge |
| `fidelity-capabilities` | Report fidelity detection/automation/production states |
| `fidelity-roundtrip` | Run explicit one-file LibreOffice/Word DOCX acceptance evidence |
| `fidelity-corpus` | Run privacy-safe local external-office acceptance across a DOCX corpus |
| `sql-preset` | Guided SQL Full Mastery 120-part publication |
| `project-create` | Create reusable JSON project |
| `merge` | Dry-run or execute project |
| `recover-output` | Recover interrupted journaled publication |
| `audit` | Local manuscript audit |
| `compare` | Compare merged output with source evidence |
