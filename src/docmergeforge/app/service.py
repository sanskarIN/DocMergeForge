from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from docmergeforge.core.exceptions import MergeCancelled
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
from docmergeforge.pdf.engine import PasswordProvider, PdfMergeEngine
from docmergeforge.presets.sql_full_mastery import (
    CHECKSUMS_FILENAME,
    DOCX_FILENAME,
    MANIFEST_FILENAME,
    PDF_FILENAME,
    REPORT_HTML_FILENAME,
    REPORT_MD_FILENAME,
)
from docmergeforge.project.selection import apply_project_selection
from docmergeforge.reports.generator import (
    write_checksums,
    write_companion_index,
    write_manifest,
    write_project_report,
    write_publishing_checklist,
    write_report,
)
from docmergeforge.utilities.hashing import sha256_file, snapshot_hashes, verify_unchanged
from docmergeforge.utilities.output_naming import render_project_basename
from docmergeforge.utilities.output_transaction import OutputTransaction, StagedOutput
from docmergeforge.utilities.storage import StorageEstimate, require_storage
from docmergeforge.validation.service import validate_part_set

ProgressCallback = Callable[[str, int, int, Path | None], None]
CancellationCallback = Callable[[], bool]


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
        discovered = scan(project.source_folders, recursive=True)
        return apply_project_selection(discovered, project.selected_files)

    def dry_run(
        self,
        project: MergeProject,
        *,
        allow_encrypted_pdf: bool = False,
    ) -> DryRunResult:
        inputs = self.discover(project)
        pdfs = [item for item in inputs if item.kind == DocumentKind.PDF]
        docxs = [item for item in inputs if item.kind == DocumentKind.DOCX]
        pdf_result = validate_part_set(
            inputs,
            DocumentKind.PDF,
            project.settings.expected_start,
            project.settings.expected_end,
            allow_encrypted_pdf=allow_encrypted_pdf,
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
    def _staged_artifact(entry: StagedOutput, kind: DocumentKind) -> OutputArtifact:
        return OutputArtifact(
            entry.final_path,
            sha256_file(entry.staging_path),
            entry.staging_path.stat().st_size,
            kind,
            True,
        )

    @staticmethod
    def _check_cancelled(cancelled: CancellationCallback | None) -> None:
        if cancelled and cancelled():
            raise MergeCancelled("Merge cancelled safely before output promotion.")

    @staticmethod
    def _emit(
        progress: ProgressCallback | None,
        stage: str,
        current: int,
        total: int,
        path: Path | None = None,
    ) -> None:
        if progress:
            progress(stage, current, total, path)

    @staticmethod
    def _stage_report(
        transaction: OutputTransaction,
        path: Path,
    ) -> StagedOutput:
        return transaction.stage(path, overwrite=True)

    def run_project(
        self,
        project: MergeProject,
        *,
        progress: ProgressCallback | None = None,
        cancelled: CancellationCallback | None = None,
        pdf_password_provider: PasswordProvider | None = None,
    ) -> list[OutputArtifact]:
        self._check_cancelled(cancelled)
        self._emit(progress, "discovering", 0, 1)
        inputs = self.discover(project)
        self._emit(progress, "discovering", 1, 1)
        pdfs = [item for item in inputs if item.kind == DocumentKind.PDF]
        docxs = [item for item in inputs if item.kind == DocumentKind.DOCX]
        companions = [item for item in inputs if item.kind == DocumentKind.COMPANION]
        ignored = [item.path for item in inputs if item.kind == DocumentKind.OTHER]
        if not pdfs and not docxs:
            raise ValueError("No PDF or DOCX inputs were discovered for this project.")

        self._check_cancelled(cancelled)
        self._emit(progress, "validating", 0, 1)
        validations: dict[str, ValidationResult] = {}
        skipped: list[str] = []
        if pdfs:
            pdf_result = validate_part_set(
                inputs,
                DocumentKind.PDF,
                project.settings.expected_start,
                project.settings.expected_end,
                allow_encrypted_pdf=pdf_password_provider is not None,
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
        self._emit(progress, "validating", 1, 1)

        tracked = [item.path for item in pdfs + docxs + companions]
        before = snapshot_hashes(tracked)
        require_storage([item.path for item in pdfs + docxs], project.output_folder)
        base_name = render_project_basename(project)
        preserve_order = bool(project.selected_files)
        refs = [
            CompanionReference(item.part.number, item.path, item.sha256, item.size)
            for item in companions
        ]

        with OutputTransaction(project.output_folder) as transaction:
            staged_outputs: list[tuple[StagedOutput, DocumentKind]] = []
            if pdfs:
                pdf_entry = transaction.stage(
                    project.output_folder / f"{base_name}.pdf",
                    overwrite=project.settings.overwrite,
                )
                PdfMergeEngine().merge(
                    pdfs,
                    pdf_entry.staging_path,
                    project.settings.pdf,
                    overwrite=True,
                    preserve_order=preserve_order,
                    progress=(
                        lambda current, total, path: self._emit(
                            progress,
                            "merging-pdf",
                            current,
                            total,
                            path,
                        )
                    ),
                    cancelled=cancelled,
                    password_provider=pdf_password_provider,
                )
                staged_outputs.append((pdf_entry, DocumentKind.PDF))

            self._check_cancelled(cancelled)
            if docxs:
                docx_entry = transaction.stage(
                    project.output_folder / f"{base_name}.docx",
                    overwrite=project.settings.overwrite,
                )
                DocxMergeEngine().merge(
                    docxs,
                    docx_entry.staging_path,
                    project.settings.docx,
                    overwrite=True,
                    preserve_order=preserve_order,
                    progress=(
                        lambda current, total, path: self._emit(
                            progress,
                            "merging-docx",
                            current,
                            total,
                            path,
                        )
                    ),
                    cancelled=cancelled,
                )
                staged_outputs.append((docx_entry, DocumentKind.DOCX))

            self._check_cancelled(cancelled)
            self._emit(progress, "verifying", 0, 1)
            changed = verify_unchanged(before)
            if changed:
                raise RuntimeError(f"Original integrity guarantee failed: {changed}")
            outputs = [
                self._staged_artifact(entry, kind) for entry, kind in staged_outputs
            ]
            self._emit(progress, "verifying", 1, 1)

            self._check_cancelled(cancelled)
            self._emit(progress, "reporting", 0, 1)
            companion_md = self._stage_report(
                transaction,
                project.output_folder / "Companion_Code_Index.md",
            )
            companion_json = self._stage_report(
                transaction,
                project.output_folder / "Companion_Code_Index.json",
            )
            write_companion_index(
                refs,
                companion_md.staging_path,
                companion_json.staging_path,
            )

            report_md = self._stage_report(
                transaction,
                project.output_folder / f"{base_name}_Merge_Report.md",
            )
            report_html = self._stage_report(
                transaction,
                project.output_folder / f"{base_name}_Merge_Report.html",
            )
            write_project_report(
                validations,
                skipped,
                len(companions),
                report_md.staging_path,
                report_html.staging_path,
            )

            manifest = self._stage_report(
                transaction,
                project.output_folder / f"{base_name}_Merge_Manifest.json",
            )
            write_manifest(
                pdfs + docxs,
                outputs,
                ignored,
                project.warnings,
                manifest.staging_path,
                project.settings.profile_name,
            )
            if project.settings.checksum_generation:
                checksums = self._stage_report(
                    transaction,
                    project.output_folder / f"{base_name}_SHA256SUMS.txt",
                )
                write_checksums(
                    pdfs + docxs + companions,
                    outputs,
                    checksums.staging_path,
                )

            checklist = self._stage_report(
                transaction,
                project.output_folder / "Publishing_Checklist.md",
            )
            write_publishing_checklist(
                checklist.staging_path,
                f"Parts {project.settings.expected_start}–{project.settings.expected_end}",
            )
            self._emit(progress, "reporting", 1, 1)
            self._check_cancelled(cancelled)
            transaction.promote()

        return outputs

    def run_sql_preset(
        self,
        project: MergeProject,
        *,
        progress: ProgressCallback | None = None,
        cancelled: CancellationCallback | None = None,
        pdf_password_provider: PasswordProvider | None = None,
    ) -> list[OutputArtifact]:
        self._check_cancelled(cancelled)
        self._emit(progress, "discovering", 0, 1)
        inputs = self.discover(project)
        self._emit(progress, "discovering", 1, 1)
        pdfs = [item for item in inputs if item.kind == DocumentKind.PDF]
        docxs = [item for item in inputs if item.kind == DocumentKind.DOCX]
        companions = [item for item in inputs if item.kind == DocumentKind.COMPANION]
        ignored = [item.path for item in inputs if item.kind == DocumentKind.OTHER]

        self._check_cancelled(cancelled)
        self._emit(progress, "validating", 0, 1)
        pdf_result = validate_part_set(
            inputs,
            DocumentKind.PDF,
            project.settings.expected_start,
            project.settings.expected_end,
            allow_encrypted_pdf=pdf_password_provider is not None,
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
        self._emit(progress, "validating", 1, 1)

        tracked = [item.path for item in pdfs + docxs + companions]
        before = snapshot_hashes(tracked)
        require_storage([item.path for item in pdfs + docxs], project.output_folder)
        refs = [
            CompanionReference(item.part.number, item.path, item.sha256, item.size)
            for item in companions
        ]

        with OutputTransaction(project.output_folder) as transaction:
            pdf_entry = transaction.stage(
                project.output_folder / PDF_FILENAME,
                overwrite=project.settings.overwrite,
            )
            PdfMergeEngine().merge(
                pdfs,
                pdf_entry.staging_path,
                project.settings.pdf,
                overwrite=True,
                progress=(
                    lambda current, total, path: self._emit(
                        progress,
                        "merging-pdf",
                        current,
                        total,
                        path,
                    )
                ),
                cancelled=cancelled,
                password_provider=pdf_password_provider,
            )

            self._check_cancelled(cancelled)
            docx_entry = transaction.stage(
                project.output_folder / DOCX_FILENAME,
                overwrite=project.settings.overwrite,
            )
            DocxMergeEngine().merge(
                docxs,
                docx_entry.staging_path,
                project.settings.docx,
                overwrite=True,
                progress=(
                    lambda current, total, path: self._emit(
                        progress,
                        "merging-docx",
                        current,
                        total,
                        path,
                    )
                ),
                cancelled=cancelled,
            )

            self._check_cancelled(cancelled)
            self._emit(progress, "verifying", 0, 1)
            changed = verify_unchanged(before)
            if changed:
                raise RuntimeError(f"Original integrity guarantee failed: {changed}")
            outputs = [
                self._staged_artifact(pdf_entry, DocumentKind.PDF),
                self._staged_artifact(docx_entry, DocumentKind.DOCX),
            ]
            self._emit(progress, "verifying", 1, 1)

            self._check_cancelled(cancelled)
            self._emit(progress, "reporting", 0, 1)
            companion_md = self._stage_report(
                transaction,
                project.output_folder / "Companion_Code_Index.md",
            )
            companion_json = self._stage_report(
                transaction,
                project.output_folder / "Companion_Code_Index.json",
            )
            write_companion_index(
                refs,
                companion_md.staging_path,
                companion_json.staging_path,
            )

            report_md = self._stage_report(
                transaction,
                project.output_folder / REPORT_MD_FILENAME,
            )
            report_html = self._stage_report(
                transaction,
                project.output_folder / REPORT_HTML_FILENAME,
            )
            write_report(
                pdf_result,
                docx_result,
                len(companions),
                report_md.staging_path,
                report_html.staging_path,
            )

            manifest = self._stage_report(
                transaction,
                project.output_folder / MANIFEST_FILENAME,
            )
            write_manifest(
                pdfs + docxs,
                outputs,
                ignored,
                project.warnings,
                manifest.staging_path,
                "Master eBook",
            )
            if project.settings.checksum_generation:
                checksums = self._stage_report(
                    transaction,
                    project.output_folder / CHECKSUMS_FILENAME,
                )
                write_checksums(
                    pdfs + docxs + companions,
                    outputs,
                    checksums.staging_path,
                )

            checklist = self._stage_report(
                transaction,
                project.output_folder / "Publishing_Checklist.md",
            )
            write_publishing_checklist(checklist.staging_path)
            self._emit(progress, "reporting", 1, 1)
            self._check_cancelled(cancelled)
            transaction.promote()

        return outputs
