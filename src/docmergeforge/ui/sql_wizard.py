from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWizard,
    QWizardPage,
    QWidget,
)

from docmergeforge.core.models import DocumentKind, InputDocument, MergeProject
from docmergeforge.discovery.scanner import scan
from docmergeforge.presets.sql_full_mastery import (
    CHECKSUMS_FILENAME,
    DOCX_FILENAME,
    MANIFEST_FILENAME,
    PDF_FILENAME,
    PRESET_NAME,
    REPORT_HTML_FILENAME,
    REPORT_MD_FILENAME,
    create_sql_full_mastery_project,
)
from docmergeforge.validation.service import validate_part_set


class _DirectoryField(QWidget):
    def __init__(self, title: str) -> None:
        super().__init__()
        self.title = title
        layout = QFormLayout(self)
        self.edit = QLineEdit()
        button = QPushButton("Browse…")
        button.clicked.connect(self._browse)
        layout.addRow(self.edit, button)

    def _browse(self) -> None:
        selected = QFileDialog.getExistingDirectory(self, self.title)
        if selected:
            self.edit.setText(selected)

    def path(self) -> Path:
        return Path(self.edit.text().strip()).expanduser()


class _IntroPage(QWizardPage):
    def __init__(self) -> None:
        super().__init__()
        self.setTitle("SQL Full Mastery — 120-Part Master Edition")
        layout = QVBoxLayout(self)
        text = QLabel(
            "This guided preset validates Parts 1–120, merges PDF and DOCX independently, "
            "keeps companion code separate, creates publication metadata, and writes integrity "
            "reports. Original source documents are never intentionally overwritten."
        )
        text.setWordWrap(True)
        layout.addWidget(text)


class _FoldersPage(QWizardPage):
    def __init__(self) -> None:
        super().__init__()
        self.setTitle("Choose source and output folders")
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.source = _DirectoryField("Select SQL Full Mastery source folder")
        self.output = _DirectoryField("Select SQL Full Mastery output folder")
        form.addRow("Source folder", self.source)
        form.addRow("Output folder", self.output)
        layout.addLayout(form)
        note = QLabel(
            "The source folder may contain PDF, DOCX, companion ZIP/project files, and unrelated "
            "files. Only PDF and DOCX documents enter the merge pipelines."
        )
        note.setWordWrap(True)
        layout.addWidget(note)

    def validatePage(self) -> bool:
        source = self.source.path()
        output = self.output.path()
        if not source.exists() or not source.is_dir():
            QMessageBox.warning(self, "Source folder required", "Choose an existing source folder.")
            return False
        if not str(self.output.edit.text()).strip():
            QMessageBox.warning(self, "Output folder required", "Choose an output folder.")
            return False
        try:
            output.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            QMessageBox.warning(self, "Output folder unavailable", str(exc))
            return False
        return True


class _DiscoveryPage(QWizardPage):
    def __init__(self, owner: SQLPresetWizard) -> None:
        super().__init__()
        self.owner = owner
        self.setTitle("Discover and validate Parts 1–120")
        layout = QVBoxLayout(self)
        self.summary = QPlainTextEdit()
        self.summary.setReadOnly(True)
        layout.addWidget(self.summary)

    def initializePage(self) -> None:
        self.owner.refresh_discovery()
        self.summary.setPlainText(self.owner.discovery_summary())

    def validatePage(self) -> bool:
        if self.owner.discovery_error:
            QMessageBox.warning(self, "Discovery failed", self.owner.discovery_error)
            return False
        if not self.owner.preset_ready:
            QMessageBox.warning(
                self,
                "Parts require attention",
                "Both PDF and DOCX must contain exactly one valid copy of Parts 1–120 before "
                "this preset can continue.",
            )
            return False
        return True


class _OrderPage(QWizardPage):
    def __init__(self, owner: SQLPresetWizard) -> None:
        super().__init__()
        self.owner = owner
        self.setTitle("Confirm locked natural order")
        layout = QVBoxLayout(self)
        note = QLabel(
            "The preset locks numeric order at Part 1 → Part 120. PDF and DOCX stay in separate "
            "pipelines. This preview cannot be manually reordered."
        )
        note.setWordWrap(True)
        layout.addWidget(note)
        self.list = QListWidget()
        self.list.setAccessibleName("SQL preset locked file order")
        layout.addWidget(self.list)

    def initializePage(self) -> None:
        self.list.clear()
        for item in self.owner.ordered_documents:
            part = item.part.number if item.part.number is not None else "?"
            self.list.addItem(f"Part {part:>3}  [{item.kind.value.upper()}]  {item.path.name}")


