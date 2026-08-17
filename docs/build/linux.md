# Linux Executable Build Guide

This guide covers native Linux PyInstaller builds, runtime compatibility, graphics/Qt requirements, archive creation, and production-distribution acceptance.

## Scope

The repository currently builds an unsigned PyInstaller application on `ubuntu-latest` and archives the onedir output as a `.tar.gz`. It does not currently automate AppImage, DEB, RPM, Flatpak, or Snap production packages.

## 1. Prepare the checkout

```bash
git clone https://github.com/sanskarIN/DocMergeForge.git
cd DocMergeForge
git status
git rev-parse HEAD
```

For release work, checkout the intended commit/tag.

## 2. Install Python/build prerequisites

Use Python 3.12 for packaging parity with CI.

On Ubuntu/Debian, PySide6 may require EGL runtime support. The repository's Linux CI installs:

```bash
sudo apt-get update
sudo apt-get install -y libegl1
```

Other distributions may use different package names. Install equivalent platform packages rather than assuming Ubuntu package names apply everywhere.

## 3. Create the Python environment

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[build]"
```

For full developer checks:

```bash
pip install -e ".[dev]"
```

## 4. Record platform baseline

For release evidence:

```bash
uname -a
uname -m
python --version
ldd --version | head -n 1
```

The glibc/runtime version of the build host matters. A binary built on a very new Linux distribution may not run on an older one.

## 5. Packaging preflight

```bash
python scripts/build_desktop.py --check
```

## 6. Build onedir

```bash
python scripts/build_desktop.py
```

Inspect:

```bash
find dist/DocMergeForge -maxdepth 3 -print
```

The current CI workflow archives this directory.

## 7. Optional one-file build

```bash
python scripts/build_desktop.py --one-file
```

Test separately. One-file extraction can depend on temporary directories, mount options, and executable permissions.

## 8. Launch in a real graphical session

From the packaged output, launch the executable under the intended desktop environment.

Verify:

- Qt platform plugin loads;
- window renders correctly;
- file/folder dialogs work;
- PDF merge works;
- DOCX merge works;
- reports are created;
- encrypted-PDF legitimate-password flow works;
- cancellation/recovery works;
- application exits normally.

## 9. X11 and Wayland

If Linux support is intended for both X11 and Wayland environments, test both explicitly. Do not claim both simply because Qt theoretically supports them.

Record:

```bash
echo "$XDG_SESSION_TYPE"
```

Potential failures can involve Qt platform plugins, display servers, clipboard/window behavior, or file-dialog integrations.

## 10. Runtime library inspection

Inspect the main executable/shared objects where useful:

```bash
ldd <path-to-executable>
```

Look for `not found` dependencies.

PyInstaller bundles many dependencies but still relies on parts of the host OS/runtime stack. Clean-system testing remains required.

## 11. GL/EGL/Qt troubleshooting baseline

If PySide6 or the packaged app reports graphics/runtime errors:

- confirm `libEGL`/graphics libraries are installed;
- verify the correct Qt platform plugin is bundled/available;
- test in a normal graphical session rather than a headless shell;
- inspect terminal output;
- compare with the Build Smoke environment.

Do not solve normal distribution issues by requiring users to run as root.

## 12. Permissions and executable bit

After copying/extracting a Linux artifact, confirm the launcher is executable:

```bash
ls -l <executable>
chmod +x <executable>   # only if the archive/copy process lost the expected bit
```

The distributed archive process should preserve required permissions so manual correction is not normally necessary.

## 13. Filesystem acceptance

Test source/output paths on the filesystems you intend to support, especially:

- ext4 or your primary local filesystem;
- removable storage if relevant;
- network mounts only if claimed;
- read-only/non-writable destinations to confirm safe failure;
- paths with spaces and Unicode.

Transaction recovery semantics should also be tested on claimed filesystems before production claims.

## 14. Archive unsigned onedir build

Current CI shape:

```bash
tar -czf DocMergeForge-Linux-unsigned.tar.gz -C dist DocMergeForge
```

Verify archive contents:

```bash
tar -tzf DocMergeForge-Linux-unsigned.tar.gz | head
```

Extract into a fresh directory and launch the extracted copy.

## 15. Generate SHA-256

```bash
sha256sum DocMergeForge-Linux-unsigned.tar.gz
```

Record the final distributed artifact hash.

## 16. Distro/runtime compatibility strategy

A Linux release should state what it actually supports. Possible strategies include:

- build on an intentionally old compatible glibc baseline;
- publish distro-specific packages;
- use a portable format such as AppImage;
- provide source installation for unsupported environments.

The repository currently does not implement a broad compatibility guarantee. Test the oldest distro/runtime you intend to list as supported.

## 17. Optional AppImage

AppImage is not currently part of the repository build pipeline. If added, document:

- toolchain/version;
- AppDir creation;
- desktop file/icon integration;
- Qt plugin/runtime bundling;
- FUSE/no-FUSE behavior;
- artifact signing/update metadata if used;
- launch on clean target distributions.

Do not present the current `.tar.gz` artifact as an AppImage.

## 18. Optional DEB/RPM packages

Native package formats are not currently automated. If added, verify:

- package metadata/versioning;
- dependencies;
- install paths;
- desktop/menu entries;
- upgrades;
- uninstall behavior;
- configuration/data preservation;
- package signatures/repository metadata if distributed through a package repository.

## 19. Container builds are not GUI acceptance

A container can help create deterministic build environments, but a successful container build does not prove the desktop app works in a real graphical session or on the target host distribution.

Always pair build automation with native launch tests.

## 20. Linux release evidence

Retain:

- commit/tag;
- distribution/version;
- kernel/architecture;
- glibc/runtime baseline;
- Python/PyInstaller versions;
- artifact filename/size/SHA-256;
- `ldd`/missing-library findings when relevant;
- X11/Wayland test result if claimed;
- clean-system launch test;
- PDF/DOCX packaged-app merge result;
- recovery/cancellation result;
- archive extraction/permission test.

## 21. Linux release checklist

- [ ] Correct commit/tag checked out.
- [ ] Python 3.12 environment prepared.
- [ ] required Qt/EGL runtime present.
- [ ] packaging preflight passes.
- [ ] clean onedir build passes.
- [ ] optional one-file build separately passes.
- [ ] packaged app launches outside repository.
- [ ] clean target distro launch passes.
- [ ] PDF/DOCX workflows pass.
- [ ] X11/Wayland claims are tested.
- [ ] minimum distro/glibc claim is tested.
- [ ] archive extraction preserves executable behavior.
- [ ] SHA-256 recorded.
- [ ] no unsupported package format is implied.

Return to the [Build Documentation Portal](README.md) for CI, verification, and troubleshooting.
