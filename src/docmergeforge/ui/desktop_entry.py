from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtWidgets import QFileDialog, QMessageBox, QPushButton, QVBoxLayout

from docmergeforge.project.store import load_project_snapshot
from docmergeforge.project.sync import apply_project_sync, plan_project_sync
from docmergeforge.ui import main as ui_main
from docmergeforge.ui.project_sync_dialog import ProjectSyncDialog


class ProjectSyncMainWindow(ui_main.MainWindow):
    """Desktop window with guarded reusable-project source synchronization."""

    def __init__(self) -> None:
        super().__init__()
        button = QPushButton("Synchronize Project Sources")
        button.setAccessibleName("Synchronize project sources")
        button.setAccessibleDescription(
            "Preview and optionally apply a guarded refresh of a saved project's selected files."
        )
        button.setMinimumHeight(58)
        button.clicked.connect(self._synchronize_project)

        central = self.centralWidget()
        layout = central.layout() if central is not None else None
        if isinstance(layout, QVBoxLayout):
            layout.insertWidget(max(0, layout.count() - 1), button)
        else:
            button.setParent(central)
            button.show()

    def _synchronize_project(self) -> None:
        project_file, _ = QFileDialog.getOpenFileName(
            self,
            "Synchronize DocMergeForge Project",
            "",
            "DocMergeForge Project (*.json)",
        )
        if not project_file:
            return

        path = Path(project_file)
        try:
            project, revision = load_project_snapshot(path)
            plan = plan_project_sync(project)
        except (OSError, ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
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
    """Run the normal desktop startup using the synchronization-enabled window."""

    original_window = ui_main.MainWindow
    ui_main.MainWindow = ProjectSyncMainWindow
    try:
        return ui_main.main()
    finally:
        ui_main.MainWindow = original_window


if __name__ == "__main__":
    raise SystemExit(main())
