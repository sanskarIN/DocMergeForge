from __future__ import annotations

import argparse
from pathlib import Path

from docmergeforge.packaging.provenance import write_provenance


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Write privacy-safe DocMergeForge build provenance JSON."
    )
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--mode", required=True, choices=("onedir", "onefile"))
    parser.add_argument("--artifact-label", required=True)
    args = parser.parse_args()

    path = write_provenance(
        args.output,
        build_mode=args.mode,
        artifact_label=args.artifact_label,
    )
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
