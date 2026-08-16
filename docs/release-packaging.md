# Release Packaging

Release artifacts should be built from tagged commits after quality gates pass.

- Windows: PyInstaller executable plus portable ZIP; installer can be produced with a maintained packaging tool.
- macOS: PyInstaller app bundle/package.
- Linux: PyInstaller portable bundle; AppImage can be produced in CI.
- Every release artifact should have SHA-256 checksums.
- Do not claim code signing unless the produced binary is actually signed and verified.

Stable `1.0.0` must wait for the full quality gate described in `README.md` and `what_changed.md`.
