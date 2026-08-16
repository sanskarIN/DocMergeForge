from __future__ import annotations

import html
import json
import platform
from datetime import UTC, datetime
from pathlib import Path

from docmergeforge import __version__
from docmergeforge.core.models import (
    CompanionReference,
    InputDocument,
    OutputArtifact,
    ValidationResult,
)


def write_checksums(
    items: list[InputDocument],
    outputs: list[OutputArtifact],
    path: Path,
) -> None:
    lines = [f"{item.sha256}  {item.path}" for item in items]
    lines.extend(f"{item.sha256}  {item.path}" for item in outputs)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_manifest(
    inputs: list[InputDocument],
    outputs: list[OutputArtifact],
    ignored: list[Path],
    warnings: list[str],
    path: Path,
    profile: str,
) -> None:
    payload = {
        "app_version": __version__,
        "timestamp": datetime.now(UTC).isoformat(),
        "os": platform.platform(),
        "profile": profile,
        "source_order": [item.to_dict() for item in inputs],
        "outputs": [
            {
                "path": str(item.path),
                "sha256": item.sha256,
                "size": item.size,
                "kind": item.kind.value,
                "validation_passed": item.validation_passed,
            }
            for item in outputs
        ],
        "ignored_files": [str(item) for item in ignored],
        "warnings": warnings,
        "code_policy": "Companion code remains separate and unchanged.",
    }
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def write_companion_index(
    companions: list[CompanionReference],
    md_path: Path,
    json_path: Path,
) -> None:
    payload = [
        {
            "part": item.part,
            "path": str(item.path),
            "sha256": item.sha256,
            "size": item.size,
        }
        for item in companions
    ]
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    lines = [
        "# Companion Code Index",
        "",
        "> Companion code is indexed only; it is never merged.",
        "",
    ]
    for item in companions:
        label = f"Part {item.part}" if item.part is not None else "Unnumbered"
        lines.append(f"- **{label}** — `{item.path}` — `{item.sha256}`")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _summary(result: ValidationResult) -> str:
    return (
        f"Expected: {len(result.expected_parts)} | Found: {len(result.found_parts)} | "
        f"Missing: {len(result.missing_parts)} | Duplicates: {len(result.duplicate_parts)} | "
        f"Ready: {'YES' if result.ready else 'NO'}"
    )


def write_project_report(
    results: dict[str, ValidationResult],
    skipped_kinds: list[str],
    companion_count: int,
    md_path: Path,
    html_path: Path,
) -> None:
    lines = [
        "# DocMergeForge Merge Report",
        "",
        "## Validation",
        "",
    ]
    for label, result in results.items():
        lines.append(f"- {label}: {_summary(result)}")
    for label in skipped_kinds:
        lines.append(f"- {label}: SKIPPED — no selected inputs")
    lines.extend(
        [
            f"- Companion code packages detected: {companion_count}",
            "- Companion code packages merged: 0",
            "- Reason: Per-part code remains intentionally independent.",
        ]
    )
    for label, result in results.items():
        lines.extend(["", f"## {label} Diagnostics"])
        if not result.diagnostics:
            lines.append("- No diagnostics.")
        for diagnostic in result.diagnostics:
            lines.append(f"- **{diagnostic.level.value}** — {diagnostic.message}")
    md = "\n".join(lines) + "\n"
    md_path.write_text(md, encoding="utf-8")

    escaped = html.escape(md)
    html_path.write_text(
        "<!doctype html><html><head><meta charset='utf-8'>"
        "<title>DocMergeForge Report</title>"
        "<style>body{font-family:system-ui;max-width:1000px;margin:40px auto;"
        "padding:0 24px;line-height:1.55}pre{white-space:pre-wrap;"
        "background:#f5f5f5;padding:20px;border-radius:12px}</style></head>"
        "<body><h1>DocMergeForge Merge Report</h1><pre>" + escaped + "</pre></body></html>",
        encoding="utf-8",
    )


def write_report(
    pdf_result: ValidationResult,
    docx_result: ValidationResult,
    companion_count: int,
    md_path: Path,
    html_path: Path,
) -> None:
    write_project_report(
        {"PDF": pdf_result, "DOCX": docx_result},
        [],
        companion_count,
        md_path,
        html_path,
    )


def write_publishing_checklist(path: Path, parts_label: str = "Parts 1–120") -> None:
    items = [
        "Master PDF exists",
        "Master DOCX exists",
        f"{parts_label} verified",
        "PDF page sequence reviewed",
        "DOCX structure reviewed",
        "Table of contents reviewed",
        "Bookmarks reviewed",
        "Hyperlinks reviewed",
        "Cover reviewed",
        "Author name verified",
        "Edition verified",
        "Price verified",
        "GitHub URL verified",
        "Contact email verified",
        "Companion-code index generated",
        "Checksums generated",
        "Backup completed",
        "Final human review completed",
    ]
    content = "# Publishing Checklist\n\n" + "\n".join(f"- [ ] {item}" for item in items)
    path.write_text(content + "\n", encoding="utf-8")
