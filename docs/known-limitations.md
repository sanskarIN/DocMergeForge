# Known Limitations

DocMergeForge is currently a pre-stable project. The core merge, validation, project, transactional publication, recovery, reporting, desktop, CLI, CI, and packaging functionality is implemented, with increasingly strong automated acceptance. Several areas still remain intentionally excluded from a stable `v1.0.0` claim until their own evidence exists.

This page is deliberately conservative. It should be updated when limitations are actually removed and verified.

## DOCX fidelity is not universally perfect

Portable OOXML composition is the current production-supported DOCX mode. It can preserve normal document structure effectively, but it cannot guarantee perfect behavior for every Microsoft Word construct/application-specific rendering detail.

Features requiring special review can include macros/legacy macro-enabled content, OLE/embedded objects, tracked changes, content controls, custom XML, complex fields, equations, external relationships, unusual style inheritance, complex numbering restarts, section/header/footer interactions, and application-specific layout behavior.

Always keep originals and perform human review in the intended office editor.

## LibreOffice fidelity adapter is not production-ready

The project can expose/detect LibreOffice-related fidelity settings/capability, but the external-suite automation path is not accepted as a production-ready high-fidelity adapter yet. Installing LibreOffice does not automatically upgrade portable mode.

## Microsoft Word fidelity adapter is not production-ready

Likewise, Windows Microsoft Word automation is not currently accepted as production-ready. Word installation alone does not make the mode complete.

A production adapter would need robust COM automation, cleanup, timeout/cancellation, dialog/macro/security handling, real-document testing, and packaged-app acceptance.

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
- human accessibility matrix;
- full interactive packaged-app acceptance on representative clean Windows/macOS/Linux targets;
- additional filesystem/network/power-loss testing where those environments are claimed;
- Windows code signing where distributed;
- macOS signing/notarization where distributed;
- explicit Linux distribution compatibility/signing approach;
- final documentation/support/security review.

Controlled abrupt-process recovery, native packaged publication smoke, cross-process local output locking, and Linux real `ENOSPC` acceptance now have automated evidence and are no longer listed as wholly untested gates.

See [Release Process](release-process.md).
