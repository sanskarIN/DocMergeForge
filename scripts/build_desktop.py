from __future__ import annotations

import argparse
import os
from pathlib import Path


def build_args(root: Path, *, one_file: bool = False) -> list[str]:
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the DocMergeForge desktop application.")
    parser.add_argument("--one-file", action="store_true", help="Build a single executable.")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository root.",
    )
    parsed = parser.parse_args(argv)

    try:
        import PyInstaller.__main__
    except ImportError as exc:
        raise SystemExit(
            "PyInstaller is required for packaging. Install it with 'pip install pyinstaller'."
        ) from exc

    root = parsed.root.resolve()
    if not (root / "pyproject.toml").exists():
        raise SystemExit(f"Not a DocMergeForge repository root: {root}")
    PyInstaller.__main__.run(build_args(root, one_file=parsed.one_file))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
