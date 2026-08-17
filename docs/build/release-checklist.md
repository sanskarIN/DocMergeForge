# Executable Release Build Checklist

Use this checklist for every DocMergeForge executable release candidate. Keep the completed record with the release evidence.

## A. Source identity

- [ ] Intended repository is `sanskarIN/DocMergeForge`.
- [ ] Exact release commit/tag recorded.
- [ ] Working tree state recorded for local builds.
- [ ] Version/release label matches source revision.
- [ ] No unintended local patch is included.

```text
Commit:
Tag:
Branch:
Dirty working tree: yes/no
Builder/workflow:
Date:
```

## B. Automated source gates

At the intended release commit:

- [ ] Quality workflow green.
- [ ] `pre-commit validate-config` green.
- [ ] Ruff green.
- [ ] Black green.
- [ ] strict mypy green.
- [ ] repository-local Markdown link integrity green.
- [ ] full pytest green.
- [ ] 120-Part Regression green.
- [ ] Build Smoke green on Windows/macOS/Linux.
- [ ] automated accessibility metadata/preference smoke green.
- [ ] packaging preflight green.
- [ ] Security/CodeQL green.
- [ ] Recovery Acceptance green when transaction/recovery behavior changed.
- [ ] Disk Full Acceptance/other filesystem gates green where required by the release claim.

Record all workflow run IDs; do not reuse an older run after materially changing the relevant code.

## C. Build environment and provenance

For each target/build mode:

- [ ] native/matching build host used.
- [ ] OS/release recorded.
- [ ] architecture recorded.
- [ ] Python version recorded.
- [ ] PyInstaller version recorded.
- [ ] installed distribution snapshot recorded.
- [ ] build mode is explicitly `onedir` or `onefile`.
- [ ] packaging preflight passes.
- [ ] privacy-safe `.provenance.json` generated.
- [ ] provenance source commit equals intended release commit.
- [ ] provenance artifact label/build mode match artifact.
- [ ] provenance explicitly reports current signed/notarized state truthfully.
- [ ] provenance contains no arbitrary environment/secrets/manuscript information.
- [ ] provenance archive filename/size/SHA-256 match exact unsigned archive.
- [ ] CycloneDX 1.6 `.cdx.json` build-environment SBOM generated and retained.
- [ ] SBOM scope is described accurately; it is not called a byte-perfect final-binary inventory.
- [ ] signed GitHub/Sigstore build-provenance attestation created for the archive.
- [ ] signed `https://cyclonedx.org/bom` SBOM predicate created for the archive.

See [Build Provenance](provenance.md).

## D. Windows onedir build

- [ ] clean onedir build completes.
- [ ] packaged mixed PDF+DOCX smoke passes on build host.
- [ ] archive created.
- [ ] `.sha256` sidecar created.
- [ ] archive-bound JSON provenance created.
- [ ] CycloneDX SBOM generated.
- [ ] build-provenance attestation created.
- [ ] CycloneDX SBOM attestation created.
- [ ] artifact upload includes archive/checksum/provenance/SBOM.
- [ ] separate fresh Windows runner downloads artifact without repository checkout/project installation.
- [ ] fresh runner verifies default GitHub build provenance.
- [ ] fresh runner explicitly verifies predicate type `https://cyclonedx.org/bom`.
- [ ] fresh runner verifies provenance source/mode/label/archive filename/size/SHA-256.
- [ ] fresh runner verifies `.sha256` sidecar.
- [ ] fresh runner extracts archive.
- [ ] fresh runner packaged mixed PDF+DOCX smoke passes.
- [ ] human application launch from Explorer passes.
- [ ] representative clean Windows machine/VM interactive test passes.
- [ ] encrypted-PDF legitimate-password flow passes.
- [ ] cancellation/recovery UX passes.
- [ ] spaces/Unicode/long-path scenarios pass as claimed.
- [ ] Authenticode verified if a signed claim is made.
- [ ] installer tested if an installer is distributed.

## E. macOS onedir build

- [ ] clean onedir/native `.app` build completes.
- [ ] packaged mixed PDF+DOCX smoke passes on build host.
- [ ] archive/checksum/provenance/SBOM generated.
- [ ] both signed GitHub attestation predicates created.
- [ ] separate fresh macOS runner downloads artifact without repository checkout/project installation.
- [ ] fresh runner verifies build-provenance and CycloneDX predicates.
- [ ] fresh runner verifies JSON provenance and archive checksum/size.
- [ ] fresh runner extracts the archive and executes packaged smoke.
- [ ] normal Finder/Terminal launch passes on representative clean Mac.
- [ ] architecture claim matches actual build.
- [ ] encrypted-PDF/cancellation/recovery interactive flows pass.
- [ ] Developer ID signature verified before signed claim.
- [ ] `spctl` assessment recorded where applicable.
- [ ] notarization succeeds before notarized claim.
- [ ] stapling/validation succeeds where applicable.
- [ ] final post-signing/notarization SHA-256 recorded.

