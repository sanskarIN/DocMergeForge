# Executable Release Build Checklist

Use this checklist for every DocMergeForge executable release candidate. Keep the completed record with the release evidence.

## A. Source identity

- [ ] Intended repository is `sanskarIN/DocMergeForge`.
- [ ] Exact release commit/tag recorded.
- [ ] Working tree state recorded.
- [ ] Version/release label matches the source revision.
- [ ] No unintended local patch is included.

Record:

```text
Commit:
Tag:
Branch:
Dirty working tree: yes/no
Builder:
Date:
```

## B. Automated source gates

At the same intended release commit:

- [ ] Quality workflow green.
- [ ] Ruff green.
- [ ] Black green.
- [ ] strict mypy green.
- [ ] full pytest green.
- [ ] 120-Part Regression green.
- [ ] Build Smoke green on Windows.
- [ ] Build Smoke green on macOS.
- [ ] Build Smoke green on Linux.
- [ ] accessibility smoke green on configured matrix.
- [ ] packaging preflight green on configured matrix.
- [ ] Security/CodeQL green.

Record workflow run IDs.

## C. Build environment

For each target:

- [ ] native/matching build host used.
- [ ] OS/version recorded.
- [ ] architecture recorded.
- [ ] Python 3.12 used unless intentionally changed.
- [ ] PyInstaller version recorded.
- [ ] dependency freeze captured.
- [ ] build environment isolated.
- [ ] packaging preflight passes.

## D. Windows build

- [ ] clean onedir build completes.
- [ ] actual `dist` layout inspected.
- [ ] packaged application launches from Explorer.
- [ ] packaged application launches outside repository.
- [ ] clean Windows machine/VM test passes.
- [ ] PDF packaged-app merge passes.
- [ ] DOCX packaged-app merge passes.
- [ ] mixed-format project passes where included in release scope.
- [ ] encrypted-PDF legitimate-password flow passes.
- [ ] cancellation passes.
- [ ] recovery acceptance passes at required level.
- [ ] spaces/Unicode path test passes.
- [ ] onefile separately tested if distributed.
- [ ] archive extracted and re-tested.
- [ ] final SHA-256 recorded.
- [ ] Authenticode verified if signed claim is made.
- [ ] installer tested if installer is distributed.

## E. macOS build

- [ ] clean onedir build completes.
- [ ] actual `dist`/bundle layout inspected.
- [ ] application launches from Terminal/Finder as applicable.
- [ ] application launches outside repository.
- [ ] clean Mac test passes.
- [ ] PDF packaged-app merge passes.
- [ ] DOCX packaged-app merge passes.
- [ ] encrypted-PDF flow passes.
- [ ] cancellation/recovery passes.
- [ ] architecture claim matches actual build.
- [ ] onefile separately tested if distributed.
- [ ] Developer ID signature verified before signed claim.
- [ ] `spctl` assessment recorded.
- [ ] notarization succeeds before notarized claim.
- [ ] stapling/validation succeeds where applicable.
- [ ] final distribution archive/container tested.
- [ ] final SHA-256 recorded after all byte-changing steps.

## F. Linux build

- [ ] clean onedir build completes.
- [ ] actual `dist` layout inspected.
- [ ] graphical launch passes.
- [ ] application launches outside repository.
- [ ] clean target distro test passes.
- [ ] PDF packaged-app merge passes.
- [ ] DOCX packaged-app merge passes.
- [ ] encrypted-PDF flow passes.
- [ ] cancellation/recovery passes.
- [ ] minimum claimed distro/glibc baseline tested.
- [ ] X11/Wayland claims tested where applicable.
- [ ] archive preserves executable behavior.
- [ ] onefile separately tested if distributed.
- [ ] final SHA-256 recorded.
- [ ] no unsupported distro/package claims are made.

## G. Package Desktop workflow

- [ ] workflow run executed for intended commit/tag when CI artifacts are used.
- [ ] Windows job passes.
- [ ] macOS job passes.
- [ ] Linux job passes.
- [ ] downloaded archives correspond to head SHA.
- [ ] archive names retain `unsigned` when unsigned.
- [ ] CI artifacts tested after download/extraction.
- [ ] workflow run ID recorded.

## H. Packaged application behavior

