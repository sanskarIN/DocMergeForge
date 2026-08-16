from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QCheckBox,
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

from docmergeforge.audit.document import audit_tree
from docmergeforge.core.models import (
    DocumentKind,
    InputDocument,
    MergeProject,
    ValidationResult,
)
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
        self.setTitle("Step 1 — Select Root Folder")
        layout = QVBoxLayout(self)
        text = QLabel(
            "SQL Full Mastery — 120-Part Master Edition is a local-first guided workflow. "
            "It validates Parts 1–120, merges PDF and DOCX independently, keeps companion code "
            "separate, and verifies source integrity before final reporting."
        )
        text.setWordWrap(True)
        layout.addWidget(text)


class _FoldersPage(QWizardPage):
    def __init__(self) -> None:
        super().__init__()
        self.setTitle("Step 1 — Select Root Folder and Output")
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.source = _DirectoryField("Select SQL Full Mastery source folder")
        self.output = _DirectoryField("Select SQL Full Mastery output folder")
        form.addRow("Root folder", self.source)
        form.addRow("Output folder", self.output)
        layout.addLayout(form)
        note = QLabel(
            "The root folder may contain PDF, DOCX, companion ZIP/project files, and unrelated "
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
        if not self.output.edit.text().strip():
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
        self.setTitle("Steps 2–3 — Discover and Validate Parts 1–120")
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


class _CodePolicyPage(QWizardPage):
    def __init__(self) -> None:
        super().__init__()
        self.setTitle("Step 4 — Confirm Companion Code Policy")
        layout = QVBoxLayout(self)
        message = QLabel(
            "Companion code remains separate and unchanged. DocMergeForge may hash, index, or "
            "copy package files when explicitly requested, but this preset never extracts, "
            "merges, refactors, rewrites, or combines source-code projects."
        )
        message.setWordWrap(True)
        layout.addWidget(message)
        self.confirm = QCheckBox(
            "I understand that companion code packages remain separate from both master books."
        )
        self.confirm.toggled.connect(self.completeChanged.emit)
        layout.addWidget(self.confirm)

    def isComplete(self) -> bool:
        return self.confirm.isChecked()


class _OrderPage(QWizardPage):
    def __init__(self, owner: SQLPresetWizard) -> None:
        super().__init__()
        self.owner = owner
        self.setTitle("Step 5 — Preview Locked Natural Order")
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


class _AuditPage(QWizardPage):
    def __init__(self, owner: SQLPresetWizard) -> None:
        super().__init__()
        self.owner = owner
        self.setTitle("Step 6 — Optional Publication Audit")
        layout = QVBoxLayout(self)
        self.enabled = QCheckBox("Run publication audit before merge")
        self.enabled.setChecked(True)
        layout.addWidget(self.enabled)
        self.result = QPlainTextEdit()
        self.result.setReadOnly(True)
        self.result.setPlainText(
            "The audit is optional and reports manuscript consistency findings separately from "
            "the merge. It never rewrites manuscript content."
        )
        layout.addWidget(self.result)
        run_button = QPushButton("Run Audit Now")
        run_button.clicked.connect(self._run_audit)
        layout.addWidget(run_button)

    def _run_audit(self) -> None:
        if not self.enabled.isChecked():
            self.owner.audit_completed = False
            self.owner.audit_summary = "Publication audit skipped by user."
            self.result.setPlainText(self.owner.audit_summary)
            return
        try:
            findings = audit_tree(self.owner.folders_page.source.path())
        except (OSError, ValueError) as exc:
            self.owner.audit_completed = False
            self.owner.audit_summary = f"Publication audit could not complete: {exc}"
            self.result.setPlainText(self.owner.audit_summary)
            return
        self.owner.audit_completed = True
        if findings:
            lines = [
                f"[{finding.severity}] {finding.path.name}: {finding.message}"
                for finding in findings
            ]
            self.owner.audit_summary = "\n".join(lines)
        else:
            self.owner.audit_summary = "No configured publication-audit findings were detected."
        self.result.setPlainText(self.owner.audit_summary)

    def validatePage(self) -> bool:
        if self.enabled.isChecked() and not self.owner.audit_completed:
            self._run_audit()
        return True


class _PlanPage(QWizardPage):
    def __init__(self, owner: SQLPresetWizard) -> None:
        super().__init__()
        self.owner = owner
        self.setTitle("Steps 7–10 — Review Merge, Validation, and Reports")
        layout = QVBoxLayout(self)
        self.plan = QPlainTextEdit()
        self.plan.setReadOnly(True)
        layout.addWidget(self.plan)

    def initializePage(self) -> None:
        self.plan.setPlainText(self.owner.plan_summary())


class _RunPage(QWizardPage):
    def __init__(self) -> None:
        super().__init__()
        self.setTitle("Step 11 — Begin and Continue to Final Summary")
        layout = QVBoxLayout(self)
        text = QLabel(
            "Select Finish to begin Steps 7–10 in the background worker: merge PDF, merge DOCX, "
            "validate outputs, and generate reports. The following final summary displays exact "
            "validated output paths. Safe cancellation and recovery checkpoints stay enabled."
        )
        text.setWordWrap(True)
        layout.addWidget(text)


class SQLPresetWizard(QWizard):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(PRESET_NAME)
        self.resize(900, 680)
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        self.discovery_items: list[InputDocument] = []
        self.ordered_documents: list[InputDocument] = []
        self.discovery_error = ""
        self.preset_ready = False
        self.audit_completed = False
        self.audit_summary = "Publication audit not run."

        self.intro_page = _IntroPage()
        self.folders_page = _FoldersPage()
        self.discovery_page = _DiscoveryPage(self)
        self.code_policy_page = _CodePolicyPage()
        self.order_page = _OrderPage(self)
        self.audit_page = _AuditPage(self)
        self.plan_page = _PlanPage(self)
        self.run_page = _RunPage()

        self.addPage(self.intro_page)
        self.addPage(self.folders_page)
        self.addPage(self.discovery_page)
        self.addPage(self.code_policy_page)
        self.addPage(self.order_page)
        self.addPage(self.audit_page)
        self.addPage(self.plan_page)
        self.addPage(self.run_page)

    def refresh_discovery(self) -> None:
        self.discovery_items = []
        self.ordered_documents = []
        self.discovery_error = ""
        self.preset_ready = False
        self.audit_completed = False
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

        def describe(label: str, result: ValidationResult) -> str:
            return (
                f"{label}: found {len(result.found_parts)}/120 | "
                f"missing {result.missing_parts or 'none'} | "
                f"duplicates {result.duplicate_parts or 'none'}"
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
        audit = self.audit_summary if self.audit_page.enabled.isChecked() else "Audit skipped."
        return "\n".join(
            [
                "Step 7 — Merge PDFs",
                f"  {output / PDF_FILENAME}",
                "  Title page, visible TOC, part bookmarks, page numbers, metadata",
                "",
                "Step 8 — Merge DOCX",
                f"  {output / DOCX_FILENAME}",
                "  Part headings, TOC field, continuous numbering, preserved sections",
                "",
                "Step 9 — Validate Outputs",
                "  Reopen both outputs, verify structural validity, source hashes, and counts",
                "",
                "Step 10 — Reports",
                f"  {output / MANIFEST_FILENAME}",
                f"  {output / REPORT_MD_FILENAME}",
                f"  {output / REPORT_HTML_FILENAME}",
                f"  {output / CHECKSUMS_FILENAME}",
                "  Companion_Code_Index.md / .json",
                "  Publishing_Checklist.md",
                "",
                "Step 6 audit evidence:",
                audit,
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
        if self.audit_page.enabled.isChecked() and self.audit_summary:
            project.warnings.append(f"Publication audit evidence:\n{self.audit_summary}")
        return project
