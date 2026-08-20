# Privacy

DocMergeForge is designed as a local-first document-processing application. Core discovery, hashing, validation, PDF/DOCX merging, audit, comparison, reporting, project storage, DOCX fidelity acceptance, and interrupted-output recovery run on the DocMergeForge Python host. Native desktop/CLI use keeps the browser/network layer out of the workflow; responsive web use sends selected files from the browser device to the Python host chosen by the user.

## Core privacy commitments

Current application design follows these principles:

- no DocMergeForge account is required;
- manuscript processing does not require uploading files to a DocMergeForge-operated cloud service;
- responsive browser uploads go to the user-selected DocMergeForge Python host, not to a project-operated cloud backend by default;
- encrypted-PDF passwords are not persisted by the application;
- project files store configuration/paths, not password secrets;
- companion archives are indexed locally without extraction/upload by the full project workflow and are not accepted by the focused browser merge route;
- private DOCX fidelity corpus execution is local and does not upload corpus files/evidence;
- native LibreOffice/Word acceptance commands run locally and do not upload private manuscripts by themselves;
- fidelity corpus JSON rewrites manuscript locations to corpus-relative paths instead of serializing absolute source paths;
- diagnostics should avoid manuscript body text;
- sensitive token/password-like values are redacted in the diagnostics layer;
- browser access tokens are kept out of query parameters by the maintained UI flow and are held in tab-scoped session storage when used through the browser client;
- temporary/staged files are cleaned after normal success/failure where safe;
- browser request workspaces and upload handles are cleaned/closed after completion or handled failure;
- a native-office acceptance destination is removed if final post-promotion validation/integrity fails; and
- recovery evidence is preserved when deleting it could destroy rollback data.

## What “local-first” does and does not mean

Local-first means DocMergeForge itself performs its document-processing work on the Python host selected by the user rather than requiring a DocMergeForge-operated cloud processing service.

For native desktop/CLI use, that host is the same machine running the user interface. For responsive browser use, the browser may be on the same computer or a different LAN/network device, so manuscript bytes travel from that browser device to the Python host.

Local-first does **not** control other software/services on your computer or network. Your files can still leave a device if you place them in or process them from:

- OneDrive/Google Drive/Dropbox/iCloud synced folders;
- network/NAS shares;
- enterprise backup systems;
- endpoint monitoring/DLP systems;
- cloud virtual desktops;
- third-party PDF/office applications with their own telemetry/cloud features;
- network infrastructure, reverse proxies, VPNs, gateways, or inspection systems used between a browser and a DocMergeForge host.

The LibreOffice/Microsoft Word fidelity acceptance paths intentionally invoke those locally installed applications. Their own telemetry, account, macro, add-in, cloud, policy, or enterprise-management behavior is outside DocMergeForge's control.

Choose source/output locations, browser-host topology, network transport, reverse-proxy configuration, and external office-suite configuration according to your privacy policy.

## Browser-to-host privacy boundary

The responsive browser interface adds a network trust boundary that the native desktop/CLI workflow does not need.

### Loopback

The default web bind is `127.0.0.1`. Browser and Python host are on the same computer, and no LAN listener is created by default.

### Trusted LAN

A non-loopback bind is rejected unless an access token is configured. On a LAN request, the selected manuscript bytes, the token header, and any shared encrypted-PDF password travel to the Python host over that network connection.

The maintained browser UI accepts a token in its masked **Access token (LAN only)** field or through a one-time `#token=...` URL fragment. It does not intentionally bootstrap tokens from `?token=...` query parameters. Query strings can be recorded by HTTP access logs/proxies/history, while URL fragments are handled by the browser and are not included in the HTTP request.

The page stores the token in `sessionStorage`, which is scoped to the browser tab/session rather than persistent project files. Closing the tab/session is the intended normal end of that browser token cache. Browser/device extensions, malware, debugging tools, or a compromised browser profile remain outside DocMergeForge's ability to guarantee secrecy.

### Untrusted or Internet transport

An access token authenticates merge requests; it does not encrypt the connection. Plain HTTP does not provide manuscript/password/token confidentiality against a party able to observe the network path.

Do not expose the built-in Uvicorn server directly to the public Internet. Use HTTPS plus an appropriately hardened reverse proxy/authentication/request-limit/host-security boundary whenever traffic leaves a trusted local environment.

DocMergeForge does not claim that browser traffic is private merely because the document engine itself is local-first.

## Source file metadata

Discovery records local metadata/evidence such as file paths/names, document kind, detected part number/title, byte size, SHA-256, PDF page count when available, encrypted-PDF state, and scanner warnings.

