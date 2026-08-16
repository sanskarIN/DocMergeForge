from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

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
    write_project_report,
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
    pdf_count: int
    docx_count: int
    ignored: list[InputDocument]
    companions: list[InputDocument]
    storage: StorageEstimate

    @property
    def ready_for_available_kinds(self) -> bool:
        has_documents = self.pdf_count + self.docx_count > 0
        pdf_ready = self.pdf_count == 0 or self.pdf.ready
        docx_ready = self.docx_count == 0 or self.docx.ready
        return has_documents and pdf_ready and docx_ready


class MergeApplicationService:
    def discover(self, project: MergeProject) -> list[InputDocument]:
        return scan(project.source_folders, recursive=True)

    def dry_run(self, project: MergeProject) -> DryRunResult:
        inputs = self.discover(project)
        pdfs = [item for item in inputs if item.kind == DocumentKind.PDF]
        docxs = [item for item in inputs if item.kind == DocumentKind.DOCX]
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
        documents = [item.path for item in pdfs + docxs]
        estimate = require_storage(documents, project.output_folder)
        return DryRunResult(
            pdf=pdf_result,
            docx=docx_result,
            pdf_count=len(pdfs),
            docx_count=len(docxs),
            ignored=[item for item in inputs if item.kind == DocumentKind.OTHER],
            companions=[item for item in inputs if item.kind == DocumentKind.COMPANION],
            storage=estimate,
        )

    @staticmethod
    def _artifact(path: Path, kind: DocumentKind) -> OutputArtifact:
        return OutputArtifact(
            path,
            sha256_file(path),
            path.stat().st_size,
            kind,
            True,
        )

    def run_project(self, project: MergeProject) -> list[OutputArtifact]:
        inputs = self.discover(project)
        pdfs = [item for item in inputs if item.kind == DocumentKind.PDF]
        docxs = [item for item in inputs if item.kind == DocumentKind.DOCX]
        companions = [item for item in inputs if item.kind == DocumentKind.COMPANION]
        ignored = [item.path for item in inputs if item.kind == DocumentKind.OTHER]
        if not pdfs and not docxs:
            raise ValueError("No PDF or DOCX inputs were discovered for this project.")

        validations: dict[str, ValidationResult] = {}
        skipped: list[str] = []
        if pdfs:
            pdf_result = validate_part_set(
                inputs,
                DocumentKind.PDF,
                project.settings.expected_start,
                project.settings.expected_end,
            )
            validations["PDF"] = pdf_result
            if not pdf_result.ready:
                raise ValueError("PDF validation failed. Resolve missing or duplicate parts.")
        else:
            skipped.append("PDF")
        if docxs:
            docx_result = validate_part_set(
                inputs,
                DocumentKind.DOCX,
                project.settings.expected_start,
                project.settings.expected_end,
            )
            validations["DOCX"] = docx_result
            if not docx_result.ready:
                raise ValueError("DOCX validation failed. Resolve missing or duplicate parts.")
        else:
            skipped.append("DOCX")

        tracked = [item.path for item in pdfs + docxs + companions]
        before = snapshot_hashes(tracked)
        require_storage([item.path for item in pdfs + docxs], project.output_folder)
        project.output_folder.mkdir(parents=True, exist_ok=True)
        slug = re.sub(r"[^A-Za-z0-9]+", "_", project.name).strip("_") or "DocMergeForge"

        outputs: list[OutputArtifact] = []
        if pdfs:
            pdf_path = PdfMergeEngine().merge(
                pdfs,
                project.output_folder / f"{slug}_Master.pdf",
                project.settings.pdf,
                overwrite=project.settings.overwrite,
            )
            outputs.append(self._artifact(pdf_path, DocumentKind.PDF))
        if docxs:
            docx_path = DocxMergeEngine().merge(
                docxs,
                project.output_folder / f"{slug}_Master.docx",
                project.settings.docx,
                overwrite=project.settings.overwrite,
            )
            outputs.append(self._artifact(docx_path, DocumentKind.DOCX))

        changed = verify_unchanged(before)
        if changed:
            raise RuntimeError(f"Original integrity guarantee failed: {changed}")

        refs = [
            CompanionReference(item.part.number, item.path, item.sha256, item.size)
            for item in companions
        ]
        write_companion_index(
            refs,
            project.output_folder / "Companion_Code_Index.md",
            project.output_folder / "Companion_Code_Index.json",
        )
        write_project_report(
            validations,
            skipped,
            len(companions),
            project.output_folder / f"{slug}_Merge_Report.md",
            project.output_folder / f"{slug}_Merge_Report.html",
        )
        write_manifest(
            pdfs + docxs,
            outputs,
            ignored,
            project.warnings,
            project.output_folder / f"{slug}_Merge_Manifest.json",
            "Custom",
        )
        write_checksums(
            pdfs + docxs + companions,
            outputs,
            project.output_folder / f"{slug}_SHA256SUMS.txt",
        )
        write_publishing_checklist(
            project.output_folder / "Publishing_Checklist.md",
            f"Parts {project.settings.expected_start}–{project.settings.expected_end}",
        )
        return outputs

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

        pdf_path = PdfMergeEngine().merge(
            pdfs,
            project.output_folder / PDF_FILENAME,
            project.settings.pdf,
            overwrite=project.settings.overwrite,
        )
        docx_path = DocxMergeEngine().merge(
            docxs,
            project.output_folder / DOCX_FILENAME,
            project.settings.docx,
            overwrite=project.settings.overwrite,
        )

        changed = verify_unchanged(before)
        if changed:
            raise RuntimeError(f"Original integrity guarantee failed: {changed}")

        outputs = [
            self._artifact(pdf_path, DocumentKind.PDF),
            self._artifact(docx_path, DocumentKind.DOCX),
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
