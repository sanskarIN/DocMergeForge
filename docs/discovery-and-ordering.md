# Discovery and Ordering

Correct discovery and ordering are publication-safety requirements in DocMergeForge. The application does not rely on arbitrary filesystem listing order and does not merge all files in a directory indiscriminately.

## Recursive scanning

The scanner accepts one or more roots. By default it scans directories recursively. A root that is itself a file is also accepted by the internal scanner.

For every discovered file, DocMergeForge records evidence including:

- path;
- document kind;
- detected part identity;
- byte size;
- SHA-256 hash;
- PDF page count when readable without a password;
- encrypted-PDF flag;
- discovery warnings.

The SHA-256 captured during discovery contributes to later source-integrity checks.

## File classification

Current classification rules are extension/name based.

### PDF manuscript

Suffix:

```text
.pdf
```

### DOCX manuscript

Suffix:

```text
.docx
```

### Companion/source archive

Archive suffixes currently recognized:

```text
.zip
.7z
.rar
.tar
.gz
.tgz
```

The scanner infrastructure also recognizes directories whose names contain words such as `code`, `companion`, or `project` as companion locations when directory classification is used. Files found inside recursively scanned directories are still classified individually.

### Other

Any file that is not PDF, DOCX, or a recognized companion archive is classified as `other`.

## Legacy `.doc`

Legacy Microsoft Word `.doc` files are **not** merged directly.

When a `.doc` file is discovered, a warning explains that the user must explicitly create a separate `.docx` conversion. DocMergeForge never silently replaces or converts the original `.doc` source.

Recommended process:

1. preserve the original `.doc`;
2. convert it using a trusted office application;
3. save a separate `.docx` copy;
4. inspect that copy;
5. rerun discovery/validation.

## Part-number detection

DocMergeForge recognizes common numbered naming patterns containing `part`, `chapter`, or `volume`, plus abbreviated `p`/`part` forms.

Examples that are designed to be recognized include names conceptually similar to:

```text
Part 1.pdf
part-002.docx
Chapter_15.pdf
Volume.3.docx
P 7.pdf
P12.docx
```

Part numbers can contain up to six digits in the current detector, and leading zeroes are normalized numerically.

Examples:

```text
Part 001 -> part number 1
Part 010 -> part number 10
```

If no supported pattern is found, the file gets no numeric part number. It may still be discovered, but a numbered-part validation workflow cannot treat it as satisfying an expected number.

## Clean titles

The detector derives a cleaned title from the filename stem by replacing underscore/hyphen runs with spaces and normalizing whitespace. The original path remains the authoritative file identity.

## Natural ordering

Natural ordering splits text into numeric and non-numeric tokens so numbers compare numerically.

Correct natural order:

```text
Part 1
Part 2
Part 3
Part 10
Part 11
Part 100
```

Plain lexical ordering could incorrectly produce:

```text
Part 1
Part 10
Part 100
Part 11
Part 2
```

That is why CLI discovery uses natural part-number ordering by default.

## CLI ordering controls

Supported on `validate`, `pdf`, and `docx`:

```bash
--natural-sort
--no-natural-sort
```

`--natural-sort` is the default.

The CLI natural-order key prioritizes files with detected part numbers and then uses numeric part identity plus a natural filename key. Files without detected numbers sort after numbered parts in this direct CLI ordering path.

Use `--no-natural-sort` only when a deliberate filename order is required and verified.

## Filename filtering

The CLI supports an optional case-insensitive glob:

```bash
--pattern "Part *.pdf"
```

Filtering applies to the filename, not the whole path.

Examples:

```bash
docmergeforge validate \
  --input "./Book" \
  --parts 1-120 \
  --pattern "Chapter *.docx"
```

A filter can make a previously complete set appear incomplete. Treat the validation result after filtering as the truth for that command.

## Selected-file ordering in projects

A project may contain `selected_files`. This allows the desktop workflow to persist a reviewed selection/order rather than always recreating it from a fresh folder scan.

Use explicit selection/order when:

- source filenames are inconsistent;
- front/back matter participates in a special workflow;
- an editor intentionally changes chapter order;
- a reproducible manual ordering decision must be retained.

After files are renamed/moved, rerun project preflight because saved paths/order may no longer match the filesystem.

## Duplicate part numbers

Two files of the same manuscript kind claiming the same expected part number are a validation blocker.

Do not resolve duplicates by relying on filename sorting. Determine which source is authoritative, rename/archive the obsolete one outside the scanned input, then validate again.

## Missing part numbers

A gap in the configured inclusive expected range is a blocker for that manuscript kind.

For expected Parts 1–5:

```text
Part 1
Part 2
Part 4
Part 5
```

Part 3 is missing even if four source files exist. File count alone is insufficient evidence.

## PDF inspection during discovery

For an unencrypted PDF, the scanner attempts to read its page count with `pypdf` in non-strict mode.

For an encrypted PDF:

- it is marked encrypted;
- page count is not treated as available until access is unlocked;
- merge/project workflows can later request a password.

If PDF inspection raises an exception, discovery retains the file and attaches a warning rather than fabricating page-count evidence.

## Hashing and source integrity

Every discovered file is SHA-256 hashed. This is intentionally more expensive than trusting filename/size alone because a source can change without its name changing.

During full project publication, source-integrity verification is performed again before final promotion. If a source changes during the run, final publication is refused instead of silently mixing versions.

## Recommended naming convention

For the easiest cross-platform experience, use predictable names:

```text
Series Name - Part 001.pdf
Series Name - Part 001.docx
Series Name - Part 002.pdf
Series Name - Part 002.docx
```

Benefits:

- unambiguous numeric detection;
- stable visual ordering;
- easier manual review;
- less risk when moving between filesystems;
- easier pattern filtering.

## Discovery checklist

Before merging:

- confirm the correct root folders are configured;
- inspect discovered file kinds;
- inspect scanner warnings;
- verify detected part numbers;
- resolve `.doc` legacy files deliberately;
- remove/relocate obsolete duplicates;
- check missing parts;
- confirm natural/manual order;
- keep companion code independent;
- run project dry-run/preflight after any filename or folder change.