This metadata may appear in manifests/reports/checksums/project evidence. A filename/path can itself reveal confidential project/client information.

For browser uploads, the host works with sanitized upload filename components inside a per-request temporary workspace. The browser still transmits the original multipart filename metadata, so do not assume a confidential filename is hidden from the host/network just because its host-side storage name is sanitized.

## Project files

Project JSON can contain project name, source/output paths, selected-file paths, expected part range, PDF/DOCX settings, state/checkpoints, and warnings. It should not contain encrypted-PDF passwords or responsive-web access tokens.

Before sharing a project file publicly, inspect absolute paths and project names for private information.

## Encrypted-PDF passwords

CLI/desktop merge paths request encrypted-PDF passwords when needed.

Current native handling:

1. the password is entered locally;
2. the target PDF verifies it locally;
3. the value is held in memory for the active operation;
4. the mapping is cleared when the command/project operation exits; and
5. the password is not written to saved project or normal output evidence.

The responsive web interface can submit one shared PDF password with the active merge request. That password is not written into project JSON, but it crosses the browser-to-host connection. Use HTTPS when that connection is not confined to a trusted local environment.

Do not include passwords in filenames, project names, shell command arguments, support tickets, screenshots, URL query strings, or exported diagnostics.

## Hashes

SHA-256 hashes are generated for source/output/companion/fidelity identity evidence.

A hash is derived from file bytes and is not normally reversible into the manuscript. However, hashes can still be sensitive identifiers for known files and can reveal that two parties possess identical content.

Share release/fidelity hashes intentionally.

## Private DOCX fidelity corpus

`docmergeforge fidelity-corpus` exists so representative real-world DOCX files can be acceptance-tested locally without putting those source documents into a public repository or CI fixture set.

The report uses corpus-relative paths such as:

```text
sections/landscape.docx
roundtrip/sections/landscape.docx
```

instead of normal absolute source/output paths. Nested single-document evidence is rewritten to the same relative paths before JSON serialization.

This reduces path-metadata disclosure but does not make the evidence directory public-safe automatically. Source/output hashes remain, error text can originate from the OS or office suite, generated DOCX files contain manuscript content, and filenames/subdirectory names can still be sensitive.

The output directory must be outside the source corpus, and the command does not upload its corpus/report/artifacts.

Keep private corpus sources and generated evidence outside public source control unless intentionally sanitized. See [Private DOCX Fidelity Corpus Testing](docx-fidelity-corpus.md).

## Native LibreOffice multi-document acceptance privacy

The explicit supervised Writer/UNO acceptance command can process multiple private DOCX files in exact order. It uses:

- a temporary copied master;
- a temporary isolated LibreOffice profile;
- a unique local UNO pipe name;
- a temporary worker script and source manifest; and
- a separate non-existing output/evidence path selected by the operator.

The JSON evidence does not serialize manuscript paragraph/table text; it stores SHA-256 fingerprints and structural/risk values. The merged output itself contains the manuscript and remains confidential if the inputs are confidential.

The public GitHub workflow uses generated synthetic documents. Do not substitute private manuscripts into public CI artifacts unless disclosure is intentional and authorized.

## Microsoft Word native acceptance privacy

Controlled Word acceptance can record environment/capability/process-state evidence and exact Word process identity values such as PID/process name/start-time fingerprint. These are technical control values, not manuscript body text, but they can still reveal system state and should be reviewed before sharing.

The synthetic controlled workflow should not be run against confidential sources unless its runner and artifact-retention policy are approved for them.

## Reports and manifests

Generated reports/manifests/checksums/companion indexes can contain local paths/filenames and publication metadata.

Before publishing them on GitHub or another public release, review whether they expose user home-directory names, client/project names, private folder structure, unpublished filenames, internal warning text, or private companion paths.

The focused browser route returns the merged document rather than the full project report bundle, but web-host access/error logs can still contain network/request metadata and local exception details. Review those logs before sharing them.

## Audit output

The audit command can output document paths, detected GitHub URLs, detected email variants, and finding details. Audit locally and review JSON before sharing.

## Diagnostic logging

Diagnostics are intended to capture technical failure/environment information without logging manuscript bodies.

Even privacy-aware diagnostics can contain local paths, project/file names, stack traces, operating-system/dependency versions, and errors originating from third-party libraries.

Unexpected browser merge exceptions are intentionally summarized to the remote browser while the host logger receives the exception. That protects remote response details but means the host log can contain technical information that should be treated as sensitive.

