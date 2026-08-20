from __future__ import annotations

import os
from pathlib import Path

from docmergeforge.core.models import DocumentKind, InputDocument, PartIdentity
from docmergeforge.project.sync import ProjectSyncPlan
from docmergeforge.settings.config import AppSettings
from docmergeforge.ui.recent import RecentProject

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import (  # noqa: E402
    QApplication,
    QDialogButtonBox,
    QPushButton,
    QWidget,
)

from docmergeforge.ui.desktop_entry import ProjectSyncMainWindow  # noqa: E402
from docmergeforge.ui.dialogs import (  # noqa: E402
    MergeProgressDialog,
    ProjectSetupDialog,
    RecentProjectsDialog,
    SettingsDialog,
    TextReportDialog,
)
from docmergeforge.ui.order_dialog import OrderEditorDialog  # noqa: E402
from docmergeforge.ui.project_sync_dialog import ProjectSyncDialog  # noqa: E402
from docmergeforge.ui.theme import apply_text_scale, apply_theme  # noqa: E402
from docmergeforge.ui.workers import MergeWorker  # noqa: E402


def _sample_document(part: int) -> InputDocument:
    return InputDocument(
        Path(f"Part {part}.pdf"),
        DocumentKind.PDF,
        PartIdentity(part, f"Part {part}"),
        1,
        f"{part:064x}",
        1,
    )


def _require_name(issues: list[str], widget: QWidget, label: str) -> None:
    if not widget.accessibleName().strip():
        issues.append(f"{label}: missing accessible name")


def _check_order_editor(issues: list[str]) -> OrderEditorDialog:
    dialog = OrderEditorDialog(
        [_sample_document(1), _sample_document(2)],
        1,
        2,
    )
    _require_name(issues, dialog, "order dialog")
    _require_name(issues, dialog.search_label, "search label")
    _require_name(issues, dialog.search, "search field")
    _require_name(issues, dialog.lock, "lock order")
    _require_name(issues, dialog.list, "order list")
    _require_name(issues, dialog.validation, "validation summary")
    _require_name(issues, dialog.boundary, "boundary preview")

    if dialog.search_label.buddy() is not dialog.search:
        issues.append("search label: keyboard buddy is not the search field")
    if not dialog.search.accessibleDescription().strip():
        issues.append("search field: missing accessible description")
    if not dialog.list.accessibleDescription().strip():
        issues.append("order list: missing accessible description")
    if dialog.lock.shortcut().isEmpty():
        issues.append("lock order: missing keyboard shortcut")

    for button in dialog._manual_buttons:
        label = button.text() or "manual order button"
        _require_name(issues, button, label)
        if not button.accessibleDescription().strip():
            issues.append(f"{label}: missing accessible description")
        if button.shortcut().isEmpty():
            issues.append(f"{label}: missing keyboard shortcut")

    confirm = dialog.buttons.button(QDialogButtonBox.StandardButton.Ok)
    cancel = dialog.buttons.button(QDialogButtonBox.StandardButton.Cancel)
    _require_name(issues, confirm, "confirm order")
    _require_name(issues, cancel, "cancel order")
    return dialog


def _check_project_setup(issues: list[str]) -> ProjectSetupDialog:
    dialog = ProjectSetupDialog()
    _require_name(issues, dialog, "project setup dialog")
    for label, widget in (
        ("project name", dialog.name),
        ("project sources", dialog.sources),
        ("output path picker", dialog.output),
        ("first part", dialog.start_part),
        ("last part", dialog.end_part),
        ("SQL preset", dialog.sql_preset),
        ("source list", dialog.sources.list),
        ("add source folder", dialog.sources.add_folder_button),
        ("add source files", dialog.sources.add_files_button),
        ("remove sources", dialog.sources.remove_button),
        ("clear sources", dialog.sources.clear_button),
    ):
        _require_name(issues, widget, label)

    for label, button in (
        ("add source folder", dialog.sources.add_folder_button),
        ("add source files", dialog.sources.add_files_button),
        ("remove sources", dialog.sources.remove_button),
        ("clear sources", dialog.sources.clear_button),
    ):
        if button.shortcut().isEmpty():
            issues.append(f"{label}: missing keyboard shortcut")

    _require_name(
        issues,
        dialog.buttons.button(QDialogButtonBox.StandardButton.Ok),
        "create project",
    )
    _require_name(
        issues,
        dialog.buttons.button(QDialogButtonBox.StandardButton.Cancel),
        "cancel project",
    )
    return dialog


def _check_project_sync(issues: list[str]) -> list[QWidget]:
    current = Path("Part 1.pdf")
    added = Path("Part 2.pdf")
    plan = ProjectSyncPlan(
        current=(current,),
        proposed=(current, added),
        added=(added,),
        removed=(),
        reordered=False,
        duplicate_pdf_parts=(),
        duplicate_docx_parts=(),
        missing_pdf_parts=(),
        missing_docx_parts=(),
    )
    dialog = ProjectSyncDialog(Path("example-project.json"), plan)
    _require_name(issues, dialog, "project synchronization dialog")
    _require_name(issues, dialog.guidance, "project synchronization guidance")
    _require_name(issues, dialog.preview, "project synchronization preview")
    if not dialog.preview.accessibleDescription().strip():
        issues.append("project synchronization preview: missing accessible description")

    apply_button = dialog.buttons.button(QDialogButtonBox.StandardButton.Save)
    cancel_button = dialog.buttons.button(QDialogButtonBox.StandardButton.Cancel)
    _require_name(issues, apply_button, "apply project synchronization")
    _require_name(issues, cancel_button, "cancel project synchronization")
    if not apply_button.accessibleDescription().strip():
        issues.append("apply project synchronization: missing accessible description")
    if not apply_button.isEnabled():
        issues.append("apply project synchronization: safe changed proposal is disabled")

    window = ProjectSyncMainWindow()
    buttons = {button.accessibleName(): button for button in window.findChildren(QPushButton)}
    for name, label in (
        ("Synchronize project sources", "desktop browse project synchronization"),
        ("Synchronize recent project", "desktop recent project synchronization"),
    ):
        button = buttons.get(name)
        if button is None:
            issues.append(f"{label}: action is missing")
            continue
        if not button.accessibleDescription().strip():
            issues.append(f"{label}: missing accessible description")

    return [dialog, window]


