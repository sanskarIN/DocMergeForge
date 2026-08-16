from __future__ import annotations

import os
from pathlib import Path


def build_args(root: Path, *, one_file: bool = False) -> list[str]:
    """Return reproducible PyInstaller arguments for the desktop application."""
    entry = root / "src" / "docmergeforge" / "ui" / "main.py"
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
