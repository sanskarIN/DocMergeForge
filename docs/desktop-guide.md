# Desktop User Guide

The DocMergeForge desktop application is a PySide6 interface for guided publication assembly. It provides project setup, source discovery, order review, guarded saved-project source synchronization, validation/preflight, merge execution, progress/cancellation, reports, audit/compare tools, recent-project handling, recovery checkpoints, settings, help/support, and the SQL Full Mastery preset.

Start it from an installed environment:

```bash
docmergeforge-gui
```

## First launch

On first use, the application can show onboarding information explaining the core safety model:

- PDF and DOCX manuscripts are handled independently;
- source/companion code is not merged into manuscripts;
- originals should be retained;
- validation/preflight should be completed before publication;
- output promotion is transactional;
- interrupted publication may require explicit recovery.

First-run completion state is persisted so normal launches can move directly to the main experience.

## Home screen

The desktop home surface exposes the primary workflows, including:

- create/open a normal merge project;
- synchronize a saved project's selected source list;
- SQL Full Mastery guided preset;
- validation;
- publication audit;
- output comparison;
- recovery/resume entry points;
- recent projects;
- settings;
- help;
- support;
- About.

## Create a project

A project records the repeatable publication configuration. Typical setup fields include:

- project name;
- one or more source locations;
- output location;
- expected start/end part numbers;
- PDF settings;
- DOCX settings;
- output naming/profile behavior.

Choose an output directory that is local/reliable, writable, and large enough for temporary/staged outputs and rollback backups.

## Select sources

DocMergeForge scans configured source locations and classifies discovered files as:

- PDF manuscript;
- DOCX manuscript;
- companion/source material;
- other/ignored.

The source-selection experience should be used to confirm that the intended manuscript files are present and that unrelated files are not being mistaken for publication parts.

## Review document order

Before merging, use the order editor to inspect the exact source sequence.

The ordering UI supports keyboard-driven operations and explicit accessible names/descriptions. Supported actions include sorting, moving items, undo/redo, locking/restoring order, and returning to automatic order where applicable.

Important rules:

- verify Part 2 appears before Part 10;
- do not assume Explorer/Finder folder display order is the merge order;
- keep PDF and DOCX series internally consistent;
- if manual ordering is used, save the project so the selection is reproducible.

## Synchronize a saved project's sources

Use **Synchronize Project Sources** when a saved project's source folders have changed and you want to rebuild its explicit `selected_files` list from the numbered PDF/DOCX material currently present.

The desktop workflow uses the same synchronization planner and guarded persistence path as the CLI. It does not invent a second selection algorithm.

Desktop synchronization works as follows:

1. Choose **Synchronize Project Sources** and select the saved project JSON.
2. DocMergeForge loads the project and its exact SHA-256 content revision from one byte snapshot.
3. Current project sources are scanned using the maintained nested-output exclusion rules.
4. A read-only preview shows current/proposed counts, additions, removals, reordering, same-kind duplicate part numbers, missing expected parts, and the complete proposed order.
5. Same-kind duplicate numbered candidates make the proposal ambiguous, so **Apply synchronization** is disabled until those duplicates are resolved and a new preview is created.
6. Missing parts remain visible but do not by themselves make metadata synchronization unsafe. A partially assembled project can therefore be synchronized while still being unready for publication.
7. If the proposal contains removals, closing the preview is not enough authorization. After **Apply synchronization**, a second confirmation lists the paths that would be removed from `selected_files`.
8. Approved synchronization writes a versioned backup of the project JSON and applies through the exact-revision stale-write guard.
9. If the project changed on disk after it was loaded, the write is refused. Reopen the project and review a fresh proposal instead of retrying a stale one.

Synchronization changes project metadata only. It never deletes, renames, moves, merges, or converts manuscript source files. A removal means only that a path is removed from the saved project's `selected_files` list.

Automatic synchronization intentionally proposes only numbered PDF/DOCX files inside the configured expected range. Manually selected covers, prefaces, appendices, legal pages, unnumbered front/back matter, or deliberately out-of-range material can therefore appear as removals. Review every removal before approving it.

A successful synchronization also does **not** mean the project is publication-ready. Run normal dry-run/preflight afterward and resolve missing parts, encrypted-input requirements, corrupt documents, storage issues, output conflicts, and other blocking conditions before publication.

CLI equivalents are documented in [Project Synchronization](project-sync.md):

```bash
docmergeforge project-sync --project "./Book.json"
docmergeforge project-sync --project "./Book.json" --apply
```

CLI removals require the separate `--allow-removals` flag; the desktop uses a separate confirmation dialog for the same safety reason.

## Validate and preflight

The desktop workflow performs preflight before a project merge. Evidence includes:

- detected PDF/DOCX counts;
- missing parts;
- duplicate parts;
- ordered input lists;
- expected outputs;
- DOCX conflict count;
- source/temporary/projected/safe-required storage estimates;
- current free bytes;
- destination writeability.

A failed preflight is not a cosmetic warning. Resolve blocking conditions before starting a production run.

## Encrypted PDFs

When encrypted PDF inputs are selected, the desktop application can request passwords locally. Password handling is intentionally memory-only for the active operation.

Do not place passwords into project names, filenames, notes, diagnostic messages, or exported reports.

## PDF publication settings

