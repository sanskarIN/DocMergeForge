# FAQ

## What is DocMergeForge?

DocMergeForge is a local-first desktop and CLI application for discovering, ordering, validating, merging, and verifying large multi-part PDF and DOCX publications while keeping companion/source code independent.

## Does it merge PDF and DOCX into one mixed file?

No. PDF and DOCX are separate publication pipelines.

- PDFs merge into a PDF.
- DOCX files merge into a DOCX.
- Companion code is indexed separately.

This separation is intentional.

## Can it merge 120 parts?

Yes. The repository includes a dedicated SQL Full Mastery 120-part preset and an automated generated 120-part regression workflow.

A generated 120-part regression is not the same as proving every multi-gigabyte real-world manuscript; scale/fidelity acceptance remains a separate test.

## Does it support more or fewer than 120 parts?

Generic projects and direct CLI commands accept configurable inclusive part ranges such as:

```text
1-20
1-80
10-150
```

The SQL Full Mastery preset specifically expects Parts 1–120.

## How does it know Part 2 comes before Part 10?

It uses numeric part detection and natural sorting instead of raw lexical filename sorting.

## What filename patterns are recognized?

Common forms containing `part`, `chapter`, `volume`, and abbreviated `p`/`part` forms followed by a number are recognized.

Examples include `Part 1`, `Chapter_20`, `Volume-3`, and `P12`-style names.

## What happens if a part is missing?

Validation reports the exact missing part number and the set is not ready.

## What happens if two files are both Part 10?

That is a duplicate part and blocks numbered validation. Choose the authoritative source and remove/move the obsolete duplicate from scanned inputs.

## Can I manually reorder files?

Yes. The desktop project/order workflow supports reviewed selected-file ordering. Save the project after making intentional ordering choices.

## Can I disable natural sorting?

For direct `validate`, `pdf`, and `docx` CLI commands:

```bash
--no-natural-sort
```

Use it only when plain filename ordering is intentionally correct.

## Can I filter filenames?

Yes:

```bash
--pattern "Part *.pdf"
```

Filtering is case-insensitive against filenames in the current CLI implementation.

## Does DocMergeForge change my originals?

Normal merge workflows are designed to read/hash original sources and write new staged/final outputs. Original manuscript files are not rewritten as part of the merge.

Keep independent backups anyway.

## Does it detect if a source changes during a long merge?

Full project publication snapshots source/companion hashes and verifies that tracked files remain unchanged before final promotion.

## Are output files written atomically?

Individual engines use staged/atomic behavior, and full project publication adds a batch transaction so PDF, DOCX, reports, manifests, checksums, companion indexes, and checklists are promoted together.

## What if the PDF succeeds and the DOCX fails?

In a full project transaction, the PDF should not be published as a new final bundle while the later DOCX stage fails. Both formats are staged before the final publication boundary.

## What if report generation fails?

Reports/evidence are also staged before publication promotion, so report failure should not leave newly published manuscripts paired with stale evidence.

## What if the process is killed while final files are being replaced?

DocMergeForge writes a recovery journal before final-path mutation. Run:

```bash
docmergeforge recover-output --output-dir "./Master"
```

Do not manually delete `.docmergeforge-staging-*` folders after a crash.

## Why does recovery refuse to delete/restore a file?

Recovery is fail-closed. If a final file no longer matches the fingerprint recorded by the interrupted transaction, the application stops rather than deleting a possibly unrelated/manual replacement.

## What is a transaction journal?

`transaction.json` is recovery metadata written inside a hidden transaction staging directory. It records the promotion phase and enough per-file evidence to restore/remove interrupted outputs safely when filesystem state still matches expectations.

## Does DocMergeForge support encrypted PDFs?

Yes, supported merge/project paths can prompt for a password, verify it locally, and use it for the active run.

## Are PDF passwords saved?

No. Current password mappings are kept in memory and cleared after the operation. Project files do not store them.

## Why doesn't `validate` prompt for an encrypted PDF password?

The plain `validate` command is a discovery/numbered-set check and does not collect passwords. Merge/project workflows handle password collection when access is required.

## Does it support legacy `.doc`?

Not directly. `.doc` is detected with a warning. Create a separate `.docx` conversion using a trusted office suite; the original is not auto-converted.

## How good is DOCX fidelity?

Portable OOXML composition preserves many normal Word structures, but no library-only merger can guarantee perfect preservation of every advanced Word construct.

