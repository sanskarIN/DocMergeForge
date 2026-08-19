from __future__ import annotations

import argparse
import json
from pathlib import Path

from docmergeforge.project.drift import evaluate_project_sync_drift
from docmergeforge.project.store import load_project


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Check whether a DocMergeForge project's saved selected_files still matches "
            "the deterministic automatic numbered/in-range source proposal."
        )
    )
    parser.add_argument("--project", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    project = load_project(args.project)
    result = evaluate_project_sync_drift(project)
    payload = result.to_dict()
    payload["project"] = str(args.project)
    print(json.dumps(payload, indent=2))
    return result.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
