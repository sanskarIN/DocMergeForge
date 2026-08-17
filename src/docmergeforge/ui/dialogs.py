from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from docmergeforge.core.models import MergeProject, MergeSettings
from docmergeforge.presets.sql_full_mastery import create_sql_full_mastery_project
from docmergeforge.settings.config import AppSettings
from docmergeforge.ui.recent import RecentProject
from docmergeforge.ui.source_picker import SourcePicker
from docmergeforge.ui.workers import MergeWorker


class PathPicker(QWidget):
    def __init__(self, title: str, directory: bool = True) -> None:
        super().__init__()
        self.title = title
        self.directory = directory
        self.setAccessibleName(title)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.edit = QLineEdit()
        self.edit.setAccessibleName(title)
        self.browse_button = QPushButton("Browse…")
        self.browse_button.setAccessibleName(f"Browse for {title.lower()}")
        self.browse_button.clicked.connect(self._browse)
        layout.addWidget(self.edit, 1)
        layout.addWidget(self.browse_button)

    def _browse(self) -> None:
        if self.directory:
            selected = QFileDialog.getExistingDirectory(self, self.title)
        else:
            selected, _ = QFileDialog.getOpenFileName(self, self.title)
        if selected:
            self.edit.setText(selected)

    def path(self) -> Path:
        return Path(self.edit.text().strip()).expanduser()

    def set_path(self, path: Path) -> None:
        self.edit.setText(str(path))


