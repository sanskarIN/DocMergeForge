from __future__ import annotations

from dataclasses import dataclass

from docmergeforge.core.models import (
    CompanionReference,
    DocumentKind,
    InputDocument,
    MergeProject,
    OutputArtifact,
    ValidationResult,
)
from docmergeforge.discovery.scanner import scan
from docmergeforge.docx.engine import DocxMergeEngine
from docmergeforge.pdf.engine import PdfMergeEngine
from docmergeforge.presets.sql_full_mastery import (
    CHECKSUMS_FILENAME,
    DOCX_FILENAME,
    MANIFEST_FILENAME,
    PDF_FILENAME,
    REPORT_HTML_FILENAME,
    REPORT_MD_FILENAME,
)
from docmergeforge.reports.generator import (
    write_checksums,
    write_companion_index,
    write_manifest,
    write_publishing_checklist,
    write_report,
)
from docmergeforge.utilities.hashing import sha256_file, snapshot_hashes, verify_unchanged
from docmergeforge.utilities.storage import StorageEstimate, require_storage
from docmergeforge.validation.service import validate_part_set


@dataclass(slots=True, frozen=True)
class DryRunResult:
    pdf: ValidationResult
    docx: ValidationResult
    ignored: list[InputDocument]
    companions: list[InputDocument]
    storage: StorageEstimate


class MergeApplicationService:
    def discover(self, project: MergeProject) -> list[InputDocument]:
        return scan(project.source_folders, recursive=True)

    def dry_run(self, project: MergeProject) -> DryRunResult:
        inputs = self.discover(project)
        pdf_result = validate_part_set(
            inputs,
            DocumentKind.PDF,
            project.settings.expected_start,
            project.settings.expected_end,
        )
        docx_result = validate_part_set(
            inputs,
            DocumentKind.DOCX,
            project.settings.expected_start,
            project.settings.expected_end,
        )
        docs = [item.path for item in inputs if item.kind in {DocumentKind.PDF, DocumentKind.DOCX}]
        estimate = require_storage(docs, project.output_folder)
        return DryRunResult(
            pdf=pdf_result,
            docx=docx_result,
            ignored=[item for item in inputs if item.kind == DocumentKind.OTHER],
            companions=[item for item in inputs if item.kind == DocumentKind.COMPANION],
            storage=estimate,
        )

    def run_sql_preset(self, project: MergeProject) -> list[OutputArtifact]:
        inputs = self.discover(project)
        pdfs = [item for item in inputs if item.kind == DocumentKind.PDF]
        docxs = [item for item in inputs if item.kind == DocumentKind.DOCX]
        companions = [item for item in inputs if item.kind == DocumentKind.COMPANION]
        ignored = [item.path for item in inputs if item.kind == DocumentKind.OTHER]

        pdf_result = validate_part_set(
            inputs,
            DocumentKind.PDF,
            project.settings.expected_start,
            project.settings.expected_end,
        )
        docx_result = validate_part_set(
            inputs,
            DocumentKind.DOCX,
            project.settings.expected_start,
            project.settings.expected_end,
        )
        if not pdf_result.ready or not docx_result.ready:
            raise ValueError(
                "Mandatory validation failed. Run dry-run and resolve missing/duplicate parts."
            )

        tracked = [item.path for item in pdfs + docxs + companions]
        before = snapshot_hashes(tracked)
        require_storage([item.path for item in pdfs + docxs], project.output_folder)
        project.output_folder.mkdir(parents=True, exist_ok=True)

        pdf_path = project.output_folder / PDF_FILENAME
        docx_path = project.output_folder / DOCX_FILENAME
        pdf_path = PdfMergeEngine().merge(
            pdfs,
            pdf_path,
            project.settings.pdf,
            overwrite=project.settings.overwrite,
        )
        docx_path = DocxMergeEngine().merge(
            docxs,
            docx_path,
            project.settings.docx,
            overwrite=project.settings.overwrite,
        )

        changed = verify_unchanged(before)
        if changed:
            raise RuntimeError(f"Original integrity guarantee failed: {changed}")

        outputs = [
            OutputArtifact(
                pdf_path,
                sha256_file(pdf_path),
                pdf_path.stat().st_size,
                DocumentKind.PDF,
                True,
            ),
            OutputArtifact(
                docx_path,
                sha256_file(docx_path),
                docx_path.stat().st_size,
                DocumentKind.DOCX,
                True,
            ),
        ]
        refs = [
            CompanionReference(item.part.number, item.path, item.sha256, item.size)
            for item in companions
        ]
        write_companion_index(
            refs,
            project.output_folder / "Companion_Code_Index.md",
            project.output_folder / "Companion_Code_Index.json",
        )
        write_report(
            pdf_result,
            docx_result,
            len(companions),
            project.output_folder / REPORT_MD_FILENAME,
            project.output_folder / REPORT_HTML_FILENAME,
        )
        write_manifest(
            pdfs + docxs,
            outputs,
            ignored,
            project.warnings,
            project.output_folder / MANIFEST_FILENAME,
            "Master eBook",
        )
        write_checksums(
            pdfs + docxs + companions,
            outputs,
            project.output_folder / CHECKSUMS_FILENAME,
        )
        write_publishing_checklist(project.output_folder / "Publishing_Checklist.md")
        return outputs
