from __future__ import annotations

import argparse
import json
from pathlib import Path

from docmergeforge.docx.word_merge_acceptance import run_word_merge_acceptance


def _positive_seconds(value: str) -> int:
    seconds = int(value)
    if seconds < 1:
        raise argparse.ArgumentTypeError("timeout must be at least one second")
    return seconds


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run the explicit Microsoft Word multi-document merge prototype and emit "
            "measured acceptance evidence."
        )
    )
    parser.add_argument(
        "--input",
        dest="inputs",
        action="append",
        required=True,
        type=Path,
        help="DOCX source in merge order. Repeat for each source.",
    )
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--evidence", required=True, type=Path)
    parser.add_argument("--timeout", default=900, type=_positive_seconds)
    parser.add_argument(
        "--start-each-on-new-page",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.evidence.exists():
        raise SystemExit(f"Refusing to overwrite existing evidence: {args.evidence}")

    evidence = run_word_merge_acceptance(
        args.inputs,
        args.output,
        timeout_seconds=args.timeout,
        start_each_on_new_page=args.start_each_on_new_page,
    )
    args.evidence.parent.mkdir(parents=True, exist_ok=True)
    args.evidence.write_text(
        json.dumps(evidence.to_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(args.evidence)
    return 0 if evidence.accepted else 2


if __name__ == "__main__":
    raise SystemExit(main())
