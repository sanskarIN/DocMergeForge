from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QPlainTextEdit, QVBoxLayout

from docmergeforge.project.sync import ProjectSyncPlan


def _format_numbers(values: tuple[int, ...]) -> str:
    return ", ".join(str(value) for value in values) if values else "None"


def _format_paths(paths: tuple[Path, ...]) -> str:
    return "\n".join(f"- {path}" for path in paths) if paths else "- None"


def format_project_sync_plan(project_path: Path, plan: ProjectSyncPlan) -> str:
    """Return a complete human-reviewable synchronization preview."""

    return (
        f"Project: {project_path}\n\n"
        f"Current selected files: {len(plan.current)}\n"
        f"Proposed selected files: {len(plan.proposed)}\n"
        f"Changed: {'Yes' if plan.changed else 'No'}\n"
        f"Safe to apply: {'Yes' if plan.safe_to_apply else 'No'}\n"
        "Numbering complete for available kinds: "
        f"{'Yes' if plan.numbering_complete_for_available_kinds else 'No'}\n"
        f"Reordered existing files: {'Yes' if plan.reordered else 'No'}\n\n"
        "Duplicate PDF parts: "
        f"{_format_numbers(plan.duplicate_pdf_parts)}\n"
        "Duplicate DOCX parts: "
        f"{_format_numbers(plan.duplicate_docx_parts)}\n"
        "Missing PDF parts: "
        f"{_format_numbers(plan.missing_pdf_parts)}\n"
        "Missing DOCX parts: "
        f"{_format_numbers(plan.missing_docx_parts)}\n\n"
        "Added to selected_files:\n"
        f"{_format_paths(plan.added)}\n\n"
        "Removed from selected_files:\n"
        f"{_format_paths(plan.removed)}\n\n"
        "Proposed selected_files order:\n"
        f"{_format_paths(plan.proposed)}\n\n"
        "Synchronization changes only project metadata. It never deletes manuscript source files."
    )


class ProjectSyncDialog(QDialog):
    """Preview and authorize one guarded project-selection synchronization plan."""

    def __init__(self, project_path: Path, plan: ProjectSyncPlan) -> None:
        super().__init__()
        self.setWindowTitle("Synchronize Project Sources")
        self.setAccessibleName("Synchronize project sources")
        self.resize(900, 680)

        layout = QVBoxLayout(self)
        if not plan.safe_to_apply:
            guidance = (
                "This proposal cannot be applied because duplicate numbered PDF or DOCX parts "
                "make the automatic selection ambiguous. Resolve the duplicates and preview again."
            )
        elif not plan.changed:
            guidance = "The saved selected-file list already matches the current automatic proposal."
        elif plan.removed:
            guidance = (
                "Review the removals carefully. Applying this proposal requires a separate removal "
                "approval after this preview. Source files themselves will not be deleted."
            )
        else:
            guidance = (
                "Review the complete proposal before applying it. A versioned backup of the project "
                "JSON will be created before the guarded update."
            )

        self.guidance = QLabel(guidance)
        self.guidance.setAccessibleName("Project synchronization guidance")
        self.guidance.setWordWrap(True)
        layout.addWidget(self.guidance)

        self.preview = QPlainTextEdit()
        self.preview.setAccessibleName("Project synchronization preview")
        self.preview.setAccessibleDescription(
            "Read-only preview of current, added, removed, reordered, duplicate, missing, and "
            "proposed project source selections."
        )
        self.preview.setReadOnly(True)
        self.preview.setPlainText(format_project_sync_plan(project_path, plan))
        layout.addWidget(self.preview, 1)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Save
        )
        apply_button = self.buttons.button(QDialogButtonBox.StandardButton.Save)
        apply_button.setText("Apply synchronization")
        apply_button.setAccessibleName("Apply project source synchronization")
        apply_button.setAccessibleDescription(
            "Applies the reviewed selected-file proposal. Removals require one more approval."
        )
        apply_button.setEnabled(plan.changed and plan.safe_to_apply)

        close_button = self.buttons.button(QDialogButtonBox.StandardButton.Cancel)
        close_button.setText("Close" if not plan.changed or not plan.safe_to_apply else "Cancel")
        close_button.setAccessibleName("Close project synchronization preview")

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
