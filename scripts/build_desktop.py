from __future__ import annotations

import argparse
from pathlib import Path

from docmergeforge.packaging.desktop import build_args, validate_build_root


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the DocMergeForge desktop application.")
    parser.add_argument("--one-file", action="store_true", help="Build a single executable.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate the desktop packaging configuration without running PyInstaller.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository root.",
    )
    parsed = parser.parse_args(argv)

    try:
        root = validate_build_root(parsed.root)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    if parsed.check:
        print(f"Desktop build configuration OK: {root}")
        return 0

    try:
        import PyInstaller.__main__
    except ImportError as exc:
        raise SystemExit(
            "PyInstaller is required for packaging. Install it with 'pip install pyinstaller'."
        ) from exc

    PyInstaller.__main__.run(build_args(root, one_file=parsed.one_file))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
