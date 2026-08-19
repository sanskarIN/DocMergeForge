from __future__ import annotations

import argparse
import subprocess
from collections.abc import Sequence
from pathlib import Path

DEFAULT_REFERENCE = Path("docs/repository-reference.md")


def tracked_files(repo_root: Path) -> list[str]:
    """Return every Git-tracked file path relative to *repo_root*."""
    completed = subprocess.run(
        ["git", "-C", str(repo_root), "ls-files", "-z"],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return sorted(path for path in completed.stdout.split("\0") if path)


def missing_references(reference_text: str, paths: Sequence[str]) -> list[str]:
    """Return tracked paths that are not explicitly backticked in the reference."""
    return sorted(path for path in paths if f"`{path}`" not in reference_text)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check that every tracked file is documented in the repository reference."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository root to inspect.",
    )
    parser.add_argument(
        "--reference",
        type=Path,
        default=DEFAULT_REFERENCE,
        help="Reference document path relative to the repository root.",
    )
    args = parser.parse_args(argv)

    root = args.root.resolve()
    reference = args.reference
    if reference.is_absolute():
        reference_path = reference
    else:
        reference_path = root / reference

    try:
        reference_text = reference_path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"Unable to read repository reference: {reference_path}: {exc}")
        return 2

    try:
        paths = tracked_files(root)
    except FileNotFoundError:
        print("Unable to inspect tracked files: git executable was not found.")
        return 2
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or "").strip()
        suffix = f": {detail}" if detail else ""
        print(f"Unable to inspect tracked files with git ls-files{suffix}")
        return 2
    except OSError as exc:
        print(f"Unable to inspect tracked files: {exc}")
        return 2

    missing = missing_references(reference_text, paths)
    if missing:
        print("Tracked files missing from docs/repository-reference.md:")
        for path in missing:
            print(f"- {path}")
        return 1

    print(f"Repository reference covers all {len(paths)} tracked files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
