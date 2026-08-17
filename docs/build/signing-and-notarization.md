# Signing and Notarization Guide

This guide documents the production trust boundary for DocMergeForge executable distribution.

The repository currently builds **unsigned** PyInstaller artifacts. The steps below describe what must be added and verified before claiming signed production distribution.

## Core rule

Never claim an artifact is signed, trusted, notarized, or production-ready merely because it was built successfully.

A trust claim requires:

- an actual signing identity;
- a signing operation on the final intended payload/container;
- successful signature verification;
- secure handling of private credentials;
- platform-specific acceptance.

## Credential safety

Never commit any of the following to Git:

- private signing keys;
- PFX/P12 files containing private keys;
- certificate passwords;
- Apple notarization passwords/tokens;
- cloud signing service secrets;
- hardware-token PINs;
- temporary decoded credential files.

Use secure OS keychains, hardware-backed identities, GitHub Environments/Secrets, or managed signing services.

## Sign after build, verify after signing

A recommended high-level sequence is:

1. build unsigned artifact;
2. perform functional acceptance on the exact unsigned build inputs;
3. sign the executable/bundle/container as required;
4. verify signatures;
5. notarize macOS distribution where required;
6. verify again;
7. create/generate final release hashes **after** all byte-changing signing/notarization/container steps;
8. publish only the verified final artifact.

## Windows Authenticode

Windows production distribution commonly uses Authenticode signing.

### Typical SignTool command shape

```text
signtool sign /fd SHA256 /td SHA256 /tr <RFC3161-timestamp-url> <certificate-selection-options> <file>
```

The certificate selection options vary by environment. Examples can involve the Windows certificate store, a hardware token, or a managed signing provider.

### Timestamping

Use an RFC 3161 timestamp service supported by the signing identity/provider so the signature can remain verifiable after certificate expiration where platform policy permits.

Do not hardcode credential-bearing timestamp or signing service secrets in source control.

### Verification

```text
signtool verify /pa /v <file>
```

PowerShell can also inspect Authenticode state:

```powershell
Get-AuthenticodeSignature <file> | Format-List
```

Record:

- signature status;
- signer subject/publisher;
- timestamp status;
- file hash after signing.

### Sign executable and installer separately

If a future Windows installer is introduced, verify both:

- the packaged executable(s);
- the installer container itself where applicable.

Do not assume a signed installer means every embedded binary is appropriately signed.

## macOS Developer ID signing

Production distribution outside the Mac App Store typically uses a Developer ID Application identity.

### Inspect available identities

A developer machine can inspect code-signing identities through standard macOS security tooling. Do not expose private-key material in logs.

### Bundle signing strategy

PyInstaller applications can contain nested frameworks/libraries/helper executables. Signing should follow the actual generated bundle structure.

A safe principle is:

- inspect the bundle;
- sign nested code where required;
- sign the outer application last;
- verify the full bundle afterward.

A final outer-bundle command commonly has this shape:

```text
codesign --force --options runtime --timestamp --sign "Developer ID Application: <identity>" <app-bundle>
```

Entitlements should be kept minimal and justified by actual application requirements.

### Verification

```bash
codesign --verify --deep --strict --verbose=2 <app-bundle>
codesign -dv --verbose=4 <app-bundle>
spctl --assess --type execute --verbose=4 <app-bundle>
```

Do not equate ad-hoc signing with Developer ID production signing.

## macOS notarization

A signed macOS application intended for common external distribution should undergo the notarization process applicable to the selected distribution format.

High-level sequence:

1. sign the complete application;
2. create an accepted notarization upload container;
3. submit through Apple's notarization tooling;
4. wait for a successful result;
5. inspect failure logs if rejected;
6. staple the notarization ticket where supported/applicable;
7. verify Gatekeeper assessment on the final distributed form.

Current command shape:

```text
xcrun notarytool submit <archive> --keychain-profile <profile> --wait
```

Stapling:

```text
xcrun stapler staple <app-or-package>
```

Validation:

```text
xcrun stapler validate <app-or-package>
```

Do not place notarization credentials in shell history or repository scripts in plaintext.

## Linux artifact trust

Linux does not have one universal equivalent of Authenticode/Apple notarization.

Depending on the distribution format, trust can involve:

- published SHA-256 checksums;
- detached cryptographic signatures;
- signed package repository metadata;
- signed DEB/RPM packages/repositories;
- reproducible-build evidence.

The current DocMergeForge Linux artifact is an unsigned `.tar.gz`. It should be distributed with a cryptographic hash at minimum when used as a release artifact.

Do not claim package signing until a specific Linux package/signing format has been implemented and verified.

## Hashes and signing order

Signing and notarization can change file bytes. Therefore:

- hashes for unsigned artifacts describe unsigned artifacts;
- hashes for final releases must be generated after final signing/notarization/container creation;
- never reuse a pre-signing hash as the final release hash.

## CI signing architecture

If signing is added to GitHub Actions, use a protected release path.

Recommended controls:

- signing jobs only on protected tags/environments;
- manual approval for production environment if appropriate;
- secrets unavailable to untrusted fork PRs;
- ephemeral credential material;
- cleanup of temporary key files;
- no secret values in logs;
- separate build/sign/publish jobs;
- artifact digest verification between jobs;
- signature verification before publishing.

## Supply-chain integrity between build and sign

When build and sign happen in separate jobs/services:

1. calculate a digest of the unsigned artifact;
2. transfer via trusted artifact storage;
3. verify the digest before signing;
4. sign;
5. calculate the final digest;
6. verify the signature;
7. publish final digest and provenance/evidence.

This reduces the risk of signing an artifact different from the one that passed build acceptance.

## Certificate/key rotation

A production process should document:

- certificate expiration dates;
- renewal/rotation procedure;
- revoked/compromised key response;
- who can access signing credentials;
- how old releases are validated after rotation.

## Failure handling

If signing verification fails:

- do not publish the artifact as signed;
- retain logs that do not expose secrets;
- identify whether signing, timestamping, bundle mutation, or certificate trust failed;
- rebuild/resign from a known clean state where necessary;
- re-run full final verification.

If macOS notarization is rejected:

- inspect notarization results/logs;
- fix the cause;
- rebuild/resign if bundle bytes change;
- resubmit;
- do not ship while describing it as notarized.

## Production trust checklist

### Windows

- [ ] valid production signing identity provisioned;
- [ ] executable signed;
- [ ] installer signed if one exists;
- [ ] RFC 3161 timestamp succeeds;
- [ ] `signtool verify /pa /v` passes;
- [ ] PowerShell signature inspection shows expected publisher;
- [ ] final SHA-256 generated after signing;
- [ ] clean Windows launch acceptance passes.

### macOS

- [ ] Developer ID Application identity provisioned;
- [ ] nested code/bundle signing strategy reviewed;
- [ ] hardened runtime/entitlements reviewed;
- [ ] `codesign --verify` passes;
- [ ] `spctl` assessment passes as intended;
- [ ] notarization succeeds;
- [ ] stapling/validation succeeds where applicable;
- [ ] final distributed artifact hash generated after final processing;
- [ ] clean Mac Gatekeeper launch passes.

### Linux

- [ ] final archive/package hash published;
- [ ] distribution compatibility verified;
- [ ] any package/repository signature actually verified before claim;
- [ ] clean target distro launch passes.

## Current project status

As of the current repository implementation, CI packaging artifacts remain deliberately named `unsigned`. This guide does not change that status; it defines the requirements for a future production trust pipeline.
