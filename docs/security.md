# Security Model

DocMergeForge is a local-first document-processing application. Its security model focuses on keeping manuscript data local, avoiding unsafe code/archive handling, preserving source integrity, failing closed around output recovery, redacting sensitive diagnostics, and distinguishing development packages from signed production distribution.

This document explains the operational model. Vulnerability reporting instructions remain in [`SECURITY.md`](../SECURITY.md).

## Trust boundaries

DocMergeForge processes local files supplied by the user. Important trust boundaries include:

- source PDF/DOCX files;
- encrypted-PDF passwords;
- companion/source archives;
- project JSON files;
- output directories/filesystems;
- browser-to-host traffic when the responsive web interface is used;
- web access tokens and reverse-proxy configuration for non-loopback browser access;
- external office applications if future high-fidelity adapters are used;
- packaged binaries and CI artifacts;
- diagnostics shared with other people.

Do not assume a file is safe simply because it has a `.pdf`, `.docx`, or archive extension.

## Local-first processing

Core merge, validation, audit, comparison, hashing, reporting, and recovery operations run locally.

The application does not require an account and does not upload manuscript content to a project-operated cloud service as part of the normal merge workflow.

Browser mode is still hosted by a DocMergeForge Python process, but it creates a network boundary between the browser device and that host. On loopback they are the same computer. On a LAN bind the uploaded manuscript bytes travel across that network to the chosen host.

Users remain responsible for external sync folders, cloud-backed drives, endpoint backup software, operating-system telemetry, network infrastructure, reverse proxies, or third-party tools they choose to use around DocMergeForge.

## Responsive web security

The built-in browser server defaults to `127.0.0.1`. Binding to a non-loopback address is rejected unless an access token is configured. This prevents accidentally starting an unauthenticated LAN merge service.

For LAN use:

- prefer `--token auto` or another high-entropy token;
- enter the token in the browser's **Access token (LAN only)** field, or use a one-time `#token=...` URL fragment;
- do not place access tokens in `?token=...` query parameters because query strings can be recorded by HTTP servers, proxies, browser history, and surrounding infrastructure;
- the browser stores the token only in tab-scoped session storage and sends it in `X-DocMergeForge-Token` for merge requests;
- a URL fragment is not sent in the HTTP request and is removed from the visible address after the page consumes it;
- the access token provides request authentication but does not encrypt manuscript traffic;
- plain HTTP should be limited to a trusted machine/network; use HTTPS plus an appropriately hardened reverse proxy/authentication layer when traffic crosses an untrusted network;
- do not expose the built-in Uvicorn development-style deployment directly to the public Internet.

The browser shell sends a restrictive content-security policy plus anti-framing, no-referrer, content-type sniffing, and browser permissions headers. Unexpected engine exceptions are logged on the host but returned to the browser as a generic error so internal host paths/details are not reflected to a remote client.

Web uploads are written to a per-request temporary workspace. Upload handles are closed on success and validation/size failure paths; the workspace is removed on handled errors and after a successful download response completes.

These controls reduce risk; they do not turn an untrusted network into a confidential channel and they do not replace operating-system, reverse-proxy, firewall, or host-security controls.

## Encrypted-PDF passwords

Encrypted-PDF passwords are requested interactively for supported merge/project workflows.

Current handling principles:

- password input is hidden in the terminal GUI/CLI path;
- passwords are held in an in-memory mapping during the operation;
- password mappings are cleared after command execution;
- passwords are not written to project JSON;
- normal documentation/diagnostics should never include them.

The responsive browser interface accepts an optional shared PDF password in a password field for the active merge request. Browser-mode secrets cross the browser-to-host connection with that request, so use HTTPS when the connection is not confined to a trusted local environment.

Do not paste passwords into issue reports or screenshots.

## Source integrity

Discovery computes SHA-256 for source files. Full project publication records a hash snapshot and verifies that tracked PDF, DOCX, and companion inputs remain unchanged before final publication promotion.

This protects against a long-running merge publishing a bundle assembled from source files that changed mid-run.

A changed hash is treated as a failure condition rather than silently accepting the new bytes.

## Companion archive safety

Recognized companion archives are indexed, not extracted or executed by the manuscript merge pipeline.

This design avoids introducing archive extraction risks such as:

- path traversal;
- overwrite of unexpected paths;
- archive bombs;
- accidental code execution;
- source-tree mutation.

DocMergeForge does not certify companion archives as malware-free. Use appropriate security scanning for software distribution.

## Project-file safety

Project files are JSON configuration. They can reveal local paths and publication metadata.