- [ ] main UI opens.
- [ ] branding/resources load.
- [ ] project creation works.
- [ ] source picking works.
- [ ] ordering works.
- [ ] validation/preflight works.
- [ ] PDF merge works.
- [ ] DOCX merge works.
- [ ] reports/manifests/checksums work.
- [ ] audit/compare entry points work where included.
- [ ] settings/help/about work.
- [ ] recent-project/recovery UI works where included.
- [ ] application exits normally.

## I. Data safety

- [ ] source files remain unchanged in acceptance tests.
- [ ] companion code remains unmerged/unextracted by manuscript pipeline.
- [ ] cancellation does not publish partial project bundle.
- [ ] interrupted-output recovery fails closed on conflicts.
- [ ] non-writable output fails safely.
- [ ] insufficient-space behavior is tested to the claimed acceptance level.
- [ ] no private manuscript is accidentally bundled in executable archive.

## J. Fidelity acceptance

- [ ] representative real PDF manuscript tested.
- [ ] representative real DOCX manuscript tested.
- [ ] styles/tables/images/sections/headers/footers/numbering relevant to claimed use are reviewed.
- [ ] current portable DOCX limitations remain documented.
- [ ] no unfinished Word/LibreOffice adapter is represented as production-ready.

## K. Accessibility acceptance

- [ ] automated accessibility smoke passes.
- [ ] keyboard-only workflow reviewed.
- [ ] screen-reader acceptance performed where required.
- [ ] high-contrast/theme acceptance performed.
- [ ] text scaling reviewed.
- [ ] reduced-motion behavior reviewed where applicable.
- [ ] unresolved accessibility limitations documented.

## L. Stress/recovery acceptance

- [ ] required synthetic stress run completed.
- [ ] measured fixture/source size recorded.
- [ ] real multi-gigabyte claim made only if actually executed successfully.
- [ ] real forced-process interruption acceptance completed if required for release gate.
- [ ] real disk-exhaustion acceptance completed if required for release gate.
- [ ] filesystem-specific recovery claims tested on claimed filesystems.

## M. Security/privacy

- [ ] no passwords/tokens/private keys bundled.
- [ ] no signing secrets committed.
- [ ] support diagnostics used in release testing exclude manuscript body/passwords as designed.
- [ ] artifact source/commit traceable.
- [ ] security workflow green.
- [ ] third-party/license notices reviewed for distribution.

## N. Signing/notarization

### Windows

- [ ] production signing identity used if signed release.
- [ ] timestamp succeeds.
- [ ] signature verification passes.
- [ ] publisher identity is correct.

### macOS

- [ ] Developer ID signing passes.
- [ ] nested bundle code is correctly signed.
- [ ] Gatekeeper assessment passes as intended.
- [ ] notarization succeeds.
- [ ] stapling validated where applicable.

### Linux

- [ ] SHA-256 published.
- [ ] any claimed package/repository signature is actually verified.

## O. Final artifact hashes

Hashes must describe the exact final distributed files.

Record:

```text
Windows artifact:
Windows SHA-256:
macOS artifact:
macOS SHA-256:
Linux artifact:
Linux SHA-256:
```

## P. Distribution container/installer

For each distributed format:

- [ ] download/extract/install from a fresh location.
- [ ] launch after extraction/installation.
- [ ] update behavior tested if supported.
- [ ] uninstall/removal tested if installer exists.
- [ ] user manuscripts/projects are not removed unexpectedly.
- [ ] shortcuts/file associations verified if provided.

## Q. Release notes and documentation

- [ ] `CHANGELOG.md` updated.
- [ ] `what_changed.md` updated.
- [ ] known limitations accurately listed.
- [ ] platform/build requirements documented.
- [ ] hashes provided.
- [ ] unsigned artifacts are called unsigned.
- [ ] signing/notarization claims match verification evidence.
- [ ] no `v1.0.0` or stable claim is made unless full stable gate is satisfied.

## R. Final go/no-go

```text
Release candidate:
Commit/tag:
Windows: GO / NO-GO / NOT TARGETED
macOS: GO / NO-GO / NOT TARGETED
Linux: GO / NO-GO / NOT TARGETED
Signing verified: YES / NO / N/A
Notarization verified: YES / NO / N/A
All required hashes recorded: YES / NO
Known limitations approved: YES / NO
Final decision: GO / NO-GO
Approver/tester:
Date:
```

A **NO-GO** item must not be hidden by renaming or repackaging the artifact. Fix, rebuild, and re-verify.
