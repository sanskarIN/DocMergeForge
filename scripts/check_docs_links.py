from __future__ import annotations

import argparse
from pathlib import Path

from docmergeforge.diagnostics.docs_links import find_broken_links


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check local Markdown links in DocMergeForge docs."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository root to scan.",
    )
    args = parser.parse_args(argv)

    broken = find_broken_links(args.root)
    if broken:
        print("Broken local Markdown links detected:")
        for item in broken:
            print(f"- {item.source}: {item.target} -> {item.resolved}")
        return 1

    print("Documentation link check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
