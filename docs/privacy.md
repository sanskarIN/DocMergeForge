# Privacy

DocMergeForge is designed as a local-first document-processing application. Core discovery, hashing, validation, PDF/DOCX merging, audit, comparison, reporting, project storage, DOCX fidelity acceptance, and interrupted-output recovery operate on files available to the local machine.

## Core privacy commitments

Current application design follows these principles:

- no DocMergeForge account is required;
- manuscript processing does not require uploading files to a DocMergeForge service;
- encrypted-PDF passwords are not persisted by the application;
- project files store configuration/paths, not password secrets;
- companion archives are indexed locally without extraction/upload;
- private DOCX fidelity corpus execution is local and does not upload corpus files/evidence;
- fidelity corpus JSON rewrites manuscript locations to corpus-relative paths instead of serializing absolute source paths;
- diagnostics should avoid manuscript body text;
- sensitive token/password-like values are redacted in the diagnostics layer;
- temporary/staged files are cleaned after normal success/failure where safe;
- recovery evidence is preserved when deleting it could destroy rollback data.

## What “local-first” does and does not mean

Local-first means DocMergeForge itself performs its core work locally.

It does **not** control other software/services on your computer. Your files can still leave the device if you place them in or process them from:

- OneDrive/Google Drive/Dropbox/iCloud synced folders;
- network/NAS shares;
- enterprise backup systems;
- endpoint monitoring/DLP systems;
- cloud virtual desktops;
- third-party PDF/office applications with their own telemetry/cloud features.

The LibreOffice/Microsoft Word fidelity acceptance paths intentionally invoke those locally installed applications. Their own telemetry, account, macro, add-in, cloud, policy, or enterprise-management behavior is outside DocMergeForge's control.

Choose source/output locations and external office-suite configuration according to your privacy policy.

## Source file metadata

Discovery records local metadata/evidence such as:

- file paths/names;
- document kind;
- detected part number/title derived from filename;
- byte size;
- SHA-256;
- PDF page count when available;
- encrypted-PDF flag;
- scanner warnings.

This metadata may appear in manifests/reports/checksums/project evidence. A filename/path can itself reveal confidential project/client information.

## Project files

Project JSON can contain:

- project name;
- source-folder paths;
- output-folder path;
- selected-file paths;
- expected part range;
- PDF/DOCX settings;
- state/checkpoint/warnings.

It should not contain encrypted-PDF passwords.

Before sharing a project file publicly, inspect absolute paths and project names for private information.

## Encrypted-PDF passwords

CLI/desktop merge paths request encrypted-PDF passwords when needed.

Current handling:

1. password is entered locally;
2. the target PDF verifies it locally;
3. the value is held in an in-memory mapping for the active operation;
4. the mapping is cleared when the command/project operation exits;
5. the password is not written to the saved project or normal output evidence.

Do not include passwords in:

- filenames;
- project names;
- shell command arguments;
- support tickets;
- screenshots;
- exported diagnostics.

## Hashes

SHA-256 hashes are generated for source/output/companion/fidelity identity evidence.

A hash is derived from file bytes and is not normally reversible into the full manuscript. However, hashes can still be sensitive identifiers for known files and can reveal that two parties possess identical content.

Share release/fidelity hashes intentionally.

## Private DOCX fidelity corpus

`docmergeforge fidelity-corpus` exists so representative real-world DOCX files can be acceptance-tested locally without putting those source documents into a public repository or CI fixture set.

The corpus report stores paths such as:

```text
sections/landscape.docx
roundtrip/sections/landscape.docx
```

instead of the absolute source/output paths held internally while the command is running. Nested single-document evidence is rewritten to the same relative paths before JSON serialization.

This reduces path-metadata disclosure but does not make the evidence directory public-safe automatically:

- source/output SHA-256 values remain in the report;
- error text can originate from the local OS or external office application and should be reviewed;
- round-tripped DOCX files contain the manuscript content;
- filenames/subdirectory names can still be sensitive;
- LibreOffice/Word may have their own local recent-file/history/telemetry behavior.

The output directory must be outside the source corpus, and the command does not upload its corpus/report/artifacts.

Keep private corpus sources and generated evidence outside public source control unless they are intentionally sanitized. See [Private DOCX Fidelity Corpus Testing](docx-fidelity-corpus.md).