Complex fields, OLE objects, tracked changes, custom XML, some equations, content controls, external relationships, macros/legacy constructs, and complicated style/numbering interactions require special review.

## Does installing Microsoft Word make Word fidelity mode production-ready?

No. The current repository deliberately does not treat the Word automation adapter as production-ready merely because Word is installed.

## Does installing LibreOffice make the LibreOffice fidelity mode production-ready?

No. The external suite may be capability-detected, but the high-fidelity automation adapter still needs implementation and real acceptance before that mode can be claimed as production-ready.

## Does DocMergeForge create a table of contents?

PDF and DOCX settings include publication helpers such as visible PDF TOC/front matter and DOCX TOC field creation where configured. Final TOC appearance/update behavior should be reviewed in the target viewer/editor.

## Can it add page numbers, headers, footers, or watermark?

PDF settings support page-number and overlay-style publication options. DOCX settings include header/footer and continuous page-numbering behavior.

Use project settings and review the final rendered output.

## Does it merge source-code ZIP files?

No. Companion archives are indexed and hashed but never merged into the manuscript.

## Does it extract ZIP/RAR/7z code archives?

No, not for companion indexing/merge. Avoiding extraction is an intentional safety/integrity choice.

## What companion archive extensions are recognized?

Currently `.zip`, `.7z`, `.rar`, `.tar`, `.gz`, and `.tgz`.

## What is the companion code index?

A Markdown/JSON record of companion artifact paths, detected part numbers, sizes, and SHA-256 hashes.

## What does dry-run do?

A project/preset dry run performs preflight without creating the final books. It reports readiness, order, expected outputs, DOCX conflict count, companion/ignored counts, and storage evidence.

## How is required disk space estimated?

Current preflight uses source size as a projected-output baseline, adds 125% temporary space and a 128 MiB safety margin, then compares against filesystem free space.

It is an estimate, not a universal worst-case bound.

## Why does preflight create a temporary file in my output folder?

It performs a writeability probe to ensure the destination can actually host transaction staging. The probe is removed immediately afterward.

## Does it work on Windows?

The source application and Build Smoke/package workflow include Windows support. Production distribution still requires signed packaged-app acceptance before making a fully signed Windows release claim.

## Does it work on macOS?

The source application/build workflow includes macOS. Production distribution requires real app signing/notarization/Gatekeeper acceptance.

## Does it work on Linux?

The source application/build workflow includes Linux. Compatibility depends on the Linux runtime/distribution baseline; PySide6 may require system libraries such as `libegl1` on minimal Debian/Ubuntu environments.

## Can I build a Windows EXE from Linux?

The supported PyInstaller process is native-platform oriented. Build Windows on Windows, macOS on macOS, and Linux on Linux (or equivalent native CI runners).

## How do I build the desktop app?

```bash
pip install -e ".[build]"
python scripts/build_desktop.py --check
python scripts/build_desktop.py
```

One-file variant:

```bash
python scripts/build_desktop.py --one-file
```

## Are CI packages signed?

No. The current Package Desktop workflow deliberately names uploaded archives as `unsigned`.

## Is DocMergeForge `v1.0.0` production-ready?

The project remains pre-stable until its full release acceptance matrix—including real stress/fidelity/accessibility/recovery/package signing acceptance—is completed and recorded.

## What CI checks exist?

Major workflows include:

- Quality;
- 120-Part Regression;
- Build Smoke;
- Security/CodeQL;
- Package Desktop;
- manual Stress Acceptance.

## What does the accessibility smoke test prove?

It verifies important accessible names/descriptions, label relationships, and keyboard metadata in representative desktop dialogs on the configured CI platforms.

It does not replace human testing with screen readers, high-contrast modes, scaling, and keyboard-only workflows.

## Does the application upload my manuscript?

Core behavior is local-first and does not require manuscript upload/account access. External cloud-sync/backup services you use on the same folders are outside DocMergeForge's control.

## What information might diagnostics contain?

They can contain file paths, filenames, platform/version information, and technical errors. Review diagnostics before public sharing. Passwords/manuscript body text should not be intentionally logged.

## Where should I report a bug?

Use the GitHub repository for non-sensitive bugs. Do not attach confidential manuscripts/passwords.

For private security issues, follow [`SECURITY.md`](../SECURITY.md).

## Where can I find the full docs?

Start with [Documentation Index](README.md).