## F. Linux onedir build

- [ ] clean onedir build completes.
- [ ] packaged mixed PDF+DOCX smoke passes on build host.
- [ ] archive/checksum/provenance/SBOM generated.
- [ ] both signed GitHub attestation predicates created.
- [ ] separate fresh Linux runner downloads artifact without repository checkout/project installation.
- [ ] fresh runner verifies build-provenance and CycloneDX predicates.
- [ ] fresh runner verifies JSON provenance and archive checksum/size.
- [ ] fresh runner extracts archive and executes packaged smoke with only documented system runtime prerequisites.
- [ ] representative clean target-distro interactive launch passes.
- [ ] minimum claimed distro/glibc baseline tested.
- [ ] X11/Wayland claims tested where applicable.
- [ ] encrypted-PDF/cancellation/recovery interactive flows pass.
- [ ] final SHA-256 recorded.
- [ ] no unsupported distro/package claims are made.

## G. Onefile mode

If onefile is distributed, it is a separate acceptance target:

- [ ] Onefile Acceptance workflow executed for intended revision.
- [ ] Windows/macOS/Linux onefile build-host smoke passes.
- [ ] onefile archives/checksums/provenance/SBOM generated for all targets.
- [ ] both GitHub attestation predicates created for all onefile archives.
- [ ] fresh Windows onefile build-provenance/SBOM/checksum/provenance/extract/smoke passes.
- [ ] fresh macOS onefile build-provenance/SBOM/checksum/provenance/extract/smoke passes.
- [ ] fresh Linux onefile build-provenance/SBOM/checksum/provenance/extract/smoke passes.
- [ ] human onefile startup latency/temp extraction/endpoint-protection behavior reviewed.
- [ ] onefile low-temp-space behavior reviewed where required.

Do not infer onefile acceptance from onedir evidence.

## H. Downloaded-artifact integrity

For every distributed artifact:

- [ ] downloaded artifact is the CI/uploaded artifact, not the pre-upload `dist` directory.
- [ ] signed default GitHub build provenance verifies against the exact archive.
- [ ] signed CycloneDX predicate verifies with `--predicate-type https://cyclonedx.org/bom`.
- [ ] uploaded `.cdx.json` is retained with evidence and its build-environment scope is understood.
- [ ] `.sha256` sidecar matches exact downloaded archive.
- [ ] provenance embedded archive SHA-256 matches independently recomputed SHA-256.
- [ ] provenance embedded archive size matches downloaded archive byte size.
- [ ] provenance source commit matches workflow/release commit.
- [ ] archive extracts successfully.
- [ ] packaged application runs after extraction.
- [ ] artifact name retains `unsigned` while unsigned.

## I. Human packaged application behavior

- [ ] main UI opens normally.
- [ ] branding/resources load.
- [ ] project creation/source picking/order editor work.
- [ ] validation/preflight works.
- [ ] representative PDF merge works.
- [ ] representative DOCX merge works.
- [ ] representative mixed project works.
- [ ] reports/manifests/checksums work.
- [ ] audit/compare works where included.
- [ ] settings/help/about/recent-project/recovery UI work.
- [ ] application exits/relaunches normally.

Automated `--packaged-smoke` is strong Level-2 evidence but does not replace these human interactive checks.

## J. Data safety/recovery

- [ ] source files remain unchanged.
- [ ] companion code remains unmerged/unextracted by manuscript pipeline.
- [ ] cross-process output lock prevents concurrent publication/recovery race.
- [ ] cancellation does not publish partial project bundle.
- [ ] interrupted-output recovery restores previous publication at tested crash boundaries.
- [ ] recovery fails closed on fingerprint/path conflicts.
- [ ] non-writable output fails safely.
- [ ] insufficient-space/ENOSPC behavior tested to claimed level.
- [ ] no private manuscript is accidentally bundled.

## K. Fidelity acceptance

- [ ] representative real PDF corpus tested and visually reviewed.
- [ ] representative real DOCX corpus tested and reviewed in intended office applications.
- [ ] relevant styles/tables/images/sections/headers/footers/numbering/links/fields are reviewed.
- [ ] current portable DOCX limits remain documented.
- [ ] no unfinished Word/LibreOffice adapter is represented as production-ready.

## L. Accessibility acceptance

