from __future__ import annotations

import argparse
import json
from pathlib import Path

from docmergeforge.docx.libreoffice_uno_acceptance import (
    run_libreoffice_uno_acceptance,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Merge an explicit ordered DOCX set through the supervised LibreOffice UNO "
            "acceptance prototype and write measured JSON evidence."
        )
    )
    parser.add_argument(
        "--input",
        action="append",
        type=Path,
        required=True,
        dest="inputs",
        help="DOCX source. Repeat in the exact intended merge order.",
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument(
        "--start-each-on-new-page",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.timeout < 1:
        raise SystemExit("--timeout must be at least one second")

    evidence_path: Path = args.evidence
    if evidence_path.exists():
        raise SystemExit(
            f"Refusing to overwrite existing LibreOffice UNO evidence: {evidence_path}"
        )
    evidence_path.parent.mkdir(parents=True, exist_ok=True)

    evidence = run_libreoffice_uno_acceptance(
        args.inputs,
        args.output,
        timeout_seconds=args.timeout,
        start_each_on_new_page=args.start_each_on_new_page,
    )
    evidence_path.write_text(
        json.dumps(evidence.to_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(evidence_path)
    return 0 if evidence.accepted else 2


if __name__ == "__main__":
    raise SystemExit(main())
