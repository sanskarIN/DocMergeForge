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
from docmergeforge.ui.workers import MergeWorker


class PathPicker(QWidget):
    def __init__(self, title: str, directory: bool = True) -> None:
        super().__init__()
        self.title = title
        self.directory = directory
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.edit = QLineEdit()
        button = QPushButton("Browse…")
        button.clicked.connect(self._browse)
        layout.addWidget(self.edit, 1)
        layout.addWidget(button)

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
        self.setMinimumWidth(650)
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.name = QLineEdit("DocMergeForge Project")
        self.source = PathPicker("Select input folder")
        self.output = PathPicker("Select output folder")
        if initial_source:
            self.source.set_path(initial_source)
            self.output.set_path(initial_source / "DocMergeForge-Output")
        self.start_part = QSpinBox()
        self.start_part.setRange(1, 999999)
        self.start_part.setValue(1)
        self.end_part = QSpinBox()
        self.end_part.setRange(1, 999999)
        self.end_part.setValue(120)
        self.sql_preset = QCheckBox("Use SQL Full Mastery — 120-Part Master Edition preset")
        self.sql_preset.toggled.connect(self._preset_changed)

        form.addRow("Project name", self.name)
        form.addRow("Input folder", self.source)
        form.addRow("Output folder", self.output)
        form.addRow("First part", self.start_part)
        form.addRow("Last part", self.end_part)
        form.addRow("Preset", self.sql_preset)
        layout.addLayout(form)

        note = QLabel(
            "PDF and DOCX are merged independently. Companion code is indexed only "
            "and never merged."
        )
        note.setWordWrap(True)
        layout.addWidget(note)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok
        )
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

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
        source = self.source.path()
        output = self.output.path()
        if not source.exists() or not source.is_dir():
            QMessageBox.warning(self, "Input required", "Choose an existing input folder.")
            return
        if self.end_part.value() < self.start_part.value():
            QMessageBox.warning(self, "Invalid range", "Last part must be at least the first part.")
            return
        if not str(output):
            QMessageBox.warning(self, "Output required", "Choose an output folder.")
            return
        self.accept()

    def project(self) -> MergeProject:
        if self.sql_preset.isChecked():
            return create_sql_full_mastery_project(self.source.path(), self.output.path())
        return MergeProject(
            name=self.name.text().strip() or "DocMergeForge Project",
            source_folders=[self.source.path()],
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
        self.setMinimumWidth(680)
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.theme = QComboBox()
        self.theme.addItems(["system", "light", "dark"])
        self.theme.setCurrentText(settings.theme)

        self.profile = QComboBox()
        self.profile.addItems(
            ["Exact Preservation", "Master eBook", "Print Draft", "Archive", "Custom"]
        )
        self.profile.setCurrentText(settings.merge_profile)

        self.filename_template = QLineEdit(settings.filename_template)
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
        self.workers.setRange(1, 64)
        self.workers.setValue(settings.worker_count)

        self.logging = QComboBox()
        self.logging.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self.logging.setCurrentText(settings.logging_level)

        self.checksums = QCheckBox()
        self.checksums.setChecked(settings.checksum_generation)
        self.validation = QCheckBox()
        self.validation.setChecked(settings.automatic_validation)

        self.pdf_optimization = QComboBox()
        self.pdf_optimization.addItems(["preserve", "balanced", "archive"])
        self.pdf_optimization.setCurrentText(settings.pdf_optimization)

        self.fidelity = QComboBox()
        self.fidelity.addItems(["portable", "libreoffice", "word"])
        self.fidelity.setCurrentText(settings.docx_fidelity_mode)

        self.libreoffice = QCheckBox()
        self.libreoffice.setChecked(settings.libreoffice_integration)
        self.word_fidelity = QCheckBox()
        self.word_fidelity.setChecked(settings.word_high_fidelity)
        self.recovery = QCheckBox()
        self.recovery.setChecked(settings.crash_recovery)
        self.recent_history = QCheckBox()
        self.recent_history.setChecked(settings.recent_project_history)
        self.reduced_motion = QCheckBox()
        self.reduced_motion.setChecked(settings.reduced_motion)

        self.text_scale = QSpinBox()
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
        fidelity_note.setWordWrap(True)
        layout.addWidget(fidelity_note)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Save
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

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
        self.resize(820, 620)
        layout = QVBoxLayout(self)
        editor = QPlainTextEdit()
        editor.setReadOnly(True)
        editor.setPlainText(text)
        layout.addWidget(editor)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)


class RecentProjectsDialog(QDialog):
    def __init__(self, projects: list[RecentProject]) -> None:
        super().__init__()
        self.setWindowTitle("Recent Projects")
        self.resize(700, 430)
        self._projects = projects
        layout = QVBoxLayout(self)
        self.list = QListWidget()
        for project in projects:
            self.list.addItem(f"{project.name}\n{project.project_file}")
        layout.addWidget(self.list)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Open
        )
        buttons.accepted.connect(self._open)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

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
        self.setModal(True)
        self.setMinimumWidth(560)
        layout = QVBoxLayout(self)
        self.stage = QLabel("Preparing…")
        self.stage.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.current_file = QLabel("")
        self.current_file.setWordWrap(True)
        cancel = QPushButton("Cancel safely")
        cancel.clicked.connect(self._cancel)
        layout.addWidget(self.stage)
        layout.addWidget(self.progress)
        layout.addWidget(self.current_file)
        layout.addWidget(cancel)

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
