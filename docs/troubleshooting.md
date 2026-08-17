# Troubleshooting

Use this guide to diagnose common DocMergeForge problems without bypassing validation or destroying recovery evidence. For production operations, also see [Operator Runbook](operator-runbook.md) and [Publication Recovery](recovery.md).

## First diagnostic steps

Before changing files/settings:

```bash
docmergeforge --help
```

If using a project:

```bash
docmergeforge merge --project "./Project.json" --dry-run
```

For numbered sources:

```bash
docmergeforge validate --input "./Sources" --parts 1-120
```

Record the exact error/exit code before attempting a fix.

---

## `docmergeforge: command not found`

Likely causes:

- virtual environment is not activated;
- package was not installed;
- terminal session predates installation;
- wrong Python environment is active.

Fix:

```bash
python -m pip install -e .
```

Then activate the correct environment and run:

```bash
docmergeforge --help
```

Check which Python/pip are active:

Windows:

```powershell
Get-Command python
Get-Command docmergeforge
```

macOS/Linux:

```bash
which python
which docmergeforge
```

---

## GUI does not start

Run from a terminal so Qt/import errors remain visible:

```bash
docmergeforge-gui
```

Check:

- PySide6 installed through normal project dependencies;
- graphical desktop/session available;
- Qt system runtime libraries present;
- packaged build contains Qt plugins/resources.

On minimal Debian/Ubuntu, an error like:

```text
ImportError: libEGL.so.1: cannot open shared object file
```

can be fixed by installing:

```bash
sudo apt-get update
sudo apt-get install -y libegl1
```

This same dependency is installed in Linux CI before UI/accessibility tests.

---

## A part is missing

Symptoms:

```json
"missing": [17]
```

Check:

1. Does the file actually exist under a scanned root?
2. Does the filename contain a supported part pattern?
3. Is the extension `.pdf`/`.docx`?
4. Did a `--pattern` filter exclude it?
5. Is the expected range correct?
6. Is the part stored outside the project source folders?

Supported naming concepts include `Part`, `Chapter`, `Volume`, and abbreviated `P/Part` followed by a number.

After correcting the source/filename, rerun validation.

---

## A file exists but has no detected part number

Rename a copy/source appropriately so the number is explicit.

Prefer:

```text
Book - Part 017.docx
```

over ambiguous names such as:

```text
Final Chapter.docx
```

Do not fake readiness by changing the expected range if the publication is genuinely missing a part.

---

## Duplicate part number

Symptoms:

```json
"duplicates": {
  "10": ["...Part 10...", "...Part 10 revised..."]
}
```

A duplicate is blocking.

Fix:

1. identify the authoritative source;
2. move obsolete/draft duplicates outside all scanned roots;
3. keep them in archive/backup storage if needed;
4. rerun validation.

Do not rely on filename sort order to choose one automatically.

---

## Part 10 is before Part 2

Natural sorting should be enabled by default in direct CLI discovery.

Ensure you did not pass:

```bash
--no-natural-sort
```

For a saved project with explicit selected order, inspect/reorder selected files in the desktop order editor because project selection can intentionally preserve manual order.

---

## Pattern filter returns too few files

Example:

```bash
--pattern "Part *.pdf"
```

The filter is applied to filenames. It may exclude files named `Chapter 1.pdf` or PDFs in the source tree that use another naming convention.

Remove/adjust the filter and rerun validation.

---

## Legacy `.doc` detected

DocMergeForge does not auto-convert `.doc`.

Fix safely:

1. keep the original `.doc`;
2. open it in trusted Microsoft Word/LibreOffice;
3. save a separate `.docx` copy;
4. inspect the conversion;
5. place the approved `.docx` in the source workflow;
6. rerun validation.

---

## Encrypted PDF requires password

Direct/project PDF merge requires a legitimate password.

The CLI prompts:

```text
Password for encrypted PDF ...:
```

If the password is unavailable, Ctrl+C cancels the operation (typically exit code `130`).

Password bypass/cracking is not a DocMergeForge feature.

---

## Encrypted PDF password is rejected

Verify the same password/file in a trusted PDF reader.

Possible causes:

- password typo;
- wrong version of the PDF;
- file changed since password was provided;
- different owner/user-password expectations in the source file;
- damaged encryption dictionary.

Do not put the password in project JSON or support logs.

---

## `validate` fails on encrypted PDF although merge can prompt

The plain `validate` command does not collect passwords. Project/direct merge paths handle interactive password collection.

Use a project dry run through:

```bash
docmergeforge merge --project "./Project.json" --dry-run
```

when encrypted inputs need password-aware readiness.

---

## PDF inspection warning

Discovery can attach:

```text
PDF inspection failed: ...
```

The scanner keeps the file but page-count evidence may be unavailable.

Open the PDF independently. If damaged, create/obtain a valid source copy rather than expecting the merge to repair arbitrary corruption.

---

## PDF merge page validation failed

The engine reopens the temporary result and checks expected page count.

Do not manually move the temporary file into place.

