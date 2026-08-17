# Known Limitations

DocMergeForge is currently a pre-stable project. The core merge, validation, project, transactional publication, recovery, reporting, desktop, CLI, CI, and packaging-foundation functionality is implemented, but several areas remain intentionally excluded from a stable `v1.0.0` claim until real acceptance evidence exists.

This page is deliberately conservative. It should be updated when limitations are actually removed and verified.

## DOCX fidelity is not universally perfect

Portable OOXML composition is the current production-supported DOCX mode. It can preserve normal document structure effectively, but it cannot guarantee perfect behavior for every Microsoft Word construct/application-specific rendering detail.

Features requiring special review can include:

- macros/legacy macro-enabled content;
- OLE/embedded objects;
- tracked changes;
- content controls;
- custom XML;
- complex fields;
- equations;
- external relationships;
- unusual style inheritance;
- complex numbering restarts;
- section/header/footer interactions;
- application-specific layout behavior.

Always keep originals and perform human review in the intended office editor.

## LibreOffice fidelity adapter is not production-ready

The project can expose/detect LibreOffice-related fidelity settings/capability, but the external-suite automation path is not accepted as a production-ready high-fidelity adapter yet.

Do not assume installing LibreOffice upgrades portable mode automatically.

## Microsoft Word fidelity adapter is not production-ready

Likewise, Windows Microsoft Word automation is not currently accepted as production-ready. Word installation alone does not make the mode complete.

A production adapter would need robust COM automation, cleanup, timeout/cancellation, dialog/macro/security handling, real-document testing, and packaged-app acceptance.

## PDF human rendering acceptance is still required

PDF output is structurally validated/reopened and page evidence is checked, but automated validation cannot guarantee every visual detail in every PDF viewer.

Human QA should review:

- generated front matter/TOC;
- bookmarks;
- overlays/page numbering;
- mixed page sizes/orientations;
- transparency/images/fonts;
- encrypted-source behavior;
- first/last/part-boundary pages.

## Synthetic 120-part regression is not multi-gigabyte proof

The repository continuously tests a generated 120-part workflow. This proves useful ordering/validation/merge/regression behavior at that fixture scale.

It does not justify claims such as:

- “tested with any file size”;
- “multi-gigabyte production accepted”;
- “memory usage guaranteed for all books.”

The manual Stress Acceptance workflow exists to collect explicit measured evidence at larger configured scales.

## Real forced-process-termination acceptance remains separate

The transaction layer has simulated interruption/recovery tests and durable journals. Stable release acceptance should also include real process termination/power-loss-style testing on disposable fixtures across target filesystems/platforms.

Automated simulation cannot reproduce every OS/filesystem crash semantic.

## Storage estimate is conservative, not a hard upper bound

Current storage preflight estimates:

- projected output from source size;
- 125% temporary overhead;
- 128 MiB safety margin.

Actual temporary/output needs can vary with document structure, compression, overwrite backups, filesystem behavior, and future features.

Do not run high-value publication jobs with a nearly full disk merely because the estimate passes by a few bytes.

## Network/removable filesystems require caution

The transaction model relies on filesystem operations such as replacement/rename. Behavior/performance can differ on:

- network shares;
- cloud-synced folders;
- removable drives;
- FUSE/virtual filesystems;
- unusual NAS/SMB configurations.

Prefer a reliable local filesystem for publication staging, then copy verified final artifacts to distribution storage.

## Accessibility is not fully human-accepted yet

Automated accessibility smoke passes key metadata/keyboard checks cross-platform, but complete accessibility acceptance requires real assistive-technology testing.

Open acceptance areas include:

- Narrator/NVDA;
- VoiceOver;
- supported Linux screen reader;
- keyboard-only full workflows;
- high contrast;
- display/text scaling;
- reduced motion;
- long paths/large lists/error states.

Do not equate “accessible names exist” with full accessibility certification.

## CI packaging artifacts are unsigned

The Package Desktop workflow currently archives artifacts with names explicitly containing `unsigned`.

No current documentation should claim:

- Windows production code signing complete;
- macOS notarization complete;
- Linux package signing complete;
- installer certification complete.

These require external credentials/platform acceptance not present in ordinary source CI.

## No finished native installer format is claimed

The current packaging helper produces PyInstaller onedir/one-file development builds. The CI packaging workflow uploads ZIP/TAR archives.

A finished MSI/MSIX/DMG/PKG/AppImage/deb/rpm/etc. distribution pipeline is not currently claimed.

## Cross-platform packaged-app launch acceptance is separate

Build Smoke validates source/CLI/accessibility/packaging configuration on Windows/macOS/Linux. It does not prove that every generated release artifact launches and completes a representative merge on a clean end-user machine.

That is a release acceptance gate.

## `audit` is targeted, not a comprehensive publishing QA system

Current audit patterns focus on selected publication issues such as stale Part 121 references and contact/branding consistency signals.

It does not replace:

- grammar/spelling review;
- plagiarism/copyright review;
- legal review;
- full link checking;
- PDF accessibility tagging checks;
- metadata standards validation;
- comprehensive publication QA.

## `compare` is evidence, not semantic equivalence

PDF comparison mainly uses page-count/page-range evidence. DOCX comparison uses structural counts such as paragraphs, tables, inline shapes, sections, and headings.

Intentional generated front matter/headings/TOC/sections can change counts. Human interpretation is required.

## Encrypted-PDF automation is interactive

Current CLI password collection is interactive. There is no documented non-interactive secret-provider CLI interface for unattended encrypted-PDF automation.

Do not place passwords in shell scripts/project JSON as a workaround.

## Plain `validate` does not unlock encrypted PDFs

The validation command does not prompt for PDF passwords. Full merge/project paths handle password collection where required.

## Legacy `.doc` is not merged/auto-converted

Legacy `.doc` files generate a warning and require explicit external conversion to a separate `.docx` copy.

This is intentional to avoid silently modifying source formats.

## Companion archives are not validated as code

DocMergeForge indexes/hashes companion code archives but does not:

- extract them;
- build them;
- run tests;
- malware-scan them;
- resolve dependencies;
- check code licenses;
- generate an SBOM.

Software-release QA remains separate.

## Relative/absolute project paths are not magically portable

Project JSON stores paths as strings. Moving a project between Windows/macOS/Linux can require path changes or a consistent relative directory layout.

Always run dry-run after moving/importing a project.

## No bit-for-bit reproducible binary build claim

Centralized PyInstaller arguments improve consistency, but exact binary bytes can vary with OS image, Python/dependency/PyInstaller versions and signing timestamps.

Record release commit/workflow/artifact hashes for provenance.

## Pre-stable configuration compatibility

The loader supplies defaults for missing fields, but project/settings schema is still pre-`1.0.0`. Future pre-stable releases may evolve configuration behavior.

Review release notes before upgrading important projects.

## Stable release blockers

Before a `v1.0.0` claim, remaining acceptance should include at least:

- large real stress/resource testing appropriate to scale claims;
- real abrupt-termination recovery testing;
- representative real-world PDF/DOCX fidelity corpus;
- human accessibility matrix;
- packaged-app launch/merge acceptance on clean Windows/macOS/Linux targets;
- Windows code signing where distributed;
- macOS signing/notarization where distributed;
- explicit Linux distribution compatibility/signing approach;
- final documentation/support/security review.

See [Release Process](release-process.md).
