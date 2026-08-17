# Glossary

## Artifact

A file produced or tracked as part of a DocMergeForge workflow, such as a merged PDF/DOCX, report, manifest, checksum file, companion index, checklist, or packaged desktop archive.

## Audit

A local text-oriented review that reports selected publication findings such as stale “Next: Part 121” references or inconsistent contact/branding patterns. Audit does not rewrite manuscripts.

## Batch transaction

The full-project publication boundary that stages multiple manuscripts/evidence files and promotes them as one coherent bundle rather than publishing each output independently.

## Bookmark

A PDF navigation outline entry. DocMergeForge can add per-part bookmarks when configured.

## Build Smoke

Cross-platform GitHub Actions workflow that verifies source compilation, CLI availability, desktop accessibility metadata, and packaging preflight on Ubuntu, Windows, and macOS.

## Cancellation

A graceful request to stop a merge. Cancellation checks are performed through merge/finalization stages so a normal cancellation can exit before final publication promotion.

## Checkpoint

Project workflow metadata indicating the last successful recoverable stage. A project checkpoint is different from the filesystem transaction journal used for final output promotion.

## Checksum

A cryptographic digest used to verify byte identity. DocMergeForge uses SHA-256 for source/output evidence.

## Companion

Source-code/project/archive material associated with a publication but intentionally excluded from PDF/DOCX manuscript merging.

## Companion Code Index

Markdown/JSON evidence listing companion artifact references, including part number where detectable, path, size, and SHA-256.

## Compare

A post-publication evidence tool. PDF compare checks source/output page counts and part ranges; DOCX compare reports aggregate structural counts for sources versus output.

## Conflict analysis

DOCX preflight analysis that detects likely package/style/numbering complexity requiring review before publication.

## Direct merge

CLI `pdf` or `docx` command that merges a single document kind using default engine settings without the full project publication evidence bundle.

## Discovery

Scanning source roots, classifying files, detecting part numbers, calculating hashes, inspecting PDFs, and collecting warnings.

## DOCX

Microsoft Word Open XML document (`.docx`), internally a ZIP package containing XML parts, relationships, media, styles, numbering, and other resources.

## Dry run

Read-only project/preset preflight that validates readiness/order/storage/expected outputs without creating final books.

## Evidence

Data retained to support verification/reproducibility, such as source order, hashes, validation results, manifests, reports, checksums, and comparison results.

## Fail closed

Safety behavior where an uncertain/conflicting condition stops the operation instead of guessing or continuing destructively. Output recovery uses fail-closed rules.

## Fidelity

How accurately a merged document preserves the visual/structural behavior of its sources in target reader/editor applications.

## Final path

The user-facing output filename/location after a staged output is successfully promoted.

## High-fidelity adapter

A planned/optional external office-suite integration intended to use LibreOffice or Microsoft Word for difficult DOCX fidelity. Current adapters are not accepted as production-ready.

## InputDocument

Internal model representing a discovered file with path, kind, part identity, size, SHA-256, optional PDF page count/encryption state, and warnings.

## Journal

`transaction.json` stored in a publication staging directory. It records promotion phase and per-output recovery metadata.

## Manifest

Machine-readable JSON publication record containing application/profile/source/output/warning evidence.

## Merge profile

Named group/label of merge behavior. The default model profile name is `Exact Preservation`.

## Natural sort

Numeric-aware ordering where Part 2 sorts before Part 10.

## Numbered-part validation

Comparison of detected part numbers against the inclusive expected start/end range, including missing and duplicate detection.

## OOXML

Office Open XML, the package/XML format used by `.docx`. DOCX fidelity/validation involves ZIP members, XML, relationships, styles, numbering, media, and sections.

## Onedir

Default PyInstaller packaging mode that creates an application directory containing the executable and bundled runtime/resources.

## One-file

Optional PyInstaller mode that creates a single distributable executable/bundle entry, with platform/runtime extraction behavior that must be tested separately.

## OutputArtifact

Internal validated staged-output record containing final path, SHA-256, size, document kind, and validation status.

## OutputTransaction

The utility responsible for staging outputs, writing the promotion journal, backing up overwritten finals, promoting the complete batch, rolling back failures, and preserving evidence if rollback is incomplete.

## Part identity

Detected numeric part plus display label/title derived from a source filename.

## PDF

Portable Document Format manuscript. The PDF engine appends ordered source pages, applies configured publication enhancements, and validates the result by reopening it.

## Portable DOCX mode

Current production-supported library-based OOXML composition path. It provides strong normal-document support but does not claim perfect preservation of every advanced Word construct.

## Preflight

Read-only evidence stage combining discovery, numbered validation, storage/writeability checks, expected-output calculation, order listing, companion/ignored counts, and DOCX conflict count.

## Promotion

The final transaction phase where staged outputs are moved/replaced into their public final paths.

## Publishing checklist

Generated Markdown checklist intended to support final human publication acceptance after automated merging.

## Recovery

Process of resolving an interrupted publication transaction using the journal and rollback backups/fingerprints.

## Regression fixture

Synthetic generated documents used to prove a known larger workflow continues to work, such as the 120-part SQL fixture.

## Report

Human-readable Markdown/HTML merge evidence generated as part of a project publication.

## Rollback backup

Temporary copy/location of a previous final file moved into the transaction staging folder when overwrite promotion needs the ability to restore it.

## Safe required bytes

Storage preflight estimate: projected output + temporary estimate + safety margin, compared against filesystem free space.

## Selected files

Project list preserving an explicitly reviewed file selection/order rather than relying only on a new automatic discovery order.

## SHA-256

Cryptographic hash function used by DocMergeForge for file-integrity evidence.

## Source integrity

Guarantee attempt that tracked source/companion bytes do not change during publication. Hash snapshots are verified before final promotion.

## Staged output

A manuscript/report file created inside the transaction staging directory before it is visible at the requested final publication path.

## Staging directory

Hidden output-folder child beginning `.docmergeforge-staging-` used by a publication transaction.

## Stress Acceptance

Manual GitHub Actions workflow for scalable synthetic fixtures, validation, preflight, merge, comparison, size evidence, and artifact upload.

## Transaction fingerprint

Recorded staged file size and SHA-256 used during interrupted recovery to ensure a current final file really belongs to the failed transaction before deletion/restoration.

## Validation

Structural/readiness checks that determine whether sources/outputs satisfy required conditions. Validation is distinct from audit and human fidelity review.

## Versioned path

Alternative output name selected when overwrite is disabled and the requested path already exists, preventing unintended replacement.

## Writeability probe

Temporary file creation/removal in the output folder used during preflight to confirm transaction staging can be created there.
