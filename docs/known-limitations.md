# Known Limitations

DocMergeForge is currently a pre-stable project. The core merge, validation, project, transactional publication, recovery, reporting, desktop, CLI, CI, and packaging functionality is implemented, with increasingly strong automated acceptance. Several areas still remain intentionally excluded from a stable `v1.0.0` claim until their own evidence exists.

This page is deliberately conservative. It should be updated when limitations are actually removed and verified.

## DOCX fidelity is not universally perfect

Portable OOXML composition is the current production-supported DOCX mode. It can preserve normal document structure effectively, but it cannot guarantee perfect behavior for every Microsoft Word construct/application-specific rendering detail.

Features requiring special review can include macros/legacy macro-enabled content, OLE/embedded objects, tracked changes, content controls, custom XML, complex fields, equations, external relationships, unusual style inheritance, complex numbering restarts, section/header/footer interactions, and application-specific layout behavior.

The risk scanner and acceptance fingerprints surface more of those risks, but detection is not equivalent to perfect rendering preservation. Always keep originals and perform human review in the intended office editor.

## LibreOffice fidelity adapter is implemented for round-trip acceptance, not production merge

DocMergeForge has an explicit source-preserving LibreOffice DOCX round-trip adapter, capability reporting, measured structural/content/risk evidence, and a GitHub Actions lane that installs LibreOffice Writer and exercises a real synthetic round trip on Ubuntu.

This still does not certify a complete native multi-document LibreOffice merge engine or universal fidelity. Installing LibreOffice does not automatically upgrade portable mode, and the normal merge gate keeps `libreoffice` non-production.

Production certification still requires true multi-document semantics plus representative real-world corpus acceptance on every claimed LibreOffice platform/version.

## Microsoft Word native merge exists as an acceptance prototype, not production mode

DocMergeForge now has both a source-preserving Word round-trip adapter and a separate Word-native multi-document acceptance prototype. The native prototype uses COM, ordered `Range.InsertFile(...)`, real section breaks, source hashes, validated temporary output, measured structure/text/section/page-number evidence, and exact Word-process identity cleanup boundaries.

The Word process created by native merge is identified by PID, `WINWORD` process name, and process start-time fingerprint. Failure/timeout cleanup refuses broad process termination and only acts when that exact identity still matches. A nominally successful merge is rejected if Word required forced termination instead of shutting down normally.

These are implementation and regression safeguards, not production certification. Detecting PowerShell or implementing COM code does not prove Word is installed, licensed, compatible with unattended execution, or correct for every supported document.

`word.production_ready` therefore remains `false`.

Production certification still requires a real passing controlled Windows/Word run, a real forced-timeout cleanup run, representative private multi-document corpus testing, repair-prompt/manual rendering review, exact supported Word/Windows version evidence, packaged-app integration if distributed, and regression coverage for discovered defects.

See [Microsoft Word Native Merge Acceptance](word-native-merge-acceptance.md).

## Measured Word evidence is not visual equivalence

Word-native acceptance currently compares aggregate structure, privacy-safe visible-text fingerprints, section layout/linkage fingerprints, page-number section semantics, source hashes, and newly introduced OOXML risk categories.

The section evidence includes orientation, page geometry, margins, header/footer distances, section start behavior, first-page behavior, and normal/first/even header/footer linkage. Page-number evidence currently includes `w:start`, `w:fmt`, `w:chapStyle`, and `w:chapSep` in global merged-section order.

Those checks can detect important silent loss, but they do not prove identical pagination, line wrapping, font substitution, floating-object placement, rendered fields/TOC/page numbers, chart/SmartArt appearance, every tracked-change/content-control behavior, Office add-in behavior, or universal equivalence across Word builds.

## A successful DOCX round-trip is not visual equivalence

`docmergeforge fidelity-roundtrip` records selected structural/content/risk evidence for one source-preserving external-office round trip. It does not compare rendered pages pixel-for-pixel, prove font availability, recalculate every field exactly, or certify all application-specific layout decisions.

