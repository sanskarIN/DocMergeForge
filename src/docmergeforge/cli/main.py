from __future__ import annotations

import argparse
import fnmatch
import getpass
import json
from dataclasses import asdict
from pathlib import Path

from docmergeforge.app.preflight import build_preflight
from docmergeforge.app.service import DryRunResult, MergeApplicationService
from docmergeforge.audit.document import audit_tree
from docmergeforge.core.models import (
    DocumentKind,
    DocxSettings,
    InputDocument,
    MergeProject,
    MergeSettings,
    PdfSettings,
)
from docmergeforge.discovery.part_detection import natural_key
from docmergeforge.discovery.scanner import scan
from docmergeforge.docx.engine import DocxMergeEngine
from docmergeforge.pdf.engine import PdfMergeEngine
from docmergeforge.pdf.passwords import verify_pdf_password
from docmergeforge.presets.sql_full_mastery import PRESET_NAME, create_sql_full_mastery_project
from docmergeforge.project.store import load_project, save_project
from docmergeforge.validation.compare import compare_docx, compare_pdf
from docmergeforge.validation.service import validate_part_set


def _parts(value: str) -> tuple[int, int]:
    start, end = value.split("-", 1)
    start_number, end_number = int(start), int(end)
    if start_number < 1 or end_number < start_number:
        raise argparse.ArgumentTypeError("parts must be a positive range such as 1-120")
    return start_number, end_number


def _dry_run_payload(result: DryRunResult) -> dict[str, object]:
    return {
        "pdf_count": result.pdf_count,
        "pdf_ready": result.pdf.ready,
        "pdf_missing": result.pdf.missing_parts,
        "pdf_duplicates": result.pdf.duplicate_parts,
        "docx_count": result.docx_count,
        "docx_ready": result.docx.ready,
        "docx_missing": result.docx.missing_parts,
        "docx_duplicates": result.docx.duplicate_parts,
        "ready_for_available_kinds": result.ready_for_available_kinds,
        "companions": len(result.companions),
        "ignored": len(result.ignored),
        "storage": {
            "source_bytes": result.storage.source_bytes,
            "temporary_bytes": result.storage.temporary_bytes,
            "projected_output_bytes": result.storage.projected_output_bytes,
            "safe_required_bytes": result.storage.safe_required_bytes,
            "free_bytes": result.storage.free_bytes,
            "sufficient": result.storage.sufficient,
        },
    }


def _preflight_payload(project: MergeProject, allow_encrypted_pdf: bool) -> dict[str, object]:
    evidence = build_preflight(project, allow_encrypted_pdf=allow_encrypted_pdf)
    payload = _dry_run_payload(evidence.result)
    payload.update(
        {
            "ordered_pdf": [str(path) for path in evidence.ordered_pdf],
            "ordered_docx": [str(path) for path in evidence.ordered_docx],
            "expected_outputs": [str(path) for path in evidence.expected_outputs],
            "docx_conflict_count": evidence.docx_conflict_count,
        }
    )
    return payload


def _filter_pattern(items: list[InputDocument], pattern: str | None) -> list[InputDocument]:
    if not pattern:
        return items
    normalized_pattern = pattern.casefold()
    return [item for item in items if fnmatch.fnmatch(item.path.name.casefold(), normalized_pattern)]


def _ordered_items(items: list[InputDocument], natural_sort: bool) -> list[InputDocument]:
    if natural_sort:
        return sorted(
            items,
            key=lambda item: (
                item.part.number is None,
                item.part.number if item.part.number is not None else 10**12,
                natural_key(item.path.name),
            ),
        )
    return sorted(items, key=lambda item: item.path.name.casefold())


def _collect_pdf_passwords(items: list[InputDocument]) -> dict[Path, str] | None:
    passwords: dict[Path, str] = {}
    encrypted = [item for item in items if item.kind == DocumentKind.PDF and item.encrypted]
    for item in encrypted:
        while True:
            try:
                password = getpass.getpass(f"Password for encrypted PDF {item.path}: ")
            except (EOFError, KeyboardInterrupt):
                passwords.clear()
                return None
            if verify_pdf_password(item.path, password):
                passwords[item.path] = password
                break
            print(f"Incorrect password for {item.path.name}; try again or press Ctrl+C to cancel.")
    return passwords


