from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from docmergeforge.app.service import DryRunResult, MergeApplicationService
from docmergeforge.core.models import DocumentKind, MergeProject
from docmergeforge.docx.engine import DocxMergeEngine
from docmergeforge.presets.sql_full_mastery import DOCX_FILENAME, PDF_FILENAME, PRESET_NAME
from docmergeforge.project.selection import project_merge_documents
from docmergeforge.utilities.output_naming import render_project_basename


@dataclass(slots=True, frozen=True)
class PreflightEvidence:
    result: DryRunResult
    ordered_pdf: list[Path]
    ordered_docx: list[Path]
    expected_outputs: list[Path]
    docx_conflict_count: int


def build_preflight(
    project: MergeProject,
    *,
    allow_encrypted_pdf: bool = False,
) -> PreflightEvidence:
    """Build read-only merge evidence without creating final books."""
    service = MergeApplicationService()
    inputs = service.discover(project)
    result = service.dry_run(project, allow_encrypted_pdf=allow_encrypted_pdf)
    pdfs = project_merge_documents(project, inputs, DocumentKind.PDF)
    docxs = project_merge_documents(project, inputs, DocumentKind.DOCX)

    if project.selected_files:
        ordered_pdf = [item.path for item in pdfs]
        ordered_docx = [item.path for item in docxs]
    else:
        ordered_pdf = [
            item.path
            for item in sorted(
                pdfs,
                key=lambda item: (
                    item.part.number is None,
                    item.part.number or 0,
                    item.path.name.casefold(),
                ),
            )
        ]
        ordered_docx = [
            item.path
            for item in sorted(
                docxs,
                key=lambda item: (
                    item.part.number is None,
                    item.part.number or 0,
                    item.path.name.casefold(),
                ),
            )
        ]

    if project.name == PRESET_NAME:
        expected_outputs = [
            project.output_folder / PDF_FILENAME,
            project.output_folder / DOCX_FILENAME,
        ]
    else:
        basename = render_project_basename(project)
        expected_outputs = []
        if pdfs:
            expected_outputs.append(project.output_folder / f"{basename}.pdf")
        if docxs:
            expected_outputs.append(project.output_folder / f"{basename}.docx")

    conflicts = DocxMergeEngine.analyze_conflicts(docxs) if docxs else []
    return PreflightEvidence(
        result=result,
        ordered_pdf=ordered_pdf,
        ordered_docx=ordered_docx,
        expected_outputs=expected_outputs,
        docx_conflict_count=len(conflicts),
    )


def format_preflight(evidence: PreflightEvidence) -> str:
    result = evidence.result
    storage = result.storage
    lines = [
        "DRY RUN — no final books have been created",
        "",
        f"PDF inputs: {result.pdf_count}",
        f"PDF missing parts: {result.pdf.missing_parts or 'none'}",
        f"PDF duplicate parts: {result.pdf.duplicate_parts or 'none'}",
        f"DOCX inputs: {result.docx_count}",
        f"DOCX missing parts: {result.docx.missing_parts or 'none'}",
        f"DOCX duplicate parts: {result.docx.duplicate_parts or 'none'}",
        f"Likely DOCX package conflicts: {evidence.docx_conflict_count}",
        f"Companion packages ignored as merge inputs: {len(result.companions)}",
        f"Other ignored files: {len(result.ignored)}",
        "",
        "Storage estimate:",
        f"  Source bytes: {storage.source_bytes}",
        f"  Temporary bytes: {storage.temporary_bytes}",
        f"  Projected output bytes: {storage.projected_output_bytes}",
        f"  Required free bytes: {storage.safe_required_bytes}",
        f"  Available free bytes: {storage.free_bytes}",
        f"  Sufficient: {'YES' if storage.sufficient else 'NO'}",
        "",
        "Expected outputs:",
    ]
    lines.extend(f"  {path}" for path in evidence.expected_outputs)
    lines.extend(["", "PDF order:"])
    lines.extend(f"  {index:03d}. {path}" for index, path in enumerate(evidence.ordered_pdf, 1))
    lines.extend(["", "DOCX order:"])
    lines.extend(f"  {index:03d}. {path}" for index, path in enumerate(evidence.ordered_docx, 1))
    return "\n".join(lines)
