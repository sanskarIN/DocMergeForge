from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from docmergeforge.app.service import MergeApplicationService
from docmergeforge.audit.document import audit_tree
from docmergeforge.core.models import DocumentKind, DocxSettings, PdfSettings
from docmergeforge.discovery.scanner import scan
from docmergeforge.docx.engine import DocxMergeEngine
from docmergeforge.pdf.engine import PdfMergeEngine
from docmergeforge.presets.sql_full_mastery import create_sql_full_mastery_project
from docmergeforge.validation.compare import compare_docx, compare_pdf
from docmergeforge.validation.service import validate_part_set


def _parts(value: str) -> tuple[int, int]:
    start, end = value.split("-", 1)
    return int(start), int(end)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="docmergeforge")
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate", help="Discover and validate numbered document parts.")
    validate.add_argument("--input", required=True, type=Path)
    validate.add_argument("--parts", default="1-120")

    for name in ("pdf", "docx"):
        merge = sub.add_parser(name, help=f"Merge {name.upper()} files.")
        merge.add_argument("--input", required=True, type=Path)
        merge.add_argument("--parts", default="1-120")
        merge.add_argument("--output", required=True, type=Path)

    preset = sub.add_parser(
        "sql-preset",
        help="Run the SQL Full Mastery 120-part guided preset.",
    )
    preset.add_argument("--input", required=True, type=Path)
    preset.add_argument("--output-dir", required=True, type=Path)
    preset.add_argument("--dry-run", action="store_true")

    audit = sub.add_parser("audit", help="Audit PDF and DOCX manuscript content locally.")
    audit.add_argument("--input", required=True, type=Path)

    compare = sub.add_parser("compare", help="Compare merged outputs with source evidence.")
    compare.add_argument("--input", required=True, type=Path)
    compare.add_argument("--pdf-output", type=Path)
    compare.add_argument("--docx-output", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    service = MergeApplicationService()
    if args.command == "validate":
        start, end = _parts(args.parts)
        items = scan([args.input])
        payload: dict[str, object] = {}
        exit_code = 0
        for kind in (DocumentKind.PDF, DocumentKind.DOCX):
            validation_result = validate_part_set(items, kind, start, end)
            payload[kind.value] = {
                "ready": validation_result.ready,
                "missing": validation_result.missing_parts,
                "duplicates": validation_result.duplicate_parts,
                "found": validation_result.found_parts,
            }
            if not validation_result.ready:
                exit_code = 2
        print(json.dumps(payload, indent=2))
        return exit_code

    if args.command in {"pdf", "docx"}:
        start, end = _parts(args.parts)
        kind = DocumentKind.PDF if args.command == "pdf" else DocumentKind.DOCX
        items = [item for item in scan([args.input]) if item.kind == kind]
        validation_result = validate_part_set(items, kind, start, end)
        if not validation_result.ready:
            print(
                json.dumps(
                    {
                        "ready": False,
                        "missing": validation_result.missing_parts,
                        "duplicates": validation_result.duplicate_parts,
                    },
                    indent=2,
                )
            )
            return 2
        if kind == DocumentKind.PDF:
            PdfMergeEngine().merge(items, args.output, PdfSettings())
        else:
            DocxMergeEngine().merge(items, args.output, DocxSettings())
        print(str(args.output))
        return 0

    if args.command == "audit":
        findings = audit_tree(args.input)
        print(
            json.dumps(
                [
                    {
                        "code": finding.code,
                        "message": finding.message,
                        "path": str(finding.path),
                        "severity": finding.severity,
                    }
                    for finding in findings
                ],
                indent=2,
            )
        )
        return 0

    if args.command == "compare":
        if args.pdf_output is None and args.docx_output is None:
            print("At least one of --pdf-output or --docx-output is required.")
            return 2
        items = scan([args.input])
        payload: dict[str, object] = {}
        if args.pdf_output is not None:
            pdf_inputs = [item for item in items if item.kind == DocumentKind.PDF]
            payload["pdf"] = asdict(compare_pdf(pdf_inputs, args.pdf_output))
        if args.docx_output is not None:
            docx_inputs = [item for item in items if item.kind == DocumentKind.DOCX]
            payload["docx"] = compare_docx(docx_inputs, args.docx_output).to_dict()
        print(json.dumps(payload, indent=2))
        return 0

    project = create_sql_full_mastery_project(args.input, args.output_dir)
    if args.dry_run:
        dry_run = service.dry_run(project)
        print(
            json.dumps(
                {
                    "pdf_ready": dry_run.pdf.ready,
                    "docx_ready": dry_run.docx.ready,
                    "companions": len(dry_run.companions),
                    "ignored": len(dry_run.ignored),
                    "storage_sufficient": dry_run.storage.sufficient,
                },
                indent=2,
            )
        )
        return 0 if dry_run.pdf.ready and dry_run.docx.ready else 2
    service.run_sql_preset(project)
    print(str(args.output_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
