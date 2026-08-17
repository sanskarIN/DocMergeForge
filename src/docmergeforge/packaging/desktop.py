from __future__ import annotations

import os
from pathlib import Path


def validate_build_root(root: Path) -> Path:
    """Validate and return a resolved DocMergeForge repository root."""
    resolved = root.resolve()
    required = (
        resolved / "pyproject.toml",
        resolved / "src" / "docmergeforge" / "ui" / "main.py",
        resolved / "src" / "docmergeforge" / "ui" / "packaged_entry.py",
    )
    missing = [path.relative_to(resolved) for path in required if not path.is_file()]
    if missing:
        details = ", ".join(str(path) for path in missing)
        raise ValueError(f"Invalid DocMergeForge build root; missing: {details}")
    return resolved


def build_args(root: Path, *, one_file: bool = False) -> list[str]:
    """Return reproducible PyInstaller arguments for the desktop application."""
    root = root.resolve()
    entry = root / "src" / "docmergeforge" / "ui" / "packaged_entry.py"
    branding = root / "assets" / "branding"
    args = [
        str(entry),
        "--name",
        "DocMergeForge",
        "--windowed",
        "--clean",
        "--noconfirm",
        "--collect-submodules",
        "docmergeforge",
        "--collect-all",
        "docxcompose",
        "--collect-all",
        "docx",
        "--collect-all",
        "pypdf",
    ]
    if branding.exists():
        args.extend(["--add-data", f"{branding}{os.pathsep}assets/branding"])
    args.append("--onefile" if one_file else "--onedir")
    return args