A project file should never be treated as executable code, but malformed/untrusted project JSON can still cause unsafe operational choices if blindly accepted. Review source/output paths before running an imported project.

Recovery path handling independently validates transaction paths so a recovery journal cannot escape the intended output/staging area.

## Transaction journal safety

Interrupted promotion journals contain filesystem recovery metadata and file fingerprints.

Recovery fails closed when:

- journal structure is invalid;
- paths are unsafe;
- required backup/staging evidence is missing;
- current final files do not match expected transaction fingerprints.

This prevents automated cleanup from deleting a file that may have been manually changed after a crash.

## Output permissions

Project preflight probes output-directory writeability by creating/removing a temporary probe file. This catches a class of permission errors before expensive document processing.

Use the least-privileged account that can read sources and write the intended output folder. Running the application as Administrator/root is normally unnecessary and increases the consequences of a path/configuration mistake.

## Diagnostics and redaction

Diagnostics are designed to be privacy-aware and should avoid manuscript body text. Sensitive tokens/password-like values are redacted in the diagnostic logging layer.

Even redacted diagnostics can contain:

- local file paths;
- filenames/project names;
- operating-system information;
- stack traces;
- dependency/version information.

Unexpected browser merge failures are intentionally summarized generically to the remote client while the host logger receives the exception for local diagnosis. Review host logs and exported diagnostics before sharing them publicly.

## PDF/DOCX parser risk

Document files are complex and parser libraries can have vulnerabilities. Keep Python and DocMergeForge dependencies updated and review dependency/security CI results before production releases.

For untrusted documents, consider processing them inside an appropriately isolated environment according to your organization's security policy.

## Macros and active content

Portable DOCX composition does not imply that active content such as macros/OLE objects has been validated or made safe.

DocMergeForge's current production path focuses on `.docx`, not executing embedded active content. Advanced Word constructs can still carry fidelity/security considerations and require separate inspection.

## External office suites

LibreOffice and Microsoft Word high-fidelity modes are not currently accepted as production-ready adapters.

When future automation launches external office software, that will create an additional trust boundary involving:

- external application version/security posture;
- macro policy;
- temporary files;
- COM/UNO automation permissions;
- document trust prompts;
- desktop-session security.

Do not enable undocumented automation workarounds in production.

## CI security checks

The repository includes a Security workflow using GitHub CodeQL. Dependency review is configured for pull-request contexts and can be skipped on ordinary push runs where the action has no PR dependency diff.

A green CodeQL run is useful evidence, not proof of absence of vulnerabilities.

## Package authenticity

The packaging workflow currently produces explicitly **unsigned** development artifacts.

Unsigned ZIP/TAR artifacts must not be presented as cryptographically authenticated production installers.

A production release needs separate platform acceptance such as:

- Windows code signing/installer verification;
- macOS signing and notarization;
- appropriate Linux package signing/distribution policy;
- published checksums;
- release provenance/records.

See [Release Process](release-process.md).

## Security checklist for operators

Before processing confidential/high-value manuscripts:

- use a trusted DocMergeForge source/binary;
- verify the repository/release provenance;
- keep dependencies current;
- use a non-admin account where possible;
- store source/output files in approved locations;
- ensure backups exist;
- avoid public/shared temp directories;
- keep the web server on loopback unless network access is deliberately required;
- require a strong token for LAN web access and never place it in a query parameter;
- use HTTPS when browser-to-host traffic leaves a trusted local environment;
- do not share encrypted-PDF passwords;
- inspect unexpected companion archives independently;
- review host logs/diagnostics before exporting them;
- recover interrupted transactions using the journal-aware command;
- verify final checksums after copying artifacts.

## Security checklist for contributors

- never add secrets to fixtures/tests;
- use synthetic/public-domain test documents;
- do not log manuscript body text unnecessarily;
- do not persist passwords or web access tokens to project files;
- keep tokens out of request URLs/query parameters;
- validate any new path manipulation against traversal;
- prefer atomic writes and fail-closed recovery;
- avoid auto-extracting untrusted archives;
- add regression tests for security-relevant fixes;
- keep CodeQL/quality workflows green;
- document new trust boundaries.

## Reporting vulnerabilities

Do not open a public issue containing a private manuscript, password, token, or sensitive diagnostics.

Use the contacts in [`SECURITY.md`](../SECURITY.md):

- `supportramsandesh@gmail.com`
- `sanskarin@outlook.in`

Include a minimal privacy-safe reproduction, operating system, DocMergeForge version/commit, and relevant diagnostics without confidential manuscript content.
