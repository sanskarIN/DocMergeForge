from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import QDesktopServices, QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from docmergeforge.app.preflight import build_preflight, format_preflight
from docmergeforge.app.service import MergeApplicationService
from docmergeforge.audit.document import audit_tree
from docmergeforge.core.exceptions import DocMergeForgeError
from docmergeforge.core.models import (
    DocumentKind,
    DocxSettings,
    MergeProject,
    MergeState,
    PdfSettings,
)
from docmergeforge.diagnostics.logging import configure_logging, get_logger
from docmergeforge.discovery.scanner import scan
from docmergeforge.docx.engine import DocxMergeEngine
from docmergeforge.pdf.engine import PdfMergeEngine
from docmergeforge.presets.sql_full_mastery import PRESET_NAME
from docmergeforge.profiles.catalog import MergeProfile, apply_profile
from docmergeforge.project.recovery import RecoveryStore
from docmergeforge.project.store import (
    load_project,
    load_project_snapshot,
    save_project,
    save_project_if_revision,
)
from docmergeforge.settings.config import AppSettings
from docmergeforge.ui.about_dialog import AboutDialog
from docmergeforge.ui.dialogs import (
    MergeProgressDialog,
    ProjectSetupDialog,
    RecentProjectsDialog,
    SettingsDialog,
    TextReportDialog,
)
from docmergeforge.ui.dry_run_dialog import DryRunDialog
from docmergeforge.ui.first_run import FirstRunDialog
from docmergeforge.ui.order_dialog import OrderEditorDialog
from docmergeforge.ui.paths import log_path, recent_projects_path, recovery_dir, settings_path
from docmergeforge.ui.pdf_passwords import collect_pdf_passwords
from docmergeforge.ui.recent import RecentProject, RecentProjectsStore
from docmergeforge.ui.sql_wizard import SQLPresetWizard
from docmergeforge.ui.support_dialog import SupportDialog
from docmergeforge.ui.theme import apply_text_scale, apply_theme
from docmergeforge.ui.workers import MergeWorker
from docmergeforge.validation.compare import compare_docx, compare_pdf
from docmergeforge.validation.service import validate_part_set


def _parts_text(result: Any) -> str:
    return (
        f"Expected: {len(result.expected_parts)}\n"
        f"Found: {len(result.found_parts)}\n"
        f"Missing: {result.missing_parts or 'None'}\n"
        f"Duplicates: {result.duplicate_parts or 'None'}\n"
        f"Ready: {'YES' if result.ready else 'NO'}"
    )