class ProjectSetupDialog(QDialog):
    def __init__(self, initial_source: Path | None = None) -> None:
        super().__init__()
        self.setWindowTitle("New Merge Project")
        self.setAccessibleName("New merge project")
        self.resize(760, 640)
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.name = QLineEdit("DocMergeForge Project")
        self.name.setAccessibleName("Project name")
        self.sources = SourcePicker()
        self.sources.setAccessibleName("Source folders and files")
        self.output = PathPicker("Select output folder")
        if initial_source:
            self.sources.add_path(initial_source)
            output_base = initial_source if initial_source.is_dir() else initial_source.parent
            self.output.set_path(output_base / "DocMergeForge-Output")
        self.start_part = QSpinBox()
        self.start_part.setAccessibleName("First part number")
        self.start_part.setRange(1, 999999)
        self.start_part.setValue(1)
        self.end_part = QSpinBox()
        self.end_part.setAccessibleName("Last part number")
        self.end_part.setRange(1, 999999)
        self.end_part.setValue(120)
        self.sql_preset = QCheckBox("Use SQL Full Mastery — 120-Part Master Edition preset")
        self.sql_preset.setAccessibleName("Use SQL Full Mastery 120-part preset")
        self.sql_preset.toggled.connect(self._preset_changed)

        form.addRow("Project name", self.name)
        form.addRow("Source folders/files", self.sources)
        form.addRow("Output folder", self.output)
        form.addRow("First part", self.start_part)
        form.addRow("Last part", self.end_part)
        form.addRow("Preset", self.sql_preset)
        layout.addLayout(form)

        note = QLabel(
            "Add one or more folders and/or individual files. PDF and DOCX are merged "
            "independently. Companion code is indexed only and never merged."
        )
        note.setAccessibleName("Project source guidance")
        note.setWordWrap(True)
        layout.addWidget(note)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok
        )
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setAccessibleName(
            "Create merge project"
        )
        self.buttons.button(QDialogButtonBox.StandardButton.Cancel).setAccessibleName(
            "Cancel new merge project"
        )
        self.buttons.accepted.connect(self._validate_and_accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def _preset_changed(self, checked: bool) -> None:
        if checked:
            self.name.setText("SQL Full Mastery — 120-Part Master Edition")
            self.start_part.setValue(1)
            self.end_part.setValue(120)
            self.start_part.setEnabled(False)
            self.end_part.setEnabled(False)
        else:
            self.start_part.setEnabled(True)
            self.end_part.setEnabled(True)

    def _validate_and_accept(self) -> None:
        sources = self.sources.paths()
        output = self.output.path()
        if not sources:
            QMessageBox.warning(
                self,
                "Sources required",
                "Add at least one source folder or individual file.",
            )
            return
        missing = [path for path in sources if not path.exists()]
        if missing:
            QMessageBox.warning(
                self,
                "Source unavailable",
                "One or more selected sources no longer exist:\n"
                + "\n".join(str(path) for path in missing[:10]),
            )
            return
        if self.sql_preset.isChecked() and (len(sources) != 1 or not sources[0].is_dir()):
            QMessageBox.warning(
                self,
                "SQL preset source",
                "The SQL Full Mastery preset requires exactly one root folder. "
                "Use its dedicated guided workflow for the complete preset experience.",
            )
            return
        if self.end_part.value() < self.start_part.value():
            QMessageBox.warning(self, "Invalid range", "Last part must be at least the first part.")
            return
        if not self.output.edit.text().strip():
            QMessageBox.warning(self, "Output required", "Choose an output folder.")
            return
        try:
            output.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            QMessageBox.warning(self, "Output unavailable", str(exc))
            return
        self.accept()

    def project(self) -> MergeProject:
        sources = self.sources.paths()
        if self.sql_preset.isChecked():
            return create_sql_full_mastery_project(sources[0], self.output.path())
        return MergeProject(
            name=self.name.text().strip() or "DocMergeForge Project",
            source_folders=sources,
            output_folder=self.output.path(),
            settings=MergeSettings(
                expected_start=self.start_part.value(),
                expected_end=self.end_part.value(),
            ),
        )


class SettingsDialog(QDialog):
    def __init__(self, settings: AppSettings) -> None:
        super().__init__()
        self._base = settings
        self.setWindowTitle("DocMergeForge Settings")
        self.setAccessibleName("DocMergeForge settings")
        self.setMinimumWidth(680)
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.theme = QComboBox()
        self.theme.setAccessibleName("Theme")
        self.theme.addItems(["system", "light", "dark"])
        self.theme.setCurrentText(settings.theme)

        self.profile = QComboBox()
        self.profile.setAccessibleName("Merge profile")
        self.profile.addItems(
            ["Exact Preservation", "Master eBook", "Print Draft", "Archive", "Custom"]
        )
        self.profile.setCurrentText(settings.merge_profile)

        self.filename_template = QLineEdit(settings.filename_template)
        self.filename_template.setAccessibleName("Filename template")
        self.filename_template.setPlaceholderText(
            "{series}_Complete_{part_count}_Part_Master_Edition"
        )

        self.output = PathPicker("Select default output folder")
        if settings.default_output_folder:
            self.output.set_path(Path(settings.default_output_folder))
        self.temp = PathPicker("Select temporary directory")
        if settings.temporary_directory:
            self.temp.set_path(Path(settings.temporary_directory))

        self.workers = QSpinBox()
        self.workers.setAccessibleName("Worker count")
        self.workers.setRange(1, 64)
        self.workers.setValue(settings.worker_count)

        self.logging = QComboBox()
        self.logging.setAccessibleName("Logging level")
        self.logging.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self.logging.setCurrentText(settings.logging_level)

        self.checksums = QCheckBox()
        self.checksums.setAccessibleName("Generate checksums")
        self.checksums.setChecked(settings.checksum_generation)
        self.validation = QCheckBox()
        self.validation.setAccessibleName("Automatic validation")
        self.validation.setChecked(settings.automatic_validation)

        self.pdf_optimization = QComboBox()
        self.pdf_optimization.setAccessibleName("PDF optimization")
        self.pdf_optimization.addItems(["preserve", "balanced", "archive"])
        self.pdf_optimization.setCurrentText(settings.pdf_optimization)

        self.fidelity = QComboBox()
        self.fidelity.setAccessibleName("DOCX fidelity mode")
        self.fidelity.setAccessibleDescription(
            "Portable is production-ready. External high-fidelity adapters require availability "
            "and production readiness."
        )
        self.fidelity.addItems(["portable", "libreoffice", "word"])
        self.fidelity.setCurrentText(settings.docx_fidelity_mode)

        self.libreoffice = QCheckBox()
        self.libreoffice.setAccessibleName("Enable LibreOffice integration")
        self.libreoffice.setChecked(settings.libreoffice_integration)
        self.word_fidelity = QCheckBox()
        self.word_fidelity.setAccessibleName("Enable Word high-fidelity mode")
        self.word_fidelity.setChecked(settings.word_high_fidelity)
        self.recovery = QCheckBox()
        self.recovery.setAccessibleName("Crash recovery")
        self.recovery.setChecked(settings.crash_recovery)
        self.recent_history = QCheckBox()
        self.recent_history.setAccessibleName("Recent project history")
        self.recent_history.setChecked(settings.recent_project_history)
        self.reduced_motion = QCheckBox()
        self.reduced_motion.setAccessibleName("Reduced motion")
        self.reduced_motion.setChecked(settings.reduced_motion)

        self.text_scale = QSpinBox()
        self.text_scale.setAccessibleName("Text scale percent")
        self.text_scale.setRange(80, 200)
        self.text_scale.setSingleStep(10)
        self.text_scale.setSuffix("%")
        self.text_scale.setValue(settings.text_scale_percent)

        form.addRow("Theme", self.theme)
        form.addRow("Merge profile", self.profile)
        form.addRow("Filename template", self.filename_template)
        form.addRow("Default output", self.output)
        form.addRow("Temporary directory", self.temp)
        form.addRow("Worker count", self.workers)
        form.addRow("Logging level", self.logging)
        form.addRow("Generate checksums", self.checksums)
        form.addRow("Automatic validation", self.validation)
        form.addRow("PDF optimization", self.pdf_optimization)
        form.addRow("DOCX fidelity mode", self.fidelity)
        form.addRow("Enable LibreOffice integration", self.libreoffice)
        form.addRow("Enable Word high-fidelity mode", self.word_fidelity)
        form.addRow("Crash recovery", self.recovery)
        form.addRow("Recent project history", self.recent_history)
        form.addRow("Reduced motion", self.reduced_motion)
        form.addRow("Text scale", self.text_scale)
        layout.addLayout(form)

        fidelity_note = QLabel(
            "High-fidelity adapters are used only when explicitly selected and available. "
            "Portable mode remains the default."
        )
        fidelity_note.setAccessibleName("DOCX fidelity guidance")
        fidelity_note.setWordWrap(True)
        layout.addWidget(fidelity_note)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Save
        )
        self.buttons.button(QDialogButtonBox.StandardButton.Save).setAccessibleName("Save settings")
        self.buttons.button(QDialogButtonBox.StandardButton.Cancel).setAccessibleName(
            "Cancel settings changes"
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def settings(self) -> AppSettings:
        return AppSettings(
            theme=self.theme.currentText(),
            default_output_folder=self.output.edit.text().strip(),
            temporary_directory=self.temp.edit.text().strip(),
            worker_count=self.workers.value(),
            logging_level=self.logging.currentText(),
            checksum_generation=self.checksums.isChecked(),
            automatic_validation=self.validation.isChecked(),
            pdf_optimization=self.pdf_optimization.currentText(),
            docx_fidelity_mode=self.fidelity.currentText(),
            crash_recovery=self.recovery.isChecked(),
            merge_profile=self.profile.currentText(),
            filename_template=self.filename_template.text().strip(),
            libreoffice_integration=self.libreoffice.isChecked(),
            word_high_fidelity=self.word_fidelity.isChecked(),
            recent_project_history=self.recent_history.isChecked(),
            reduced_motion=self.reduced_motion.isChecked(),
            text_scale_percent=self.text_scale.value(),
            first_run_completed=self._base.first_run_completed,
        )


class TextReportDialog(QDialog):
    def __init__(self, title: str, text: str) -> None:
        super().__init__()
        self.setWindowTitle(title)
        self.setAccessibleName(title)
        self.resize(820, 620)
        layout = QVBoxLayout(self)
        self.editor = QPlainTextEdit()
        self.editor.setAccessibleName(f"{title} report content")
        self.editor.setReadOnly(True)
        self.editor.setPlainText(text)
        layout.addWidget(self.editor)
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        self.buttons.button(QDialogButtonBox.StandardButton.Close).setAccessibleName(
            f"Close {title}"
        )
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)