- [ ] automated accessibility metadata/preference smoke passes on all target CI operating systems.
- [ ] theme application and text-scale/reduced-motion setting checks pass automatically.
- [ ] keyboard-only workflow reviewed by a human.
- [ ] intended screen-reader acceptance performed.
- [ ] real OS high-contrast/theme acceptance performed.
- [ ] text/display scaling reviewed on representative systems.
- [ ] reduced-motion behavior reviewed where applicable.
- [ ] unresolved accessibility limitations documented.

## M. Stress/environmental acceptance

- [ ] required synthetic stress run completed.
- [ ] measured generated source size recorded.
- [ ] merge elapsed/CPU/RSS/disk telemetry recorded when part of the acceptance claim.
- [ ] multi-gigabyte claim made only if measured run actually reaches that class and succeeds.
- [ ] controlled forced-process recovery acceptance completed when required.
- [ ] real disk-exhaustion acceptance completed where required.
- [ ] platform/filesystem/network/power-loss claims have corresponding evidence rather than inference.

## N. Security/privacy/supply chain

- [ ] no passwords/tokens/private keys bundled.
- [ ] no signing secrets committed.
- [ ] provenance allowlist/privacy tests pass.
- [ ] artifact source/commit/dependencies traceable.
- [ ] security workflow green.
- [ ] third-party/license notices reviewed.
- [ ] archive checksum, JSON provenance, CycloneDX SBOM, and signed attestation evidence retained.
- [ ] SBOM is described as build-environment dependency evidence unless a stronger binary-inventory gate was separately performed.
- [ ] any package/license policy assertions are backed by an actual validation gate.

## O. Signing/notarization

### Windows

- [ ] production signing identity used if signed release.
- [ ] timestamp succeeds.
- [ ] Authenticode verification passes.
- [ ] publisher identity is correct.

### macOS

- [ ] Developer ID signing passes.
- [ ] nested bundle code correctly signed.
- [ ] Gatekeeper assessment passes as intended.
- [ ] notarization succeeds.
- [ ] stapling validated where applicable.

### Linux

- [ ] final SHA-256 published.
- [ ] any claimed package/repository signature actually verified.

## P. Final artifact hashes/evidence

Hashes and attestations must describe the exact final distributed bytes **after** all signing/notarization/repacking.

```text
Windows artifact:
Windows SHA-256:
Windows final provenance/SBOM/attestation evidence:
macOS artifact:
macOS SHA-256:
macOS final provenance/SBOM/attestation evidence:
Linux artifact:
Linux SHA-256:
Linux final provenance/SBOM/attestation evidence:
```

Current CI evidence describes unsigned archives and must not be reused for a changed signed/repacked artifact.

## Q. Distribution container/installer

For each distributed format:

- [ ] download/extract/install from a fresh location.
- [ ] launch after extraction/installation.
- [ ] update behavior tested if supported.
- [ ] uninstall/removal tested if installer exists.
- [ ] user manuscripts/projects are preserved.
- [ ] shortcuts/file associations verified if provided.
- [ ] signature/trust behavior verified for the actual container/installer.

## R. Release notes/documentation

- [ ] `CHANGELOG.md` updated.
- [ ] `what_changed.md` updated without deleting prior history.
- [ ] `docs/release-evidence.md` updated.
- [ ] known limitations accurate.
- [ ] platform/build requirements documented.
- [ ] checksum/provenance/CycloneDX/attestation evidence documented/provided.
- [ ] final hashes provided.
- [ ] unsigned artifacts are called unsigned.
- [ ] signing/notarization claims match actual verification.
- [ ] no stable `v1.0.0` claim until the full required stable gate is satisfied.

## S. Final go/no-go

```text
Release candidate:
Commit/tag:
Onedir Package Desktop run:
Onefile Acceptance run (if distributed):
Windows: GO / NO-GO / NOT TARGETED
macOS: GO / NO-GO / NOT TARGETED
Linux: GO / NO-GO / NOT TARGETED
Fresh-runner artifact verification: YES / NO
Archive checksum verified: YES / NO
JSON provenance verified: YES / NO
Build-provenance attestation verified: YES / NO
CycloneDX SBOM predicate verified: YES / NO
Human clean-machine acceptance: YES / NO
Signing verified: YES / NO / N/A
Notarization verified: YES / NO / N/A
All required final hashes/evidence recorded: YES / NO
Known limitations approved: YES / NO
Final decision: GO / NO-GO
Approver/tester:
Date:
```

A **NO-GO** item must not be hidden by renaming, repackaging, or documenting around the failure. Fix, rebuild, and re-verify.