A single synthetic fixture or one real manuscript is insufficient to flip an external adapter to `production_ready=true`.

## PDF human rendering acceptance is still required

PDF output is structurally validated/reopened and page evidence is checked, but automated validation cannot guarantee every visual detail in every PDF viewer.

Human QA should still review generated front matter/TOC, bookmarks, overlays/page numbering, mixed page sizes/orientations, transparency/images/fonts, encrypted-source behavior, and representative part boundaries.

## Synthetic 120-part regression is not multi-gigabyte proof

The repository continuously tests a generated 120-part workflow. This proves useful ordering/validation/merge/regression behavior at that fixture scale.

It does not justify claims such as “tested with any file size,” “multi-gigabyte production accepted,” or “memory usage guaranteed for all books.”

The manual Stress Acceptance workflow exists to collect explicit measured evidence at larger configured scales. No measured multi-gigabyte acceptance is currently claimed.

## Controlled forced-process recovery is verified; physical failure modes are not

Recovery is no longer limited to simulated journals. `Recovery Acceptance` kills a real child process with `os._exit()` at three promotion boundaries on Windows, macOS, and Ubuntu, then verifies that public recovery restores the previous publication and that the OS-level output lock can be reacquired. Run `32022863454` passed all three cases on all three platforms.

That evidence still does **not** reproduce every physical/environmental failure mode. Separate acceptance remains for power loss, storage-device removal, filesystem corruption, and multi-host/network-filesystem semantics when those environments are claimed.

## Linux real disk-full recovery is verified; other filesystems remain separate

`Disk Full Acceptance` mounts an isolated 32 MiB Ubuntu tmpfs and writes/fsyncs through the real `atomic_output()` path until the kernel returns `ENOSPC`. Run `32023666826` verified the previous target remained unchanged and atomic `.part` residue was removed.

This is real filesystem-exhaustion evidence, not only injected exceptions. It does not prove identical behavior on NTFS, APFS, removable drives, network shares, or every Linux filesystem.

## Storage estimate is conservative, not a hard upper bound

Current storage preflight estimates projected output from source size, 125% temporary overhead, and a 128 MiB safety margin.

Actual needs can vary with document structure, compression, overwrite backups, filesystem behavior, and future features. Do not run high-value publication jobs with a nearly full disk merely because the estimate passes by a small margin.

## Network/removable filesystems require caution

The transaction model uses filesystem replacement/rename plus an OS-level advisory/exclusive lock. Behavior and support can differ on network shares, cloud-synced folders, removable drives, FUSE/virtual filesystems, and NAS/SMB configurations.

The local Windows/macOS/Linux recovery acceptance does not prove multi-host network-lock semantics. Prefer a reliable local filesystem for publication staging, then copy verified final artifacts to distribution storage unless direct-network acceptance is explicitly recorded.

## Accessibility is not fully human-accepted yet

Automated accessibility smoke passes key metadata/keyboard checks cross-platform, but complete accessibility acceptance requires real assistive-technology testing.

Open areas include Narrator/NVDA, VoiceOver, a supported Linux screen reader, keyboard-only full workflows, high contrast, display/text scaling, reduced motion, and difficult large-list/error states.

Do not equate “accessible names exist” with full accessibility certification.

## CI packaging artifacts are unsigned

Package Desktop currently builds native Windows/macOS/Linux PyInstaller applications, executes a packaged mixed PDF+DOCX smoke publication, creates archive SHA-256 sidecars, and uploads artifacts whose names explicitly contain `unsigned`.

No current documentation should claim Windows production code signing, macOS notarization, Linux package signing, or installer certification complete. Those require external credentials/platform acceptance not present in ordinary source CI.

## No finished native installer format is claimed

The current packaging helper produces PyInstaller onedir/one-file builds. CI distributes ZIP/TAR archives.

A finished MSI/MSIX/DMG/PKG/AppImage/deb/rpm/etc. distribution pipeline is not currently claimed.