class RecentProjectsDialog(QDialog):
    def __init__(self, projects: list[RecentProject]) -> None:
        super().__init__()
        self.setWindowTitle("Recent Projects")
        self.setAccessibleName("Recent projects")
        self.resize(700, 430)
        self._projects = projects
        layout = QVBoxLayout(self)
        self.list = QListWidget()
        self.list.setAccessibleName("Recent project list")
        for project in projects:
            self.list.addItem(f"{project.name}\n{project.project_file}")
        layout.addWidget(self.list)
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Open
        )
        self.buttons.button(QDialogButtonBox.StandardButton.Open).setAccessibleName(
            "Open selected recent project"
        )
        self.buttons.button(QDialogButtonBox.StandardButton.Cancel).setAccessibleName(
            "Cancel recent project selection"
        )
        self.buttons.accepted.connect(self._open)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def _open(self) -> None:
        if self.list.currentRow() < 0:
            QMessageBox.information(self, "Recent Projects", "Select a project first.")
            return
        self.accept()

    def selected(self) -> RecentProject | None:
        index = self.list.currentRow()
        return self._projects[index] if 0 <= index < len(self._projects) else None


class MergeProgressDialog(QDialog):
    def __init__(self, worker: MergeWorker, title: str = "DocMergeForge") -> None:
        super().__init__()
        self.worker = worker
        self.setWindowTitle(title)
        self.setAccessibleName(f"{title} progress")
        self.setModal(True)
        self.setMinimumWidth(560)
        layout = QVBoxLayout(self)
        self.stage = QLabel("Preparing…")
        self.stage.setAccessibleName("Merge stage")
        self.stage.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.progress = QProgressBar()
        self.progress.setAccessibleName("Merge progress")
        self.progress.setRange(0, 100)
        self.current_file = QLabel("")
        self.current_file.setAccessibleName("Current merge file")
        self.current_file.setWordWrap(True)
        self.cancel_button = QPushButton("Cancel safely")
        self.cancel_button.setAccessibleName("Cancel merge safely")
        self.cancel_button.setAccessibleDescription(
            "Requests cooperative cancellation without publishing partial output."
        )
        self.cancel_button.clicked.connect(self._cancel)
        layout.addWidget(self.stage)
        layout.addWidget(self.progress)
        layout.addWidget(self.current_file)
        layout.addWidget(self.cancel_button)

        worker.progress_changed.connect(self._on_progress)
        worker.completed.connect(self.accept)
        worker.cancelled.connect(self.reject)
        worker.failed.connect(self._on_failure)

    def start(self) -> int:
        self.worker.start()
        return self.exec()

    def _cancel(self) -> None:
        self.worker.request_cancel()
        self.stage.setText("Cancelling safely…")

    def _on_progress(self, stage: str, current: int, total: int, path: str) -> None:
        label = stage.replace("-", " ").title()
        self.stage.setText(f"{label}: {current}/{total}")
        self.progress.setValue(int((current / total) * 100) if total else 0)
        self.current_file.setText(path)

    def _on_failure(self, message: str) -> None:
        QMessageBox.critical(self, "Operation failed safely", message)
        self.reject()