Investigate:

- damaged source page structures;
- unexpected reader behavior;
- generated front matter/page count logic;
- source changing during merge;
- library regression.

Create a minimal synthetic reproduction for a bug report.

---

## PDF output unexpectedly encrypted

`validate_output` rejects a final PDF that unexpectedly becomes encrypted.

DocMergeForge does not intentionally encrypt the output merely because an input was encrypted/unlocked. Treat this as a validation failure and investigate before release.

---

## DOCX input validation fails

The engine validates OOXML package structure before composition.

Safe recovery path:

1. preserve the original source;
2. open it in Microsoft Word or LibreOffice;
3. if the application repairs it, save a **new** corrected `.docx` copy;
4. inspect the copy;
5. use the corrected copy in the project;
6. rerun preflight.

Do not overwrite the only original during repair.

---

## DOCX output says Word found unreadable content / repair prompt

Treat the output as failed human acceptance even if automated package validation passed.

Investigate:

- source package validity;
- style/numbering conflicts;
- relationships/media/custom XML;
- section/header/footer complexity;
- advanced fields/content controls/OLE/equations;
- docxcompose/library edge case.

Use a smaller subset/binary search of source parts to locate the first problematic append.

---

## DOCX style conflicts block merge

If project policy is:

```text
style_conflict_policy = error
```

any detected style collision blocks portable composition.

Options:

- inspect/standardize source styles;
- intentionally use `prefer_master` if that policy is acceptable;
- keep `error` for strict review;
- do not invent an unsupported policy string.

---

## DOCX numbering conflicts block merge

If:

```text
numbering_conflict_policy = error
```

numbering collisions block the merge.

Use `remap` only when its portable behavior is appropriate and human-test lists/numbering afterward.

---

## High-fidelity LibreOffice/Word mode is refused

This is intentional if the adapter is not marked production-ready.

Installing the external office suite does not make the DocMergeForge integration complete.

Use portable mode or contribute/test the adapter rather than bypassing the fidelity gate.

---

## Table of contents is not updated in final DOCX

DocMergeForge inserts a TOC field when configured. Word/LibreOffice may need to update/recalculate the field after opening.

In Word, use the normal field/TOC update action and review the result before publication.

---

## Page numbering/header/footer changed unexpectedly in DOCX

Review project settings:

```text
preserve_sections
continuous_page_numbering
header_text
footer_text
```

Section-linked headers/footers/page numbering are complex OOXML behavior. Compare a minimal multi-section sample and decide whether preserve/normalize behavior matches the desired master-book design.

---

## Not enough disk space

Preflight reports required/free bytes and blocks insufficient storage.

Fix:

- free space;
- use a larger local output filesystem;
- remove obsolete build artifacts (not transaction recovery evidence);
- allow extra margin beyond the estimate.

Remember overwrite publication may temporarily retain old final files as rollback backups.

Rerun dry-run after freeing/moving storage.

---

## Output folder is not writable

Preflight creates/removes a write probe. Failure raises an output-access error before expensive merge work.

Check:

- directory/parent permissions;
- read-only drive;
- network share permissions/availability;
- ransomware/security controls;
- invalid/missing mount;
- path reserved by another process.

Choose an appropriate user-writable destination. Avoid elevating to Administrator/root just to hide an unexplained permissions issue.

---

## Write-probe file remains after a crash

Normal cleanup removes `.docmergeforge-write-probe-*`.

If the process was killed at the exact probe moment, a zero/small probe file could remain. Ensure no active DocMergeForge process is using it, then remove the probe if it is clearly the write-probe artifact.

This is different from `.docmergeforge-staging-*`, which may contain critical recovery backups and must not be casually deleted.

---

## An interrupted publication transaction is detected

Do not manually delete:

```text
.docmergeforge-staging-*
```

Run:

```bash
docmergeforge recover-output --output-dir "/path/to/output"
```

A `promoting` journal is evaluated for rollback. A stale `committed`/`rolled-back` journal can be cleaned.

See [Publication Recovery](recovery.md).

---

## Recovery says fingerprint mismatch / refuses to proceed

This means a current final file no longer matches the interrupted transaction evidence.

Possible causes:

- someone opened/saved/replaced the file after crash;
- another process copied a different file to the same path;
- transaction evidence is damaged/incomplete.

Do **not** disable the fingerprint check or delete the backup folder.

1. back up the whole output directory;
2. identify the current final hash/size;
3. inspect the transaction backup/journal;
4. determine the authoritative version manually;
5. restore/remove only with proof.

---

## Recovery says expected backup/staging evidence is unavailable

The recovery engine cannot prove a safe rollback.

Likely causes:

- manual cleanup after crash;
- antivirus/sync tool moved/deleted hidden files;
- filesystem damage;
- external process partially changed transaction contents.

Preserve remaining evidence and restore from independent backups if needed.

---

## New merge refuses because a transaction is pending

This is deliberate. Recover/resolve the pending output transaction first.

Running a new merge on top of unresolved rollback evidence could destroy the previous publication state.

