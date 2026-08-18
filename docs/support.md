# Support

This guide explains how to get help with DocMergeForge while protecting private manuscripts, passwords, and local-system information.

## Project links

- Repository: https://github.com/sanskarIN/DocMergeForge
- GitHub profile: https://www.github.com/sanskarIN
- LinkedIn: https://www.linkedin.com/in/sanskarIN
- Buy Me a Coffee: https://buymeacoffee.com/sanskarIN
- YouTube: https://youtube.com/@Sanskar-in
- X: https://x.com/x_sanskarIN

> **Made by the Sanskar**

## Contact

Business:

- `sanskarin@outlook.in`
- `sanskarin.business@gmail.com`

Support:

- `supportramsandesh@gmail.com`

Security reports should follow [`SECURITY.md`](../SECURITY.md) and should not be posted publicly when sensitive.

## Before requesting help

Check:

1. [Installation](installation.md)
2. [Getting Started](getting-started.md)
3. [Troubleshooting](troubleshooting.md)
4. [FAQ](faq.md)
5. [Known Limitations](known-limitations.md)
6. current [`CHANGELOG.md`](../CHANGELOG.md)

Then reproduce the problem with the smallest safe example possible.

## Information to include in a bug report

Useful non-sensitive details:

- DocMergeForge version or Git commit SHA;
- operating system/version;
- Python version if running from source;
- whether CLI or desktop app was used;
- exact command (with private paths replaced if needed);
- expected behavior;
- actual behavior;
- exit code;
- relevant error text/stack trace;
- whether source validation/preflight passed;
- whether the failure happened during discovery, validation, PDF, DOCX, reporting, or publication promotion;
- whether a `.docmergeforge-staging-*` transaction folder remains;
- whether the output filesystem is local/network/removable;
- smallest synthetic reproduction.

## Never post publicly

Do not post:

- encrypted-PDF passwords;
- API keys/access tokens;
- private source manuscripts;
- confidential output manuscripts;
- private companion code;
- credentials/signing certificates;
- unreviewed diagnostics containing sensitive paths/names;
- transaction backups from confidential publications.

## Redact paths safely

Instead of:

```text
C:\Users\RealName\Clients\SecretBook\Part 1.docx
```

Use:

```text
C:\Users\USER\Books\PROJECT\Part 1.docx
```

Keep enough structure to reproduce the issue (spaces, Unicode, depth) without revealing confidential names.

## Reproduce with synthetic files

For document-processing bugs, the best public issue usually includes a tiny synthetic fixture that reproduces the structure rather than the original private document.

For the 120-part path, the repository can generate a safe fixture:

```bash
python scripts/generate_120_fixture.py fixtures/generated/sql-120
```

If the bug only happens with one advanced DOCX feature, create a small document containing only that feature.

## Diagnostics

DocMergeForge includes privacy-aware diagnostics/logging. Before sharing a diagnostics export:

- open/review it;
- remove client/project names if needed;
- confirm no manuscript body text is present;
- confirm no passwords/tokens are present;
- retain relevant technical errors/version info.

Diagnostics are support evidence, not a substitute for a minimal reproduction.

## Recovery-related support

If the problem involves an interrupted output transaction:

1. do not delete `.docmergeforge-staging-*`;
2. back up the affected output folder;
3. run recovery only if safe:

```bash
docmergeforge recover-output --output-dir "<output-folder>"
```

4. if recovery fails closed, preserve the complete transaction folder before asking for help;
5. do **not** publicly upload confidential backup files from that folder.

For support, provide sanitized journal structure/error/fingerprints rather than private output contents when possible.

## Encrypted-PDF problems

If a password is rejected:

- verify the password in a trusted PDF reader;
- confirm the same file/version is being processed;
- report that verification succeeded/failed;
- never send the password itself.

## Packaging problems

Include:

- target OS/architecture;
- local vs GitHub Actions build;
- `python scripts/build_desktop.py --check` output;
- PyInstaller version;
- whether build failed or packaged app failed at launch;
- relevant terminal output;
- whether `assets/branding` appears in the package;
- whether the package is onedir/one-file.

Remember that current workflow artifacts are unsigned development packages.

## Accessibility problems

Include:

- OS;
- assistive technology and version;
- exact dialog/control;
- keyboard-only steps;
- what was/was not announced;
- theme/text/display scaling;
- result of:

```bash
python scripts/check_accessibility.py
```

Do not include screenshots containing confidential manuscript names unless redacted.

## Fidelity problems

For DOCX fidelity bugs, identify the smallest relevant construct:

- style;
- numbering;
- section break;
- header/footer;
- field/TOC;
- table;
- image/relationship;
- equation;
- content control;
- tracked change;
- OLE/custom XML.

State which application/version was used to create/view the source and output (for example Word/LibreOffice). A minimal synthetic DOCX is much more useful than a description like “formatting changed.”

For PDF problems, include source/output page counts and the page number where behavior differs.

## Security vulnerabilities

For suspected security issues, do not use a public issue if disclosure would expose users or sensitive details. Follow [`SECURITY.md`](../SECURITY.md).

## Feature requests

A useful feature request explains:

- user problem/workflow;
- why current behavior is insufficient;
- expected input/output;
- cross-platform implications;
- safety/privacy implications;
- whether it affects PDF, DOCX, companion code, UI, CLI, packaging, or recovery;
- whether it changes existing project-file behavior.

## Support scope

The project can document/support its own code and workflows. It cannot guarantee support for every third-party viewer/editor/OS configuration or repair arbitrary corrupted source manuscripts.

Advanced Microsoft Word/LibreOffice fidelity issues may require reproducing the document in the target office suite because portable OOXML libraries do not implement every application-specific behavior.

## Supporting development

If DocMergeForge is useful, the project highlights:

**Buy Me a Coffee:** https://buymeacoffee.com/sanskarIN

Support contributions do not change technical acceptance requirements: code still needs quality, regression, security, accessibility, and release verification.
