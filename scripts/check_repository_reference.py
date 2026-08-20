from __future__ import annotations

import argparse
import subprocess
from collections.abc import Sequence
from pathlib import Path

DEFAULT_REFERENCES = (
    Path("docs/repository-reference.md"),
    Path("docs/repository-reference-cross-platform.md"),
)


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
    """Return tracked paths that are not explicitly backticked in the reference corpus."""
    return sorted(path for path in paths if f"`{path}`" not in reference_text)


def _resolve_reference(root: Path, reference: Path) -> Path:
    return reference if reference.is_absolute() else root / reference


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check that every tracked file is documented in the repository references."
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
        action="append",
        default=None,
        help=(
            "Reference document path relative to the repository root. Repeat to combine "
            "multiple references. Defaults to the main reference plus maintained addenda."
        ),
    )
    args = parser.parse_args(argv)

    root = args.root.resolve()
    references = args.reference or list(DEFAULT_REFERENCES)
    reference_parts: list[str] = []
    for reference in references:
        reference_path = _resolve_reference(root, reference)
        try:
            reference_parts.append(reference_path.read_text(encoding="utf-8"))
        except OSError as exc:
            print(f"Unable to read repository reference: {reference_path}: {exc}")
            return 2
    reference_text = "\n".join(reference_parts)

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
        print("Tracked files missing from the repository reference corpus:")
        for path in missing:
            print(f"- {path}")
        return 1

    print(
        f"Repository reference corpus covers all {len(paths)} tracked files "
        f"across {len(references)} document(s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
