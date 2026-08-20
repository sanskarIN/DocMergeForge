from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from docmergeforge.diagnostics.logging import configure_logging
from docmergeforge.project.store import load_project_snapshot
from docmergeforge.project.sync import apply_project_sync, plan_project_sync
from docmergeforge.settings.config import AppSettings
from docmergeforge.ui import main as ui_main
from docmergeforge.ui.dialogs import RecentProjectsDialog
from docmergeforge.ui.paths import log_path, settings_path
from docmergeforge.ui.project_sync_dialog import ProjectSyncDialog
from docmergeforge.ui.theme import apply_text_scale, apply_theme


class ProjectSyncMainWindow(ui_main.MainWindow):
    """Desktop window with guarded reusable-project source synchronization."""

    def __init__(self) -> None:
        super().__init__()
        browse_button = QPushButton("Synchronize Project Sources")
        browse_button.setAccessibleName("Synchronize project sources")
        browse_button.setAccessibleDescription(
            "Browse for a saved project, preview source-selection changes, and optionally apply them."
        )
        browse_button.setMinimumHeight(58)
        browse_button.clicked.connect(self._synchronize_project)

        recent_button = QPushButton("Synchronize Recent Project")
        recent_button.setAccessibleName("Synchronize recent project")
        recent_button.setAccessibleDescription(
            "Choose a saved recent project, then use the same guarded synchronization preview."
        )
        recent_button.setMinimumHeight(58)
        recent_button.clicked.connect(self._synchronize_recent_project)

        sync_row = QHBoxLayout()
        sync_row.addWidget(browse_button)
        sync_row.addWidget(recent_button)

        central = self.centralWidget()
        layout = central.layout() if central is not None else None
        if isinstance(layout, QVBoxLayout):
            layout.insertLayout(max(0, layout.count() - 1), sync_row)
        else:
            browse_button.setParent(central)
            recent_button.setParent(central)
            browse_button.show()
            recent_button.show()

    def _synchronize_project(self) -> None:
        project_file, _ = QFileDialog.getOpenFileName(
            self,
            "Synchronize DocMergeForge Project",
            "",
            "DocMergeForge Project (*.json)",
        )
        if project_file:
            self._synchronize_project_path(Path(project_file))

    def _synchronize_recent_project(self) -> None:
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
        if selected is not None:
            self._synchronize_project_path(selected.project_file)

    def _synchronize_project_path(self, path: Path) -> None:
        try:
            project, revision = load_project_snapshot(path)
            plan = plan_project_sync(project)
        except (OSError, ValueError, UnicodeDecodeError) as exc:
            self._record_error(str(exc))
            QMessageBox.critical(self, "Project synchronization preview failed", str(exc))
            return

        dialog = ProjectSyncDialog(path, plan)
        result = dialog.exec()
        if not plan.safe_to_apply:
            self.statusBar().showMessage(
                "Synchronization blocked until duplicate numbered parts are resolved.",
                7000,
            )
            return
        if not plan.changed:
            self.statusBar().showMessage("Project sources are already synchronized.", 5000)
            return
        if result != int(dialog.DialogCode.Accepted):
            return

        if plan.removed:
            shown = "\n".join(str(item) for item in plan.removed[:20])
            remaining = len(plan.removed) - 20
            suffix = f"\n… and {remaining} more" if remaining > 0 else ""
            answer = QMessageBox.question(
                self,
                "Approve selected-file removals",
                "The reviewed synchronization proposal removes these paths from the project's "
                "selected_files list:\n\n"
                f"{shown}{suffix}\n\n"
                "This does not delete any manuscript source files. Apply these removals?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                self.statusBar().showMessage("Project synchronization cancelled.", 5000)
                return

        try:
            backup = apply_project_sync(
                project,
                path,
                plan,
                expected_revision=revision,
            )
        except (OSError, ValueError, UnicodeDecodeError) as exc:
            self._record_error(str(exc))
            QMessageBox.critical(self, "Project synchronization failed", str(exc))
            return

        self._remember_project(project, path)
        self.logger.info(
            "project synchronization applied project=%s backup=%s selected=%s",
            path,
            backup or "",
            len(project.selected_files),
        )
        self.statusBar().showMessage("Project source selection synchronized safely.", 7000)
        QMessageBox.information(
            self,
            "Project sources synchronized",
            "The reviewed selected-file proposal was applied safely.\n\n"
            f"Project: {path}\n"
            f"Backup: {backup or 'Not required'}\n"
            f"Selected files: {len(project.selected_files)}\n\n"
            "No manuscript source files were deleted.",
        )


def main() -> int:
    """Run the synchronization-enabled desktop application."""

    app = QApplication(sys.argv)
    app.setApplicationName("DocMergeForge")
    app.setOrganizationName("Sanskar")
    settings = AppSettings.load(settings_path())
    configure_logging(log_path(), settings.logging_level)
    apply_theme(app, settings.theme)
    apply_text_scale(app, settings.text_scale_percent)
    window = ProjectSyncMainWindow()
    window.show()
    QTimer.singleShot(0, window.show_startup_dialogs)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
