# Security Policy

DocMergeForge processes local documents that can be confidential or commercially sensitive. Security reports must therefore minimize disclosure of manuscripts, passwords, credentials, and private diagnostics.

For the broader technical threat model and operational guidance, read [docs/security.md](docs/security.md). Privacy guidance is in [docs/privacy.md](docs/privacy.md).

## Supported versions

Security fixes are applied to the latest maintained release line. Until `1.0.0`, DocMergeForge remains pre-stable and users should review release notes, migration notes, and known limitations before upgrading important publication projects.

The exact maintained-version policy can evolve as stable release lines are created; current security support should always be interpreted together with the latest repository release notes.

## Reporting a vulnerability

Do **not** post a sensitive vulnerability publicly if doing so could expose users, manuscripts, credentials, recovery backups, signing information, or an exploitable issue before it can be assessed.

Private security contacts:

- Support: `supportramsandesh@gmail.com`
- Business: `sanskarin@outlook.in`

A useful private report includes:

- DocMergeForge version/tag or commit SHA;
- operating system and relevant architecture;
- whether the issue occurs in CLI, desktop, packaging, recovery, or document processing;
- minimal reproducible steps;
- security impact and affected trust boundary;
- privacy-safe error/diagnostic information;
- a minimal synthetic proof-of-concept where possible.

## Do not send secrets unnecessarily

Never include in a security report unless there is an exceptional, explicitly agreed need:

- encrypted-PDF passwords;
- API keys/tokens;
- authorization headers;
- signing private keys/certificates;
- complete confidential manuscripts;
- private companion source repositories;
- private recovery backups;
- unredacted client/user paths if not required.

A synthetic document reproducing the vulnerability is strongly preferred to a real private manuscript.

## Diagnostics

DocMergeForge's diagnostics layer includes redaction and structured export behavior, but no automated redactor can guarantee removal of every sensitive value.

Before sending diagnostics:

1. open the export/log yourself;
2. confirm passwords/tokens are absent;
3. redact client/project/user paths if needed;
4. remove manuscript excerpts or other unnecessary private data;
5. send only the portion needed to reproduce/understand the issue.

See [docs/diagnostics.md](docs/diagnostics.md).

## Recovery vulnerabilities

If a security issue involves `.docmergeforge-staging-*` or `transaction.json`, preserve the affected evidence locally before experimenting.

Do not publish transaction folders from confidential projects. They may contain rollback copies of previously published manuscripts/reports.

Provide sanitized journal metadata/fingerprints/error messages first.

## Coordinated disclosure

Please allow reasonable time to reproduce, assess, fix, test, and prepare an advisory/release before public disclosure when the issue has meaningful security impact.

A fix may require:

- focused regression tests;
- Quality/Regression/Build Smoke/Security CI;
- packaging acceptance;
- release notes/advisory;
- dependency or platform coordination.

## Out-of-scope assumptions

DocMergeForge cannot secure an already-compromised operating system, malicious administrator/root account, unsafe cloud-sync policy, or third-party viewer/editor outside its control.

However, issues where DocMergeForge itself mishandles untrusted paths, document packages, secrets, output recovery, archives, diagnostics, or packaged distribution are relevant security concerns and should be reported.

## Production package authenticity

Current CI Package Desktop artifacts are explicitly unsigned development builds. A report that an unsigned development archive lacks a production signature is not a vulnerability by itself; presenting such an artifact as signed/authenticated would be a release-process problem.

Actual signature/notarization bypasses or failures in a future production signing pipeline should be treated as security-sensitive.

## Public non-sensitive bugs

For ordinary bugs with no sensitive/security impact, use the repository issue templates and follow [docs/support.md](docs/support.md). Do not attach confidential manuscripts to a public issue.