Project PDF settings can include behavior such as:

- part bookmarks;
- title/author/edition metadata;
- generated title page;
- visible table of contents;
- page numbering and starting number;
- header/footer text;
- watermark text;
- optimization mode.

The PDF engine validates the completed file by reopening it and verifying expected page evidence.

## DOCX publication settings

Project DOCX settings can include:

- start each part on a new page;
- preserve sections;
- fidelity mode;
- generated part headings;
- TOC field creation;
- style conflict policy;
- numbering conflict policy;
- header/footer text;
- continuous page numbering.

Portable OOXML is the supported production path in the current codebase. High-fidelity LibreOffice/Word adapters must not be assumed complete just because the external office application is installed.

## Run the merge

When a project is ready, start the merge from the desktop workflow. The application service coordinates discovery, validation, source-integrity capture, document generation, output validation, report/checksum creation, source revalidation, and publication promotion.

During execution, the progress interface communicates the active stage and exposes cancellation where supported.

## Cancellation behavior

Cancellation checks exist through later PDF/DOCX finalization stages, not only between source files. A cancelled run should not publish a half-updated mixed-format publication bundle.

Cancellation does not mean manually terminating filesystem operations or deleting staging directories. If the process is forcibly killed during final promotion, use the recovery workflow afterward.

## Transactional publication

For full project runs, final manuscript outputs and generated publication evidence are staged before a single promotion boundary.

This protects against cases such as:

- PDF completes but DOCX fails;
- both manuscripts complete but report generation fails;
- source files change during the run;
- cancellation occurs before promotion;
- overwrite promotion needs rollback.

Existing outputs may be temporarily backed up inside the transaction staging directory until the new bundle is fully committed.

## Recovery and resume

The desktop project system includes recovery checkpoints for interrupted work. Publication-promotion recovery is a separate filesystem safety mechanism.

If the output folder contains an interrupted `.docmergeforge-staging-*` journal, do not delete it manually. Use the recovery command or the corresponding desktop recovery path so recorded backups/fingerprints are honored.

CLI equivalent:

```bash
docmergeforge recover-output --output-dir "./Master"
```

See [Publication Recovery](recovery.md).

## Reports and evidence

After a successful project publication, use the reports area to inspect generated evidence. Depending on configuration/preset, this may include manifests, checksums, companion indexes, reports, and publishing checklists.

These files support repeatability and later verification. Archive them with the release outputs when appropriate.

## Audit

The publication-audit feature inspects PDF/DOCX content locally and reports findings without rewriting the originals.

CLI equivalent:

```bash
docmergeforge audit --input "./Book"
```

## Compare output

The compare workflow checks merged output evidence against discovered source evidence.

CLI equivalent:

```bash
docmergeforge compare \
  --input "./Book" \
  --pdf-output "./Master/Book.pdf" \
  --docx-output "./Master/Book.docx"
```

## Recent projects

Recent-project history provides a fast way to reopen existing work. A recent-project entry is a convenience pointer, not a backup. Keep project files and source folders in durable storage.

If a project path becomes unavailable, restore/move the project deliberately rather than recreating settings from memory.

## Settings

The settings UI exposes application/project preferences supported by the current desktop code. Accessibility metadata is attached to important path fields, checkboxes, spin boxes, reports, lists, synchronization previews, and progress controls so assistive technologies have explicit context.

Changes that affect publication behavior should be reviewed before the next merge, especially overwrite, ordering, naming, and fidelity choices.

## Accessibility

The desktop application includes automated headless accessibility checks and keyboard metadata, including:

- explicit accessible names/descriptions;
- label-to-field relationships where appropriate;
- keyboard operations in the order editor;
- named synchronization preview/action controls;
- named progress/report/recent-project controls.

Automated metadata checks do not replace human acceptance with real screen readers, high-contrast modes, scaling, reduced-motion expectations, and keyboard-only workflows. Those remain release-gate verification areas.

See [Accessibility](accessibility.md).

## Help and support

Use the built-in Help/Support/About surfaces for project identity and support information. Repository support references are also documented in [Support](support.md).

## SQL Full Mastery workflow

The SQL preset provides a guided 120-part path intended to assemble the complete PDF and DOCX editions while keeping companion code independent.

Recommended workflow:

1. select the SQL source folder;
2. choose the master-edition output folder;
3. run validation/preflight;
4. confirm Parts 1–120 are complete for required kinds;
5. review order;
6. inspect DOCX risk/conflict evidence;
7. run the preset;
8. inspect outputs/reports/checksums;
9. archive the evidence with the publication.

See [SQL Full Mastery Preset](sql-full-mastery-preset.md).

## Safe desktop operating checklist

Before clicking the final merge action:

- originals are backed up;
- project file is saved;
- saved project source selection has been synchronized/reviewed when source membership changed;
- source folders are correct;
- expected part range is correct;
- no missing/duplicate blocking errors remain;
- order has been reviewed;
- output folder is writable;
- storage preflight is sufficient;
- encrypted PDF passwords are available;
- DOCX fidelity risks are understood;
- overwrite behavior is intentional.

After completion:

- open the merged PDF/DOCX in your normal reader/editor;
- inspect generated evidence;
- run compare/audit where required;
- preserve checksums/manifest/report files;
- do not claim signed production packaging unless signing/notarization verification was actually completed.