Always review diagnostic exports and host logs before sending them to support or attaching them to a public issue.

## Temporary files and final promotion

Document engines use temporary/atomic output paths. Full project publication also uses a hidden staging directory under the chosen output folder. External DOCX fidelity adapters/native prototypes use separate temporary directories beside the requested acceptance output before promoting a validated copy.

Browser uploads/results use a separate per-request temporary workspace on the Python host. Upload handles close through the maintained save cleanup path; the workspace is removed on handled error and after a successful download response completes.

Ordinary temporary data is cleaned after normal completion/failure where safe. External-office final promotion verifies the destination and tracked source hashes immediately after promotion; if that final verification fails, the newly created acceptance destination is removed instead of being left as a misleading successful artifact.

### Recovery exception

If normal project publication is interrupted during final promotion or rollback fails, the hidden transaction folder may contain the only backup of a previously published file.

DocMergeForge intentionally preserves that recovery evidence instead of deleting it automatically.

Treat `.docmergeforge-staging-*` as potentially containing confidential manuscript/report files. Secure it like the output folder and recover using:

```bash
docmergeforge recover-output --output-dir "<output-folder>"
```

The browser request workspace is not a durable project recovery journal; browser mode should be retried from the original client files after a failed request rather than treating its temporary directory as publication recovery evidence.

## Git/source-control safety net

The repository `.gitignore` excludes common local fidelity evidence directories, private corpus directories, generated fixtures, transaction staging folders, and the output lock file.

This reduces accidental commits but is not a security boundary. A contributor can still force-add ignored data. Always review staged files and `git status` before committing.

## Output write probe

Preflight creates a small temporary `.docmergeforge-write-probe-*` file in the output directory solely to verify writeability, then removes it. No manuscript content is written into that probe.

## Companion code

Companion archives are hashed/indexed without extraction by the normal manuscript workflow. Their internal source content is not copied into DocMergeForge reports/manuscripts, but the companion index still exposes archive filenames/paths/hashes/sizes.

The focused web merge route rejects archive uploads rather than adding a second network-facing companion-code workflow.

## Desktop recent projects/settings

Desktop convenience features can persist settings/recent-project metadata so the application can reopen workflows. Those records can reveal local project paths/names.

On shared computers, use an OS account/profile appropriate for the privacy level of the publications being processed.

## Crash/recovery state

Project recovery checkpoints and output transaction journals are local operational metadata. They should not contain PDF passwords but can contain project/output paths and filenames.

Do not upload raw transaction folders from confidential projects to public issue trackers.

## Telemetry

Future DocMergeForge telemetry, if ever introduced, should be explicit, opt-in, disabled by default, documented with exactly what leaves the device, and designed never to send manuscript content/passwords.

No documentation should imply DocMergeForge telemetry exists until it is actually implemented. This does not make a claim about telemetry in third-party office applications invoked by fidelity acceptance, browser/network infrastructure, or reverse proxies chosen by the operator.

## Backups

For confidential publications, use approved/encrypted backup storage, keep originals separate from working output, understand cloud-sync behavior, preserve final release evidence according to retention policy, and securely delete obsolete working copies only after confirming recovery requirements.

## Public issue/report checklist

Before sharing support material:

- [ ] Passwords/tokens removed.
- [ ] Browser-host/reverse-proxy logs reviewed.
- [ ] Client/author names reviewed.
- [ ] Local usernames/home paths redacted if necessary.
- [ ] Manuscript body text removed unless intentionally public.
- [ ] Private companion code not attached.
- [ ] Transaction backup files not attached.
- [ ] Project JSON paths reviewed.
- [ ] Diagnostic stack traces reviewed.
- [ ] Audit findings reviewed for email/URL exposure.
- [ ] Fidelity corpus/native acceptance report filenames/hashes/errors reviewed.
- [ ] External-office generated DOCX artifacts excluded unless intentionally shareable.
- [ ] Word/LibreOffice environment or process-control metadata reviewed before sharing.

## Related documents

- [Security Model](security.md)
- [Platform Support](platform-support.md)
- [Installation](installation.md)
- [Private DOCX Fidelity Corpus Testing](docx-fidelity-corpus.md)
- [DOCX Fidelity Adapters and Acceptance](docx-fidelity-acceptance.md)
- [LibreOffice Native Multi-Document Merge Acceptance](libreoffice-native-merge-acceptance.md)
- [Microsoft Word Native Merge Acceptance](word-native-merge-acceptance.md)
- [Support](support.md)
- [Publication Recovery](recovery.md)
- [`SECURITY.md`](../SECURITY.md)