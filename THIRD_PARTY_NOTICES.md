# Third-Party Notices

DocMergeForge is MIT-licensed, but it uses and can bundle third-party software whose own licenses, notices, source-offer requirements, attribution requirements, and redistribution conditions remain independent of the DocMergeForge license.

This document is a release-maintainer checklist, not a substitute for the license text distributed by any dependency.

## Runtime dependencies

The Python application currently declares these direct runtime dependencies in `pyproject.toml`:

- **PySide6 / Qt** — desktop user interface and Qt runtime bindings.
- **pypdf** — PDF parsing, reading, and writing.
- **python-docx** — DOCX object-model access.
- **docxcompose** — portable multi-document DOCX composition.
- **ReportLab** — generated PDF publication material and overlays.

Every redistributed build must use the license terms that apply to the exact resolved versions included in that build. In particular, Qt/PySide6 distribution must be reviewed against the licensing option and obligations actually used by the distributor; do not infer compliance merely from DocMergeForge being MIT-licensed.

## Development and build dependencies

Development/build extras currently include tools such as:

- pytest and pytest-cov;
- Ruff;
- Black;
- mypy and typing stubs;
- pre-commit;
- PyInstaller; and
- CycloneDX tooling.

These tools may be present only in the build environment rather than the final executable. Their inclusion in a build-environment SBOM does not by itself mean their code is embedded in the shipped binary.

## External office applications

LibreOffice and Microsoft Word are **not bundled runtime dependencies** of DocMergeForge.

The optional fidelity/acceptance tooling can invoke a locally installed office application when the operator explicitly runs those acceptance paths. The office application's own license, installation, account, enterprise-policy, and redistribution terms remain separate. DocMergeForge must not redistribute LibreOffice or Microsoft Office merely because its acceptance code can automate them.

## Release-maintainer requirements

Before publishing any binary/archive/installable release:

1. record the exact resolved dependency versions used by the build;
2. generate and retain the build-environment SBOM/provenance evidence;
3. collect the license/notice files required by the exact bundled dependencies;
4. determine which dependency files are actually redistributed by the packaged artifact;
5. preserve attribution/source-offer/relinking or other obligations where applicable;
6. review platform-specific packaging for Qt/PySide6 license obligations;
7. keep external-office licensing separate from DocMergeForge redistribution;
8. re-run this review after any dependency major-version change; and
9. archive the reviewed notices with the exact release artifact and checksum.

A GitHub/Sigstore attestation, checksum, SBOM, or successful CI run proves neither license compatibility nor fulfillment of third-party redistribution obligations.

## Source of truth

For a release, the source of truth is the license and notice material shipped by the **exact dependency versions actually resolved and bundled**, together with the dependency projects' official licensing information. If this file conflicts with an upstream license, the upstream license controls that component.
