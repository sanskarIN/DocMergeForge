# Private DOCX Fidelity Corpus Testing

Representative real-world DOCX fidelity testing often requires manuscripts that cannot be committed to a public repository. DocMergeForge provides a local corpus runner so those files can be exercised through the explicit LibreOffice or Microsoft Word round-trip adapters while keeping source documents outside source control and CI.

## Command

```bash
docmergeforge fidelity-corpus \
  --input-dir "./private-corpus" \
  --output-dir "./private-fidelity-evidence" \
  --mode libreoffice
```

Windows with Microsoft Word installed:

```powershell
docmergeforge fidelity-corpus `
  --input-dir ".\private-corpus" `
  --output-dir ".\private-fidelity-evidence" `
  --mode word
```

## Options

Required:

- `--input-dir PATH` — private source corpus directory;
- `--output-dir PATH` — separate evidence/output directory outside the source corpus;
- `--mode libreoffice|word` — explicit external office adapter.

Optional:

- `--pattern GLOB` — case-insensitive filename glob; default `*.docx`;
- `--recursive` / `--no-recursive` — recurse into subdirectories; recursive by default;
- `--timeout SECONDS` — positive per-document native-office timeout; default `300`;
- `--fail-fast` — stop after the first adapter/validation failure instead of collecting additional failures.

## Source/output separation

The output directory must not be the corpus directory and must not be nested inside it.

This prevents generated round-trip documents from being rediscovered as source corpus inputs and reinforces the rule that original manuscripts remain separate from acceptance artifacts.

## Discovery

The corpus runner:

1. verifies the input directory exists;
2. applies the requested recursion mode;
3. selects `.docx` files only;
4. applies the filename pattern case-insensitively;
5. sorts selected files deterministically by corpus-relative path.

If no DOCX file matches, the command fails rather than producing an empty “successful” report.

## Per-document execution

Each selected source is passed to the same explicit single-document acceptance path used by `fidelity-roundtrip`.

That path records:

- source/output file SHA-256;
- source/output structural counts;
- source/output visible-text SHA-256 fingerprints;
- source/output risky-construct findings;
- structural-match status;
- content-fingerprint-match status;
- newly introduced risk categories;
- overall measured acceptance.

The visible-text fingerprints cover measured body paragraphs, body table cells, header paragraphs/table cells, and footer paragraphs/table cells. The report stores SHA-256 fingerprints, not the manuscript text itself.

External-office exceptions, invalid output, timeout, missing automation, source-integrity failures, and output-write failures are recorded as failed corpus items. With `--fail-fast`, processing stops after the first such error.

A fail-fast run that stops before every discovered document has been processed is always reported as incomplete and is never accepted.

## Output layout

For a corpus such as:

```text
private-corpus/
├── simple.docx
├── sections/
│   └── landscape.docx
└── fields/
    └── toc-fields.docx
```

The evidence directory uses:

```text
private-fidelity-evidence/
├── roundtrip/
│   ├── simple.docx
│   ├── sections/
│   │   └── landscape.docx
│   └── fields/
│       └── toc-fields.docx
└── fidelity-corpus-<mode>-report.json
```

The source directory structure is preserved below `roundtrip/`.

## Report privacy

The corpus JSON report deliberately stores corpus-relative source/output paths instead of absolute private manuscript paths.

For example:

```json
{
  "source": "sections/landscape.docx",
  "output": "roundtrip/sections/landscape.docx"
}
```

The nested evidence object is also rewritten to use those relative paths before report serialization.

When an adapter/validation error contains the absolute source file, destination file, corpus root, or evidence root, the corpus runner rewrites those locations before serializing the per-item error. Examples use placeholders such as:

```text
<corpus>/sections/landscape.docx
<evidence>/roundtrip/sections/landscape.docx
```

The replacement is intentionally limited to known corpus/evidence paths. Third-party error text can still contain other sensitive data and should be reviewed before sharing.

This reduces accidental disclosure of usernames, workstation directory layouts, client names embedded in parent folders, and other path metadata.

The generated round-trip DOCX files still contain whatever document content the source manuscripts contain. Treat the entire evidence directory as private unless it has been intentionally sanitized.

The report also contains file hashes and visible-text fingerprints. Those hashes do not contain the plain manuscript text, but they can still act as identifiers for known content and should be shared intentionally.

## No automatic upload

`fidelity-corpus` is a local command. It does not upload the corpus, generated copies, hashes, fingerprints, or report to GitHub or another service.

Do not add private corpus/evidence folders to the repository. Store them outside the repository or add appropriate local ignore rules if they must temporarily live near a checkout.

## Corpus design

A production-oriented corpus should intentionally cover the constructs and application versions the project plans to claim.

Useful categories include:

- plain paragraphs and common styles;
- custom themes/styles;
- numbered and bulleted lists, including restarts;
- tables with merged cells and pagination behavior;
- images and drawings;
- multiple sections;
- portrait/landscape transitions;
- different margins/page sizes;
- section-linked and unlinked headers/footers;
- page numbering changes;
- hyperlinks/bookmarks;
- footnotes/endnotes;
- TOC and other fields;
- equations;
- content controls;
- comments and tracked changes;
- charts/SmartArt;
- embedded objects;
- custom XML;
- non-Latin scripts and representative fonts;
- very large documents;
- documents created by multiple supported Word/LibreOffice versions.

Use legally shareable synthetic reductions when a private document reveals a reproducible defect that should become a permanent public regression test.

## Interpreting acceptance

Corpus-level `accepted=true` means:

- at least one matching file was discovered;
- every discovered file was processed;
- every processed item retained the measured structural snapshot;
- every processed item retained the measured visible-text fingerprints; and
- no processed item introduced a new risky-construct category.

It does not mean every page renders identically or that the external adapter is production-ready.

A corpus can pass these structural/content checks while still requiring manual review for:

- line/page wrapping;
- font substitution;
- floating object placement;
- image rendering/positioning;
- chart rendering;
- field recalculation;
- TOC page numbers;
- section header/footer linkage semantics;
- tracked-change display state;
- equation appearance;
- custom XML/content-control behavior;
- application-specific layout differences.

## Manual review record

For a release-candidate corpus, keep a separate review record containing at least:

- DocMergeForge commit SHA;
- operating-system version;
- office-suite version/build and architecture;
- corpus revision/identifier;
- generated corpus report hash;
- count of discovered/processed files;
- Word/LibreOffice repair prompts, if any;
- automated structural/content/risk result;
- manual visual/behavior result per risk category;
- accepted deviations and their rationale;
- blocker defects and regression-test links.

Do not store confidential document content in the review record unless the storage location is approved for it.

## Production gate

A passing private corpus is one required evidence source, not permission to edit `production_ready` by itself.

External adapter production certification still requires complete multi-document merge semantics, platform/application coverage, cleanup/cancellation behavior, packaged-app testing where claimed, and release evidence tied to exact versions.

See [DOCX Fidelity Adapters and Acceptance](docx-fidelity-acceptance.md) and [Known Limitations](known-limitations.md).