class _PlanPage(QWizardPage):
    def __init__(self, owner: SQLPresetWizard) -> None:
        super().__init__()
        self.owner = owner
        self.setTitle("Review merge and publication plan")
        layout = QVBoxLayout(self)
        self.plan = QPlainTextEdit()
        self.plan.setReadOnly(True)
        layout.addWidget(self.plan)

    def initializePage(self) -> None:
        self.plan.setPlainText(self.owner.plan_summary())


class _RunPage(QWizardPage):
    def __init__(self) -> None:
        super().__init__()
        self.setTitle("Ready to run")
        layout = QVBoxLayout(self)
        text = QLabel(
            "Select Finish to begin the validated merge. Progress, safe cancellation, recovery "
            "checkpoints, source-integrity verification, and final reports are handled by the "
            "main DocMergeForge workflow."
        )
        text.setWordWrap(True)
        layout.addWidget(text)


class SQLPresetWizard(QWizard):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(PRESET_NAME)
        self.resize(860, 650)
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        self.discovery_items: list[InputDocument] = []
        self.ordered_documents: list[InputDocument] = []
        self.discovery_error = ""
        self.preset_ready = False

        self.intro_page = _IntroPage()
        self.folders_page = _FoldersPage()
        self.discovery_page = _DiscoveryPage(self)
        self.order_page = _OrderPage(self)
        self.plan_page = _PlanPage(self)
        self.run_page = _RunPage()

        self.addPage(self.intro_page)
        self.addPage(self.folders_page)
        self.addPage(self.discovery_page)
        self.addPage(self.order_page)
        self.addPage(self.plan_page)
        self.addPage(self.run_page)

    def refresh_discovery(self) -> None:
        self.discovery_items = []
        self.ordered_documents = []
        self.discovery_error = ""
        self.preset_ready = False
        try:
            self.discovery_items = scan([self.folders_page.source.path()], recursive=True)
        except OSError as exc:
            self.discovery_error = str(exc)
            return

        pdf = validate_part_set(self.discovery_items, DocumentKind.PDF, 1, 120)
        docx = validate_part_set(self.discovery_items, DocumentKind.DOCX, 1, 120)
        self.preset_ready = pdf.ready and docx.ready
        mergeable = [
            item
            for item in self.discovery_items
            if item.kind in {DocumentKind.PDF, DocumentKind.DOCX}
        ]
        self.ordered_documents = sorted(
            mergeable,
            key=lambda item: (
                item.part.number is None,
                item.part.number or 0,
                0 if item.kind == DocumentKind.PDF else 1,
                item.path.name.casefold(),
            ),
        )

    def discovery_summary(self) -> str:
        if self.discovery_error:
            return f"Discovery error:\n{self.discovery_error}"
        pdf = validate_part_set(self.discovery_items, DocumentKind.PDF, 1, 120)
        docx = validate_part_set(self.discovery_items, DocumentKind.DOCX, 1, 120)
        companions = sum(item.kind == DocumentKind.COMPANION for item in self.discovery_items)
        ignored = sum(item.kind == DocumentKind.OTHER for item in self.discovery_items)

        def describe(label: str, result: object) -> str:
            validation = result
            missing = getattr(validation, "missing_parts")
            duplicates = getattr(validation, "duplicate_parts")
            found = getattr(validation, "found_parts")
            return (
                f"{label}: found {len(found)}/120 | missing {missing or 'none'} | "
                f"duplicates {duplicates or 'none'}"
            )

        return "\n".join(
            [
                describe("PDF", pdf),
                describe("DOCX", docx),
                f"Companion packages indexed only: {companions}",
                f"Other files ignored by merge engines: {ignored}",
                f"Preset ready: {'YES' if self.preset_ready else 'NO'}",
            ]
        )

    def plan_summary(self) -> str:
        output = self.folders_page.output.path()
        return "\n".join(
            [
                "SQL Full Mastery publication plan",
                "",
                "PDF pipeline:",
                f"  {output / PDF_FILENAME}",
                "  Title page, visible TOC, part bookmarks, page numbers, metadata",
                "",
                "DOCX pipeline:",
                f"  {output / DOCX_FILENAME}",
                "  Part headings, TOC field, continuous numbering, preserved sections",
                "",
                "Integrity and reports:",
                f"  {output / MANIFEST_FILENAME}",
                f"  {output / REPORT_MD_FILENAME}",
                f"  {output / REPORT_HTML_FILENAME}",
                f"  {output / CHECKSUMS_FILENAME}",
                "  Companion_Code_Index.md / .json",
                "  Publishing_Checklist.md",
                "",
                "Companion code is indexed only and is never merged into either book.",
            ]
        )

    def project(self) -> MergeProject:
        project = create_sql_full_mastery_project(
            self.folders_page.source.path(),
            self.folders_page.output.path(),
        )
        project.selected_files = [item.path for item in self.ordered_documents]
        return project
