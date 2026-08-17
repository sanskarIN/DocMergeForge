# Companion Code Policy

DocMergeForge intentionally separates publication manuscripts from companion/source code. This is a core data-integrity rule, not merely a UI preference.

> **PDF manuscripts merge with PDF manuscripts. DOCX manuscripts merge with DOCX manuscripts. Companion code remains independent.**

## Why code is not merged into documents

Source-code projects and manuscript formats have different integrity requirements. Automatically unpacking, rewriting, or embedding code during a document merge could:

- change project structure;
- corrupt line endings or encodings;
- break build systems;
- lose executable permissions or metadata;
- introduce unsafe extraction behavior;
- confuse publication validation;
- create a master manuscript that no longer corresponds to original source archives.

DocMergeForge therefore indexes companion artifacts without treating them as PDF/DOCX merge inputs.

## Recognized companion archive types

Current scanner archive suffixes:

```text
.zip
.7z
.rar
.tar
.gz
.tgz
```

The broader scanner design also recognizes source-oriented directory naming such as names containing `code`, `companion`, or `project` where directory classification is applicable.

## What happens during discovery

A companion archive is classified as `companion`, not `pdf` or `docx`.

Its discovery evidence includes:

- path;
- detected part identity when present in the name;
- size;
- SHA-256 hash.

## What happens during merge

Companion items are excluded from manuscript engine input lists.

They are not:

- concatenated into a PDF;
- inserted into a DOCX;
- extracted;
- compiled;
- reformatted;
- renamed internally;
- rewritten;
- refactored.

Full project runs track their hashes so source-integrity verification can detect if the companion package changes during publication.

## Companion index

A project publication creates:

```text
Companion_Code_Index.md
Companion_Code_Index.json
```

The index records references such as:

- part number when detectable;
- companion path;
- SHA-256;
- byte size.

This allows the manuscript and its companion artifacts to be distributed as a coordinated release without physically merging incompatible content.

## Recommended source layout

Example:

```text
Book/
  Part 001.pdf
  Part 001.docx
  Part 001 Code.zip
  Part 002.pdf
  Part 002.docx
  Part 002 Code.zip
  ...
```

or:

```text
Book/
  manuscripts/
    Part 001.pdf
    Part 001.docx
    ...
  companion-code/
    Part 001 Code.zip
    Part 002 Code.zip
    ...
```

Because source scanning is recursive, organize folders so intended document and companion files remain easy to audit.

## Archive safety

DocMergeForge does not need to extract companion archives in order to index them. This is safer than automatically unpacking untrusted archives and avoids path traversal/archive-bomb risks in the merge path.

If a user chooses to inspect a companion archive independently, use trusted archive tools and normal security practices outside the manuscript merge pipeline.

## Hash verification

SHA-256 evidence helps verify that the companion archive shipped with a release is byte-identical to the one indexed during publication.

A matching hash does not prove the code is safe or correct. It proves identity relative to the recorded bytes.

## Code changes after publication

If companion code changes after a manuscript publication:

1. create a new version of the companion archive;
2. rerun project discovery/preflight;
3. regenerate companion index/checksum evidence;
4. decide whether manuscript outputs also need a new edition;
5. keep old release evidence immutable where possible.

Do not replace an archived companion ZIP in place while retaining old checksums/indexes.

## Companion code and version control

Git repositories are usually better for active source history than ZIP files. A publication can still include a release archive or repository commit/tag reference externally.

DocMergeForge's companion index currently records local file evidence, not Git commit semantics.

For reproducible releases, consider preserving both:

- the companion archive/checksum used for the publication;
- the corresponding Git commit/tag in release notes.

## Unsupported behavior

DocMergeForge does not currently promise to:

- merge code from multiple parts into one source tree;
- resolve conflicting dependencies;
- build/compile companion projects;
- run tests inside companion archives;
- generate SBOMs for arbitrary code archives;
- rewrite repository history;
- verify licenses inside arbitrary archives.

These are separate software-engineering tasks.

## Release checklist for companion code

Before release:

- each intended companion package is present;
- obsolete/duplicate archives are removed from the scanned source tree;
- companion hashes are generated;
- `Companion_Code_Index.md` and `.json` are reviewed;
- archives are independently malware/security scanned where required;
- source repository commit/tag is recorded where relevant;
- manuscript files do not contain accidentally embedded source archives;
- checksums and index ship with the correct release version.