def _check_settings(issues: list[str]) -> SettingsDialog:
    dialog = SettingsDialog(AppSettings())
    _require_name(issues, dialog, "settings dialog")
    for label, widget in (
        ("theme", dialog.theme),
        ("merge profile", dialog.profile),
        ("filename template", dialog.filename_template),
        ("default output", dialog.output),
        ("temporary directory", dialog.temp),
        ("worker count", dialog.workers),
        ("logging level", dialog.logging),
        ("checksums", dialog.checksums),
        ("automatic validation", dialog.validation),
        ("PDF optimization", dialog.pdf_optimization),
        ("DOCX fidelity", dialog.fidelity),
        ("LibreOffice integration", dialog.libreoffice),
        ("Word fidelity", dialog.word_fidelity),
        ("crash recovery", dialog.recovery),
        ("recent history", dialog.recent_history),
        ("reduced motion", dialog.reduced_motion),
        ("text scale", dialog.text_scale),
    ):
        _require_name(issues, widget, label)

    if not dialog.fidelity.accessibleDescription().strip():
        issues.append("DOCX fidelity: missing safety description")
    _require_name(
        issues,
        dialog.buttons.button(QDialogButtonBox.StandardButton.Save),
        "save settings",
    )
    _require_name(
        issues,
        dialog.buttons.button(QDialogButtonBox.StandardButton.Cancel),
        "cancel settings",
    )
    return dialog


def _check_visual_preferences(app: QApplication, issues: list[str]) -> None:
    apply_text_scale(app, 100)
    base_value = app.property("docmergeforgeBasePointSize")
    if not isinstance(base_value, float) or base_value <= 0:
        issues.append("text scale: missing positive base font size")
        return

    for requested, expected_factor in ((50, 0.8), (100, 1.0), (250, 2.0)):
        apply_text_scale(app, requested)
        expected = base_value * expected_factor
        if abs(app.font().pointSizeF() - expected) > 0.01:
            issues.append(f"text scale: {requested}% did not clamp/apply to {expected_factor:.1f}x")

    apply_theme(app, "dark")
    if "#111827" not in app.styleSheet():
        issues.append("theme: dark stylesheet was not applied")
    apply_theme(app, "light")
    if "#ffffff" not in app.styleSheet():
        issues.append("theme: light stylesheet was not applied")
    apply_theme(app, "system")
    if app.styleSheet():
        issues.append("theme: system mode did not restore the native stylesheet")

    preference_dialog = SettingsDialog(
        AppSettings(theme="dark", reduced_motion=True, text_scale_percent=170)
    )
    round_trip = preference_dialog.settings()
    if round_trip.theme != "dark":
        issues.append("settings: theme preference did not round-trip")
    if not round_trip.reduced_motion:
        issues.append("settings: reduced-motion preference did not round-trip")
    if round_trip.text_scale_percent != 170:
        issues.append("settings: text-scale preference did not round-trip")
    preference_dialog.close()

    apply_text_scale(app, 100)
    apply_theme(app, "system")


def _check_secondary_dialogs(issues: list[str]) -> list[QWidget]:
    report = TextReportDialog("Accessibility Report", "Example")
    _require_name(issues, report, "report dialog")
    _require_name(issues, report.editor, "report content")

    recent = RecentProjectsDialog(
        [
            RecentProject(
                "Example",
                Path("example.json"),
                Path("source"),
                Path("output"),
            )
        ]
    )
    _require_name(issues, recent, "recent projects dialog")
    _require_name(issues, recent.list, "recent projects list")
    _require_name(
        issues,
        recent.buttons.button(QDialogButtonBox.StandardButton.Open),
        "open recent project",
    )

    worker = MergeWorker(lambda _progress, _cancelled: None)
    progress = MergeProgressDialog(worker)
    _require_name(issues, progress, "merge progress dialog")
    _require_name(issues, progress.stage, "merge stage")
    _require_name(issues, progress.progress, "merge progress bar")
    _require_name(issues, progress.current_file, "current merge file")
    _require_name(issues, progress.cancel_button, "safe cancel")
    if not progress.cancel_button.accessibleDescription().strip():
        issues.append("safe cancel: missing cancellation behavior description")

    return [report, recent, progress]


def main() -> int:
    app = QApplication.instance()
    if not isinstance(app, QApplication):
        app = QApplication([])

    issues: list[str] = []
    _check_visual_preferences(app, issues)
    widgets: list[QWidget] = [
        _check_order_editor(issues),
        _check_project_setup(issues),
        *_check_project_sync(issues),
        _check_settings(issues),
        *_check_secondary_dialogs(issues),
    ]

    for widget in widgets:
        widget.close()
    app.processEvents()

    if issues:
        print("Desktop accessibility smoke failed:")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print(
        "Desktop accessibility smoke passed: project setup, source picking, ordering, "
        "project synchronization, settings, reports, recent projects, merge progress, theme "
        "application, text scaling, and reduced-motion preference metadata are verified offscreen."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