def _add_discovery_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--pattern",
        help="Optional filename glob, for example 'Part *.pdf'.",
    )
    parser.add_argument(
        "--natural-sort",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Use natural part-number ordering (default); --no-natural-sort uses filename order.",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="docmergeforge")
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate", help="Discover and validate numbered document parts.")
    validate.add_argument("--input", required=True, type=Path)
    validate.add_argument("--parts", default="1-120", type=_parts)
    _add_discovery_options(validate)

    for name in ("pdf", "docx"):
        merge_kind = sub.add_parser(name, help=f"Merge {name.upper()} files.")
        merge_kind.add_argument("--input", required=True, type=Path)
        merge_kind.add_argument("--parts", default="1-120", type=_parts)
        merge_kind.add_argument("--output", required=True, type=Path)
        _add_discovery_options(merge_kind)

    preset = sub.add_parser(
        "sql-preset",
        help="Run the SQL Full Mastery 120-part guided preset.",
    )
    preset.add_argument("--input", required=True, type=Path)
    preset.add_argument("--output-dir", required=True, type=Path)
    preset.add_argument("--dry-run", action="store_true")

    project_create = sub.add_parser("project-create", help="Create a reusable merge project file.")
    project_create.add_argument("--input", required=True, type=Path)
    project_create.add_argument("--output-dir", required=True, type=Path)
    project_create.add_argument("--project-file", required=True, type=Path)
    project_create.add_argument("--name", default="DocMergeForge Project")
    project_create.add_argument("--parts", default="1-120", type=_parts)
    project_create.add_argument("--sql-preset", action="store_true")

    project_merge = sub.add_parser("merge", help="Run a reusable DocMergeForge project file.")
    project_merge.add_argument("--project", required=True, type=Path)
    project_merge.add_argument("--dry-run", action="store_true")

    audit = sub.add_parser("audit", help="Audit PDF and DOCX manuscript content locally.")
    audit.add_argument("--input", required=True, type=Path)

    compare = sub.add_parser("compare", help="Compare merged outputs with source evidence.")
    compare.add_argument("--input", required=True, type=Path)
    compare.add_argument("--pdf-output", type=Path)
    compare.add_argument("--docx-output", type=Path)
    return parser


def _run_direct_merge(args: argparse.Namespace) -> int:
    start, end = args.parts
    kind = DocumentKind.PDF if args.command == "pdf" else DocumentKind.DOCX
    items = [item for item in scan([args.input]) if item.kind == kind]
    items = _ordered_items(_filter_pattern(items, args.pattern), args.natural_sort)
    passwords = _collect_pdf_passwords(items) if kind == DocumentKind.PDF else {}
    if passwords is None:
        return 130
    try:
        validation_result = validate_part_set(
            items,
            kind,
            start,
            end,
            allow_encrypted_pdf=bool(passwords),
        )
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
            PdfMergeEngine().merge(
                items,
                args.output,
                PdfSettings(),
                preserve_order=True,
                password_provider=lambda path: passwords.get(path),
            )
        else:
            DocxMergeEngine().merge(
                items,
                args.output,
                DocxSettings(),
                preserve_order=True,
            )
        print(str(args.output))
        return 0
    finally:
        passwords.clear()


def _run_project(project: MergeProject, dry_run: bool) -> int:
    service = MergeApplicationService()
    inputs = service.discover(project)
    passwords = _collect_pdf_passwords(inputs)
    if passwords is None:
        return 130
    try:
        if dry_run:
            payload = _preflight_payload(project, allow_encrypted_pdf=bool(passwords))
            print(json.dumps(payload, indent=2))
            if project.name == PRESET_NAME:
                return 0 if payload["pdf_ready"] and payload["docx_ready"] else 2
            return 0 if payload["ready_for_available_kinds"] else 2

        def provider(path: Path) -> str | None:
            return passwords.get(path)

        if project.name == PRESET_NAME:
            service.run_sql_preset(project, pdf_password_provider=provider)
        else:
            service.run_project(project, pdf_password_provider=provider)
        print(str(project.output_folder))
        return 0
    finally:
        passwords.clear()


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "validate":
        start, end = args.parts
        items = _ordered_items(
            _filter_pattern(scan([args.input]), args.pattern),
            args.natural_sort,
        )
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
        return _run_direct_merge(args)

    if args.command == "project-create":
        if args.sql_preset:
            project = create_sql_full_mastery_project(args.input, args.output_dir)
        else:
            start, end = args.parts
            project = MergeProject(
                name=args.name,
                source_folders=[args.input],
                output_folder=args.output_dir,
                settings=MergeSettings(expected_start=start, expected_end=end),
            )
        save_project(project, args.project_file)
        print(str(args.project_file))
        return 0

    if args.command == "merge":
        return _run_project(load_project(args.project), args.dry_run)

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
        compare_payload: dict[str, object] = {}
        if args.pdf_output is not None:
            pdf_inputs = [item for item in items if item.kind == DocumentKind.PDF]
            compare_payload["pdf"] = asdict(compare_pdf(pdf_inputs, args.pdf_output))
        if args.docx_output is not None:
            docx_inputs = [item for item in items if item.kind == DocumentKind.DOCX]
            compare_payload["docx"] = compare_docx(docx_inputs, args.docx_output).to_dict()
        print(json.dumps(compare_payload, indent=2))
        return 0

    project = create_sql_full_mastery_project(args.input, args.output_dir)
    return _run_project(project, args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