_STATE_BY_STAGE = {
    "discovering": MergeState.DISCOVERING,
    "validating": MergeState.VALIDATING,
    "merging-pdf": MergeState.MERGING,
    "merging-docx": MergeState.MERGING,
    "verifying": MergeState.VERIFYING,
    "reporting": MergeState.REPORTING,
}


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.service = MergeApplicationService()
        self.app_settings = AppSettings.load(settings_path())
        self.recent = RecentProjectsStore(recent_projects_path())
        self.recovery = RecoveryStore(recovery_dir())
        self.recent_errors: list[str] = []
        self.logger = get_logger()
        self.setWindowTitle("DocMergeForge")
        self.resize(1080, 720)
        self.setMinimumSize(820, 560)
        self.setAcceptDrops(True)
        root = QWidget()
        outer = QVBoxLayout(root)

        heading = QLabel(
            "<h1>DocMergeForge</h1>"
            "<p>Discover correctly. Order correctly. Merge safely. Validate everything.</p>"
        )
        heading.setAccessibleName("DocMergeForge heading")
        heading.setTextFormat(Qt.TextFormat.RichText)
        outer.addWidget(heading)

        privacy = QLabel(
            "Local-first • Originals are never overwritten • PDF and DOCX stay separate • "
            "Companion code is never merged"
        )
        privacy.setWordWrap(True)
        outer.addWidget(privacy)

        grid = QGridLayout()
        actions = [
            ("New Merge Project", self._new_project),
            ("Merge PDFs", lambda: self._quick_merge(DocumentKind.PDF)),
            ("Merge DOCX", lambda: self._quick_merge(DocumentKind.DOCX)),
            ("SQL Full Mastery 120-Part Preset", self._sql_preset),
            ("Validate Files", self._validate_files),
            ("Publication Audit", self._publication_audit),
            ("Compare Output with Inputs", self._compare_outputs),
            ("Resume Project", self._resume_project),
            ("Recent Projects", self._recent_projects),
            ("Settings", self._settings),
            ("Help", self._help),
            ("Support", self._support),
            ("About", self._about),
        ]
        for index, (label, callback) in enumerate(actions):
            button = QPushButton(label)
            button.setAccessibleName(label)
            button.setMinimumHeight(58)
            button.clicked.connect(callback)
            grid.addWidget(button, index // 3, index % 3)
        outer.addLayout(grid)

        support_row = QHBoxLayout()
        support_row.addWidget(QLabel("<b>Made by the Sanskar</b>"))
        support_row.addStretch(1)
        bmc = QPushButton("☕ Buy Me a Coffee")
        bmc.setAccessibleName("Buy Me a Coffee support link")
        bmc.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl("https://buymeacoffee.com/sanskarIN"))
        )
        support_row.addWidget(bmc)
        outer.addLayout(support_row)

        self.setCentralWidget(root)
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Drop a project folder here or choose an action.")
        self.logger.info("desktop application initialized")

    def show_startup_dialogs(self) -> None:
        if not self.app_settings.first_run_completed:
            FirstRunDialog().exec()
            self.app_settings.first_run_completed = True
            self.app_settings.save(settings_path())
        if not self.app_settings.crash_recovery:
            return
        try:
            project = self.recovery.recover()
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            self._record_error(str(exc))
            self.recovery.clear()
            return
        if project is None:
            return
        checkpoint = project.last_successful_checkpoint or "saved checkpoint"
        answer = QMessageBox.question(
            self,
            "Recover interrupted merge?",
            f"An interrupted project was found at {checkpoint}. Resume it now?",
        )
        if answer == QMessageBox.StandardButton.Yes:
            self.logger.info("recovering project from checkpoint=%s", checkpoint)
            self._run_project(project)
        else:
            self.recovery.clear()

    def _record_error(self, message: str) -> None:
        sanitized = message.strip()
        if not sanitized:
            return
        self.recent_errors.append(sanitized[:4000])
        self.recent_errors = self.recent_errors[-20:]
        self.logger.error("%s", sanitized)

    def _about(self) -> None:
        AboutDialog().exec()

    def _support(self) -> None:
        SupportDialog(recent_errors=self.recent_errors).exec()

    def _apply_project_defaults(self, project: MergeProject) -> None:
        if project.name == PRESET_NAME:
            return
        try:
            profile = MergeProfile(self.app_settings.merge_profile)
        except ValueError:
            profile = MergeProfile.CUSTOM
        project.settings = apply_profile(project.settings, profile)
        project.settings.checksum_generation = self.app_settings.checksum_generation
        project.settings.automatic_validation = self.app_settings.automatic_validation
        project.settings.filename_template = (
            self.app_settings.filename_template or "{series}_Master"
        )
        project.settings.pdf.optimization = self.app_settings.pdf_optimization
        project.settings.docx.fidelity_mode = self.app_settings.docx_fidelity_mode

    def _checkpoint_project(self, project: MergeProject, name: str) -> bool:
        if not self.app_settings.crash_recovery:
            return True
        try:
            self.recovery.checkpoint(project, name)
        except (OSError, ValueError) as exc:
            self._record_error(str(exc))
            QMessageBox.critical(self, "Recovery checkpoint failed", str(exc))
            return False
        return True

    def _confirm_project_order(self, project: MergeProject, *, checkpoint: bool = True) -> bool:
        try:
            discovered = self.service.discover(project)
        except (OSError, ValueError) as exc:
            QMessageBox.critical(self, "Discovery failed", str(exc))
            self._record_error(str(exc))
            return False
        documents = [
            item for item in discovered if item.kind in {DocumentKind.PDF, DocumentKind.DOCX}
        ]
        if not documents:
            QMessageBox.warning(
                self,
                "No documents found",
                "No PDF or DOCX documents are available for this project.",
            )
            return False
        order_dialog = OrderEditorDialog(
            documents,
            project.settings.expected_start,
            project.settings.expected_end,
            allow_manual_order=project.name != PRESET_NAME,
        )
        if order_dialog.exec() != int(order_dialog.DialogCode.Accepted):
            return False
        project.selected_files = order_dialog.ordered_paths()
        if checkpoint and not self._checkpoint_project(project, "ordering"):
            return False
        return True

    def _new_project(self, initial_source: Path | None = None) -> None:
        dialog = ProjectSetupDialog(initial_source)
        if self.app_settings.default_output_folder:
            dialog.output.set_path(Path(self.app_settings.default_output_folder))
        if dialog.exec() != int(dialog.DialogCode.Accepted):
            return
        project = dialog.project()
        self._apply_project_defaults(project)
        if not self._confirm_project_order(project):
            return
        suggested = project.output_folder / "docmergeforge-project.json"
        project_file, _ = QFileDialog.getSaveFileName(
            self,
            "Save Merge Project",
            str(suggested),
            "DocMergeForge Project (*.json)",
        )
        if not project_file:
            return
        path = Path(project_file)
        try:
            save_project(project, path)
        except (OSError, ValueError) as exc:
            self._record_error(str(exc))
            QMessageBox.critical(self, "Project could not be saved", str(exc))
            return
        self._remember_project(project, path)
        self._run_project(project)

    def _project_passwords(self, project: MergeProject) -> dict[Path, str] | None:
        try:
            inputs = self.service.discover(project)
        except (OSError, ValueError) as exc:
            self._record_error(str(exc))
            QMessageBox.critical(self, "Discovery failed", str(exc))
            return None
        return collect_pdf_passwords(self, inputs)

    def _run_project(self, project: MergeProject) -> None:
        use_sql = project.name == PRESET_NAME
        passwords = self._project_passwords(project)
        if passwords is None:
            return
        try:
            preflight = build_preflight(
                project,
                allow_encrypted_pdf=bool(passwords),
            )
        except (DocMergeForgeError, OSError, ValueError) as exc:
            passwords.clear()
            self._record_error(str(exc))
            QMessageBox.critical(self, "Dry run failed", str(exc))
            return
        ready = preflight.result.storage.sufficient
        if use_sql:
            ready = ready and preflight.result.pdf.ready and preflight.result.docx.ready
        else:
            ready = ready and preflight.result.ready_for_available_kinds
        dry_run_dialog = DryRunDialog(format_preflight(preflight), ready)
        if dry_run_dialog.exec() != int(dry_run_dialog.DialogCode.Accepted):
            passwords.clear()
            return

        def password_provider(path: Path) -> str | None:
            return passwords.get(path)

        def runner(progress: Any, cancelled: Any) -> object:
            def checkpointing_progress(
                stage: str,
                current: int,
                total: int,
                path: Path | None,
            ) -> None:
                progress(stage, current, total, path)
                self.logger.info(
                    "merge stage=%s current=%s total=%s file=%s",
                    stage,
                    current,
                    total,
                    path or "",
                )
                if not self.app_settings.crash_recovery or current != total:
                    return
                state = _STATE_BY_STAGE.get(stage)
                if state is not None:
                    project.state = state
                self.recovery.checkpoint(project, stage)

            dry_run = self.service.dry_run(
                project,
                allow_encrypted_pdf=bool(passwords),
            )
            if use_sql:
                if not dry_run.pdf.ready or not dry_run.docx.ready:
                    raise ValueError("SQL preset requires valid PDF and DOCX Parts 1–120.")
                return self.service.run_sql_preset(
                    project,
                    progress=checkpointing_progress,
                    cancelled=cancelled,
                    pdf_password_provider=password_provider,
                )
            if not dry_run.ready_for_available_kinds:
                raise ValueError("Dry-run validation failed for the available document inputs.")
            return self.service.run_project(
                project,
                progress=checkpointing_progress,
                cancelled=cancelled,
                pdf_password_provider=password_provider,
            )

        worker = MergeWorker(runner)
        worker.failed.connect(self._record_error)
        title = "SQL Full Mastery — Steps 7–10" if use_sql else "DocMergeForge Merge"
        progress_dialog = MergeProgressDialog(worker, title)
        try:
            result = progress_dialog.start()
        finally:
            passwords.clear()
        if result == int(progress_dialog.DialogCode.Accepted):
            project.state = MergeState.SUCCEEDED
            self.recovery.clear()
            outputs = worker.result or []
            paths = "\n".join(str(item.path) for item in outputs)
            self.logger.info("merge completed after validation outputs=%s", paths)
            summary_title = "Step 11 — Final Summary" if use_sql else "Validated outputs created"
            QMessageBox.information(
                self,
                summary_title,
                paths or str(project.output_folder),
            )

    def _quick_merge(self, kind: DocumentKind) -> None:
        source = QFileDialog.getExistingDirectory(
            self,
            f"Select folder containing {kind.value.upper()}",
        )
        if not source:
            return
        try:
            items = [item for item in scan([Path(source)]) if item.kind == kind]
        except OSError as exc:
            self._record_error(str(exc))
            QMessageBox.critical(self, "Discovery failed", str(exc))
            return
        passwords = collect_pdf_passwords(self, items) if kind == DocumentKind.PDF else {}
        if passwords is None:
            return
        output, _ = QFileDialog.getSaveFileName(
            self,
            f"Save merged {kind.value.upper()}",
            str(Path(source) / f"DocMergeForge_Master.{kind.value}"),
            f"{kind.value.upper()} (*.{kind.value})",
        )
        if not output:
            passwords.clear()
            return

        def runner(progress: Any, cancelled: Any) -> object:
            progress("discovering", 1, 1, None)
            numbered = [item.part.number for item in items if item.part.number is not None]
            if not items or not numbered:
                raise ValueError("No numbered document inputs were found.")
            start, end = min(numbered), max(numbered)
            validation = validate_part_set(
                items,
                kind,
                start,
                end,
                allow_encrypted_pdf=bool(passwords),
            )
            if not validation.ready:
                raise ValueError(_parts_text(validation))
            if kind == DocumentKind.PDF:
                return PdfMergeEngine().merge(
                    items,
                    Path(output),
                    PdfSettings(optimization=self.app_settings.pdf_optimization),
                    progress=lambda current, total, path: progress(
                        "merging-pdf", current, total, path
                    ),
                    cancelled=cancelled,
                    password_provider=lambda path: passwords.get(path),
                )
            return DocxMergeEngine().merge(
                items,
                Path(output),
                DocxSettings(fidelity_mode=self.app_settings.docx_fidelity_mode),
                progress=lambda current, total, path: progress(
                    "merging-docx", current, total, path
                ),
                cancelled=cancelled,
            )

        worker = MergeWorker(runner)
        worker.failed.connect(self._record_error)
        dialog = MergeProgressDialog(worker, f"Merge {kind.value.upper()}")
        try:
            result = dialog.start()
        finally:
            passwords.clear()
        if result == int(dialog.DialogCode.Accepted):
            QMessageBox.information(self, "Validated output created", str(worker.result))

    def _sql_preset(self) -> None:
        wizard = SQLPresetWizard()
        if wizard.exec() != int(wizard.DialogCode.Accepted):
            return
        project = wizard.project()
        if not self._checkpoint_project(project, "sql-preflight"):
            return
        self._run_project(project)

    def _validate_files(self) -> None:
        source = QFileDialog.getExistingDirectory(self, "Select folder to validate")
        if not source:
            return

        def runner(progress: Any, _cancelled: Any) -> object:
            progress("discovering", 0, 1, None)
            items = scan([Path(source)])
            progress("discovering", 1, 1, None)
            pdf = validate_part_set(items, DocumentKind.PDF, 1, 120)
            docx = validate_part_set(items, DocumentKind.DOCX, 1, 120)
            companions = sum(item.kind == DocumentKind.COMPANION for item in items)
            return (
                f"PDF\n{_parts_text(pdf)}\n\nDOCX\n{_parts_text(docx)}\n\n"
                f"Companion packages: {companions}"
            )

        worker = MergeWorker(runner)
        worker.failed.connect(self._record_error)
        dialog = MergeProgressDialog(worker, "Validate Files")
        if dialog.start() == int(dialog.DialogCode.Accepted):
            TextReportDialog("Validation Results", str(worker.result)).exec()

    def _publication_audit(self) -> None:
        source = QFileDialog.getExistingDirectory(self, "Select folder for publication audit")
        if not source:
            return

        def runner(progress: Any, cancelled: Any) -> object:
            progress("auditing", 0, 1, None)
            if cancelled():
                return []
            findings = audit_tree(Path(source))
            progress("auditing", 1, 1, None)
            return findings

        worker = MergeWorker(runner)
        worker.failed.connect(self._record_error)
        dialog = MergeProgressDialog(worker, "Publication Audit")
        if dialog.start() != int(dialog.DialogCode.Accepted):
            return
        findings = worker.result or []
        if findings:
            text = "\n".join(f"[{item.severity}] {item.path}: {item.message}" for item in findings)
        else:
            text = "No configured publication-audit findings were detected."
        TextReportDialog("Publication Audit", text).exec()

    def _compare_outputs(self) -> None:
        source = QFileDialog.getExistingDirectory(self, "Select source folder")
        if not source:
            return
        pdf_output, _ = QFileDialog.getOpenFileName(
            self,
            "Select master PDF (optional)",
            "",
            "PDF (*.pdf)",
        )
        docx_output, _ = QFileDialog.getOpenFileName(
            self,
            "Select master DOCX (optional)",
            "",
            "DOCX (*.docx)",
        )
        if not pdf_output and not docx_output:
            return
        try:
            items = scan([Path(source)])
            evidence: dict[str, object] = {}
            if pdf_output:
                pdfs = [item for item in items if item.kind == DocumentKind.PDF]
                evidence["pdf"] = asdict(compare_pdf(pdfs, Path(pdf_output)))
            if docx_output:
                docxs = [item for item in items if item.kind == DocumentKind.DOCX]
                evidence["docx"] = compare_docx(docxs, Path(docx_output)).to_dict()
        except (OSError, ValueError) as exc:
            self._record_error(str(exc))
            QMessageBox.critical(self, "Comparison failed", str(exc))
            return
        TextReportDialog(
            "Output Comparison",
            json.dumps(evidence, indent=2, default=str),
        ).exec()

    def _resume_project(self) -> None:
        project_file, _ = QFileDialog.getOpenFileName(
            self,
            "Open DocMergeForge Project",
            "",
            "DocMergeForge Project (*.json)",
        )
        if not project_file:
            return
        path = Path(project_file)
        try:
            project, revision = load_project_snapshot(path)
        except (OSError, ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            self._record_error(str(exc))
            QMessageBox.critical(self, "Project could not be opened", str(exc))
            return
        if not self._confirm_project_order(project, checkpoint=False):
            return
        try:
            save_project_if_revision(project, path, revision)
        except (OSError, ValueError) as exc:
            self._record_error(str(exc))
            QMessageBox.critical(self, "Project changed on disk", str(exc))
            return
        if not self._checkpoint_project(project, "ordering"):
            return
        self._remember_project(project, path)
        self._run_project(project)

    def _recent_projects(self) -> None:
        if not self.app_settings.recent_project_history:
            QMessageBox.information(
                self,
                "Recent Projects",
                "Recent project history is disabled in Settings.",
            )
            return
        projects = self.recent.remove_missing()
        if not projects:
            QMessageBox.information(self, "Recent Projects", "No saved recent projects were found.")
            return
        dialog = RecentProjectsDialog(projects)
        if dialog.exec() != int(dialog.DialogCode.Accepted):
            return
        selected = dialog.selected()
        if selected is None:
            return
        try:
            project = load_project(selected.project_file)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            self._record_error(str(exc))
            QMessageBox.critical(self, "Recent project could not be opened", str(exc))
            return
        self._run_project(project)

    def _remember_project(self, project: MergeProject, project_file: Path) -> None:
        if not self.app_settings.recent_project_history:
            return
        source = project.source_folders[0] if project.source_folders else Path()
        self.recent.add(
            RecentProject(
                project.name,
                project_file,
                source,
                project.output_folder,
            )
        )

    def _settings(self) -> None:
        dialog = SettingsDialog(self.app_settings)
        if dialog.exec() != int(dialog.DialogCode.Accepted):
            return
        self.app_settings = dialog.settings()
        self.app_settings.save(settings_path())
        self.logger = configure_logging(log_path(), self.app_settings.logging_level)
        app = QApplication.instance()
        if isinstance(app, QApplication):
            apply_theme(app, self.app_settings.theme)
            apply_text_scale(app, self.app_settings.text_scale_percent)
        self.statusBar().showMessage("Settings saved locally.", 5000)

    def _help(self) -> None:
        TextReportDialog(
            "DocMergeForge Help",
            "Local-first workflow:\n\n"
            "1. Select or drop the folder containing numbered Parts.\n"
            "2. Confirm the final document order.\n"
            "3. Review the dry-run evidence.\n"
            "4. Validate missing and duplicate Parts.\n"
            "5. Merge PDF and DOCX independently.\n"
            "6. Review generated reports, checksums, and manifests.\n\n"
            "Original documents are never overwritten. Companion code remains separate.\n\n"
            "Support: supportramsandesh@gmail.com\n"
            "Repository: https://github.com/sanskarIN/DocMergeForge\n"
            "Buy Me a Coffee: https://buymeacoffee.com/sanskarIN",
        ).exec()

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        urls = event.mimeData().urls()
        if not urls:
            return
        path = Path(urls[0].toLocalFile())
        initial = path if path.is_dir() else path.parent
        self._new_project(initial)
        event.acceptProposedAction()


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("DocMergeForge")
    app.setOrganizationName("Sanskar")
    settings = AppSettings.load(settings_path())
    configure_logging(log_path(), settings.logging_level)
    apply_theme(app, settings.theme)
    apply_text_scale(app, settings.text_scale_percent)
    window = MainWindow()
    window.show()
    QTimer.singleShot(0, window.show_startup_dialogs)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