## Reports and manifests

Generated reports/manifests/checksums/companion indexes can contain local paths/filenames and publication metadata.

Before publishing them on GitHub or another public release, review whether they expose:

- user home-directory names;
- client/project names;
- private folder structure;
- unpublished filenames;
- internal warning text;
- private companion paths.

For public releases, consider sanitizing workflow/layout so generated paths are already publication-safe.

## Audit output

The audit command can output findings containing:

- document path;
- detected GitHub URLs;
- detected email variants in message text;
- finding details.

Audit locally and review JSON before sharing.

## Diagnostic logging

Diagnostics are intended to capture technical failure/environment information without logging manuscript bodies.

Even privacy-aware diagnostics can contain:

- local filesystem paths;
- project/file names;
- stack traces;
- operating system/dependency versions;
- error messages originating from third-party libraries.

Always review diagnostic exports before sending them to support or attaching them to a public issue.

## Temporary files

Document engines use temporary/atomic output paths. Full project publication also uses a hidden staging directory under the chosen output folder. External DOCX fidelity adapters use separate temporary directories beside the requested acceptance output before promoting a validated copy.

Ordinary temporary/staged data is cleaned after normal completion/failure where safe.

### Recovery exception

If publication is interrupted during final promotion or rollback fails, the hidden transaction folder may contain the only backup of a previously published file.

DocMergeForge intentionally preserves that recovery evidence instead of deleting it automatically.

Treat `.docmergeforge-staging-*` as potentially containing confidential manuscript/report files. Secure it like the output folder and recover using:

```bash
docmergeforge recover-output --output-dir "<output-folder>"
```

## Output write probe

Preflight creates a small temporary `.docmergeforge-write-probe-*` file in the output directory solely to verify writeability, then removes it.

No manuscript content is written into that probe.

## Companion code

Companion archives are hashed/indexed without extraction by the normal manuscript workflow. This means their internal source content is not copied into DocMergeForge reports/manuscripts.

The companion index still exposes archive filenames/paths/hashes/sizes.

## Desktop recent projects/settings

Desktop convenience features can persist settings/recent-project metadata so the application can reopen workflows. Those records can reveal local project paths/names.

On shared computers, use an OS account/profile appropriate for the privacy level of the publications being processed.

## Crash/recovery state

Project recovery checkpoints and output transaction journals are local operational metadata. They should not contain PDF passwords but can contain project/output paths and filenames.

Do not upload raw transaction folders from confidential projects to public issue trackers.

## Telemetry

Future DocMergeForge telemetry, if ever introduced, should be:

- explicit;
- opt-in;
- disabled by default;
- documented with exactly what fields leave the device;
- designed never to send manuscript content/passwords.

No documentation should imply DocMergeForge telemetry exists until it is actually implemented. This statement does not make a claim about telemetry in third-party office applications that the fidelity acceptance adapters may invoke.

## Backups

Privacy and durability can conflict if backups are not planned.

For confidential publications:

- use encrypted/approved backup storage;
- keep originals separate from working output;
- understand cloud-sync behavior;
- preserve final release evidence according to retention policy;
- securely delete obsolete working copies only after confirming backups/recovery requirements.

## Public issue/report checklist

Before sharing any support material:

- [ ] Passwords/tokens removed.
- [ ] Client/author names reviewed.
- [ ] Local usernames/home paths redacted if necessary.
- [ ] Manuscript body text removed unless intentionally public.
- [ ] Private companion code not attached.
- [ ] Transaction backup files not attached.
- [ ] Project JSON paths reviewed.
- [ ] Diagnostic stack traces reviewed.
- [ ] Audit findings reviewed for email/URL exposure.
- [ ] Fidelity corpus report filenames/hashes/errors reviewed.
- [ ] Fidelity round-trip DOCX artifacts excluded unless intentionally shareable.

## Related documents

- [Security Model](security.md)
- [Private DOCX Fidelity Corpus Testing](docx-fidelity-corpus.md)
- [DOCX Fidelity Adapters and Acceptance](docx-fidelity-acceptance.md)
- [Support](support.md)
- [Publication Recovery](recovery.md)
- [`SECURITY.md`](../SECURITY.md)
