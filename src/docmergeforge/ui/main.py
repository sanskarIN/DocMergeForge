from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

from PySide6.QtCore import Qt, QUrl
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

from docmergeforge.app.service import MergeApplicationService
from docmergeforge.audit.document import audit_tree
from docmergeforge.core.models import DocumentKind, DocxSettings, MergeProject, PdfSettings
from docmergeforge.discovery.scanner import scan
from docmergeforge.docx.engine import DocxMergeEngine
from docmergeforge.pdf.engine import PdfMergeEngine
from docmergeforge.presets.sql_full_mastery import PRESET_NAME, create_sql_full_mastery_project
from docmergeforge.project.store import load_project, save_project
from docmergeforge.settings.config import AppSettings
from docmergeforge.ui.about_dialog import AboutDialog
from docmergeforge.ui.dialogs import (
    MergeProgressDialog,
    ProjectSetupDialog,
    RecentProjectsDialog,
    SettingsDialog,
    TextReportDialog,
)
from docmergeforge.ui.paths import recent_projects_path, settings_path
from docmergeforge.ui.recent import RecentProject, RecentProjectsStore
from docmergeforge.ui.theme import apply_theme
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


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.service = MergeApplicationService()
        self.app_settings = AppSettings.load(settings_path())
        self.recent = RecentProjectsStore(recent_projects_path())
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

    def _about(self) -> None:
        AboutDialog().exec()

    def _new_project(self, initial_source: Path | None = None) -> None:
        dialog = ProjectSetupDialog(initial_source)
        if dialog.exec() != int(dialog.DialogCode.Accepted):
            return
        project = dialog.project()
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
        save_project(project, path)
        self._remember_project(project, path)
        self._run_project(project)

    def _run_project(self, project: MergeProject) -> None:
        use_sql = project.name == PRESET_NAME

        def runner(progress: Any, cancelled: Any) -> object:
            dry_run = self.service.dry_run(project)
            if use_sql:
                if not dry_run.pdf.ready or not dry_run.docx.ready:
                    raise ValueError("SQL preset requires valid PDF and DOCX Parts 1–120.")
                return self.service.run_sql_preset(
                    project,
                    progress=progress,
                    cancelled=cancelled,
                )
            if not dry_run.ready_for_available_kinds:
                raise ValueError("Dry-run validation failed for the available document inputs.")
            return self.service.run_project(project, progress=progress, cancelled=cancelled)

        worker = MergeWorker(runner)
        progress_dialog = MergeProgressDialog(worker, "DocMergeForge Merge")
        result = progress_dialog.start()
        if result == int(progress_dialog.DialogCode.Accepted):
            outputs = worker.result or []
            paths = "\n".join(str(item.path) for item in outputs)
            QMessageBox.information(
                self,
                "Validated outputs created",
                paths or str(project.output_folder),
            )

    def _quick_merge(self, kind: DocumentKind) -> None:
        source = QFileDialog.getExistingDirectory(self, f"Select folder containing {kind.value.upper()}")
        if not source:
            return
        output, _ = QFileDialog.getSaveFileName(
            self,
            f"Save merged {kind.value.upper()}",
            str(Path(source) / f"DocMergeForge_Master.{kind.value}"),
            f"{kind.value.upper()} (*.{kind.value})",
        )
        if not output:
            return

        def runner(progress: Any, cancelled: Any) -> object:
            progress("discovering", 0, 1, None)
            items = [item for item in scan([Path(source)]) if item.kind == kind]
            progress("discovering", 1, 1, None)
            numbered = [item.part.number for item in items if item.part.number is not None]
            if not items or not numbered:
                raise ValueError("No numbered document inputs were found.")
            start, end = min(numbered), max(numbered)
            validation = validate_part_set(items, kind, start, end)
            if not validation.ready:
                raise ValueError(_parts_text(validation))
            if kind == DocumentKind.PDF:
                return PdfMergeEngine().merge(
                    items,
                    Path(output),
                    PdfSettings(),
                    progress=lambda current, total, path: progress(
                        "merging-pdf", current, total, path
                    ),
                    cancelled=cancelled,
                )
            return DocxMergeEngine().merge(
                items,
                Path(output),
                DocxSettings(),
                progress=lambda current, total, path: progress(
                    "merging-docx", current, total, path
                ),
                cancelled=cancelled,
            )

        worker = MergeWorker(runner)
        dialog = MergeProgressDialog(worker, f"Merge {kind.value.upper()}")
        if dialog.start() == int(dialog.DialogCode.Accepted):
            QMessageBox.information(self, "Validated output created", str(worker.result))

    def _sql_preset(self) -> None:
        source = QFileDialog.getExistingDirectory(self, "Select root folder containing Parts 1–120")
        if not source:
            return
        output = QFileDialog.getExistingDirectory(self, "Select output folder")
        if not output:
            return
        project = create_sql_full_mastery_project(Path(source), Path(output))
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
            return f"PDF\n{_parts_text(pdf)}\n\nDOCX\n{_parts_text(docx)}\n\nCompanion packages: {companions}"

        worker = MergeWorker(runner)
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
        dialog = MergeProgressDialog(worker, "Publication Audit")
        if dialog.start() != int(dialog.DialogCode.Accepted):
            return
        findings = worker.result or []
        if findings:
            text = "\n".join(
                f"[{item.severity}] {item.path}: {item.message}" for item in findings
            )
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
        items = scan([Path(source)])
        evidence: dict[str, object] = {}
        if pdf_output:
            pdfs = [item for item in items if item.kind == DocumentKind.PDF]
            evidence["pdf"] = asdict(compare_pdf(pdfs, Path(pdf_output)))
        if docx_output:
            docxs = [item for item in items if item.kind == DocumentKind.DOCX]
            evidence["docx"] = compare_docx(docxs, Path(docx_output)).to_dict()
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
        project = load_project(path)
        self._remember_project(project, path)
        self._run_project(project)

    def _recent_projects(self) -> None:
        projects = self.recent.remove_missing()
        if not projects:
            QMessageBox.information(self, "Recent Projects", "No saved recent projects were found.")
            return
        dialog = RecentProjectsDialog(projects)
        if dialog.exec() != int(dialog.DialogCode.Accepted):
            return
        selected = dialog.selected()
        if selected:
            self._run_project(load_project(selected.project_file))

    def _remember_project(self, project: MergeProject, project_file: Path) -> None:
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
        app = QApplication.instance()
        if isinstance(app, QApplication):
            apply_theme(app, self.app_settings.theme)
        self.statusBar().showMessage("Settings saved locally.", 5000)

    def _help(self) -> None:
        TextReportDialog(
            "DocMergeForge Help",
            "Local-first workflow:\n\n"
            "1. Select or drop the folder containing numbered Parts.\n"
            "2. Validate missing and duplicate Parts.\n"
            "3. Merge PDF and DOCX independently.\n"
            "4. Review generated reports, checksums, and manifests.\n\n"
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
    apply_theme(app, settings.theme)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