## Native packaged execution is verified in CI; full interactive clean-machine acceptance remains

Package Desktop run `32023353227` built and executed the actual packaged application on Windows, macOS, and Ubuntu. The smoke initializes the Qt desktop stack and runs a real temporary mixed PDF+DOCX publication through the bundled engines, transaction layer, reports, manifest, and checksums.

That is stronger than packaging preflight or import-only smoke, but it is still automated CI acceptance. It does not replace human interactive testing on representative clean end-user machines for dialogs, encrypted-PDF entry, cancellation interactions, platform trust prompts, accessibility, and real manuscripts.

## `audit` is targeted, not a comprehensive publishing QA system

Current audit patterns focus on selected publication issues such as stale Part 121 references and contact/branding consistency signals. They do not replace grammar/spelling review, plagiarism/copyright review, legal review, full link checking, PDF accessibility tagging checks, metadata standards validation, or comprehensive publication QA.

## `compare` is evidence, not semantic equivalence

PDF comparison mainly uses page-count/page-range evidence. DOCX comparison uses structural counts such as paragraphs, tables, inline shapes, sections, and headings.

Intentional generated front matter/headings/TOC/sections can change counts. Human interpretation is required.

## Encrypted-PDF automation is interactive

Current CLI password collection is interactive. There is no documented non-interactive secret-provider CLI interface for unattended encrypted-PDF automation. Do not place passwords in shell scripts/project JSON as a workaround.

## Plain `validate` does not unlock encrypted PDFs

The validation command does not prompt for PDF passwords. Full merge/project paths handle password collection where required.

## Legacy `.doc` is not merged/auto-converted

Legacy `.doc` files generate a warning and require explicit external conversion to a separate `.docx` copy. This is intentional to avoid silently modifying source formats.

## Companion archives are not validated as code

DocMergeForge indexes/hashes companion code archives but does not extract them, build them, run tests, malware-scan them, resolve dependencies, check code licenses, or generate an SBOM. Software-release QA remains separate.

## Relative/absolute project paths are not magically portable

Project JSON stores paths as strings. Moving a project between Windows/macOS/Linux can require path changes or a consistent relative directory layout. Always run dry-run after moving/importing a project.

## No bit-for-bit reproducible binary build claim

Centralized PyInstaller arguments improve consistency, but exact binary bytes can vary with OS image, Python/dependency/PyInstaller versions, archive metadata, and signing timestamps. Record release commit/workflow/artifact hashes for provenance.

## Pre-stable configuration compatibility

The loader supplies defaults for missing fields, but project/settings schema is still pre-`1.0.0`. Future pre-stable releases may evolve configuration behavior. Review release notes before upgrading important projects.

## Stable release blockers

Before a `v1.0.0` claim, remaining acceptance should include at least:

- measured large/multi-gigabyte stress/resource testing appropriate to scale claims;
- representative real-world PDF/DOCX fidelity corpus;
- complete LibreOffice multi-document semantics before LibreOffice native mode is claimed;
- controlled Microsoft Word normal and forced-timeout acceptance before Word native mode is claimed;
- exact-version Word/Windows evidence plus human rendering/behavior review;
- human accessibility matrix;
- full interactive packaged-app acceptance on representative clean Windows/macOS/Linux targets;
- additional filesystem/network/power-loss testing where those environments are claimed;
- Windows code signing where distributed;
- macOS signing/notarization where distributed;
- explicit Linux distribution compatibility/signing approach;
- final documentation/support/security review.

Controlled abrupt-process recovery, native packaged publication smoke, cross-process local output locking, Linux real `ENOSPC` acceptance, external-office single-document round-trip infrastructure, and the Word-native multi-document **acceptance prototype** are implemented. None of those facts alone converts an external-office mode into a production-ready merge engine.

See [DOCX Fidelity Adapters and Acceptance](docx-fidelity-acceptance.md), [Microsoft Word Native Merge Acceptance](word-native-merge-acceptance.md), and [Release Process](release-process.md).