---

## Final validation failed

The staged output is not considered complete and should not be promoted as a successful project result.

Original source files remain unchanged by normal merge logic.

Investigate the specific PDF/DOCX/report/source-integrity error and rerun from a fresh preflight.

---

## Source integrity violation

A tracked PDF/DOCX/companion changed during the run.

Possible causes:

- editor autosave;
- sync process replaced file;
- source-generation process was still running;
- user copied a new version over the file;
- storage corruption.

Fix:

1. stop modifying sources;
2. choose/freeze authoritative versions;
3. rerun discovery/preflight;
4. restart publication.

Do not continue with staged outputs from the failed mixed-source run.

---

## Reports fail after documents seem merged

In a full project, reports are staged inside the same publication transaction. If report generation fails before promotion, newly staged manuscripts should not replace the old final publication bundle.

Fix the reporting/path/permission problem and rerun the project.

---

## Direct merge behaves differently from project merge

Direct `pdf`/`docx` commands are simpler one-format workflows. Full project runs additionally provide:

- broader tracked source integrity;
- combined PDF/DOCX transaction boundary;
- reports;
- manifest;
- checksums;
- companion index;
- publishing checklist.

For production master-edition assembly, prefer a project/preset when you need the complete evidence bundle.

---

## `compare` requires an output option

At least one is required:

```bash
--pdf-output FILE.pdf
--docx-output FILE.docx
```

Example:

```bash
docmergeforge compare --input "./Book" --pdf-output "./Master/Book.pdf"
```

---

## PDF compare page count differs after adding front matter

The comparison sums source pages. If the final PDF intentionally includes generated title/TOC pages, output pages can exceed raw source-page sum.

Use engine validation and configured-front-matter knowledge to interpret this difference.

---

## DOCX compare counts differ

Generated part headings, TOC structure, page breaks/sections, and header/footer changes can make output structural counts differ from raw source totals.

Use counts as review evidence, not a universal equality requirement.

---

## Audit reports `stale-next-part`

The audited text contains a `Next: Part 121`-style reference.

For a 120-part final series, review whether this is stale continuation text and correct the source/final manuscript through the normal editorial process.

---

## Audit reports many emails / multiple GitHub URLs

These are consistency review signals. Confirm whether multiple contact identities are intentional before editing publication content.

---

## Accessibility smoke fails on Linux with `libEGL.so.1`

Install:

```bash
sudo apt-get update
sudo apt-get install -y libegl1
```

Then rerun:

```bash
python scripts/check_accessibility.py
```

---

## Accessibility smoke reports missing accessible name/shortcut

This is an application regression. Do not weaken/remove the smoke check. Add the correct metadata/keyboard behavior to the control and extend tests if needed.

---

## `build_desktop.py --check` says invalid build root

The selected root must contain at least:

```text
pyproject.toml
src/docmergeforge/ui/main.py
```

Run from the repository root or pass:

```bash
python scripts/build_desktop.py --check --root "/correct/repository/path"
```

---

## PyInstaller is required

Install build dependencies:

```bash
pip install -e ".[build]"
```

Then:

```bash
python scripts/build_desktop.py --check
python scripts/build_desktop.py
```

---

## Packaged app builds but will not start

Launch from a terminal where possible and inspect errors.

Check:

- Qt platform/plugin dependencies;
- resource paths/branding;
- missing hidden imports/package data;
- OS/runtime compatibility;
- executable permissions on Linux/macOS;
- security/Gatekeeper/SmartScreen behavior;
- one-file temporary extraction behavior.

Reproduce on a clean machine/VM and fix shared packaging configuration rather than adding machine-specific manual files to `dist`.

---

## Windows says app is untrusted / SmartScreen warning

Current CI packaging artifacts are unsigned development builds. This is expected behavior for an unsigned binary and is not solved by hiding the warning.

Production distribution requires actual code signing and acceptance.

---

## macOS blocks the app

Current CI archive is unsigned/not notarized. Production distribution requires Developer ID signing/notarization/Gatekeeper verification.

Do not tell end users to bypass Gatekeeper as a substitute for completing release signing.

---

## Linux packaged app fails on another distro

PyInstaller Linux compatibility depends on build/runtime baseline. A binary built on a new Ubuntu/glibc environment may not be universally portable.

Define/test your supported distro baseline or use an appropriate Linux packaging strategy.

---

## CI Quality fails before tests run

Quality order is roughly:

1. Ruff;
2. Black;
3. strict mypy;
4. pytest.

A failure in an earlier gate can skip later evidence. Fix the first concrete issue and rerun; do not claim tests are green if they never ran.

---

## CI fails only on Ubuntu Qt import

Distinguish environment dependency from UI application behavior. The repository installs `libegl1` in Linux workflows that import PySide6.

Do not delete UI/accessibility tests to make CI green.

---

## Need to report a bug

See [Support](support.md).

Include version/commit, OS, command, exit code, sanitized error, and a minimal synthetic reproduction. Never publish passwords or confidential manuscripts.
