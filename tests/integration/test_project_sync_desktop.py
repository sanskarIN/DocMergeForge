from __future__ import annotations

import os
from pathlib import Path

import pytest

from docmergeforge.core.models import MergeProject
from docmergeforge.project.sync import ProjectSyncPlan

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import (  # noqa: E402
    QApplication,
    QDialog,
    QDialogButtonBox,
    QMessageBox,
    QPushButton,
)

from docmergeforge.ui import desktop_entry  # noqa: E402
from docmergeforge.ui import main as ui_main  # noqa: E402
from docmergeforge.ui.project_sync_dialog import (  # noqa: E402
    ProjectSyncDialog,
    format_project_sync_plan,
)


@pytest.fixture(scope="module")
def qt_app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


def _plan(
    tmp_path: Path,
    *,
    removed: bool = False,
    duplicate_pdf_parts: tuple[int, ...] = (),
) -> ProjectSyncPlan:
    old = tmp_path / "Part 1.pdf"
    new = tmp_path / "Part 2.pdf"
    current = (old,) if removed else ()
    return ProjectSyncPlan(
        current=current,
        proposed=(new,),
        added=(new,),
        removed=(old,) if removed else (),
        reordered=False,
        duplicate_pdf_parts=duplicate_pdf_parts,
        duplicate_docx_parts=(),
        missing_pdf_parts=(),
        missing_docx_parts=(),
    )


def _unchanged_plan(tmp_path: Path) -> ProjectSyncPlan:
    selected = tmp_path / "Part 1.pdf"
    return ProjectSyncPlan(
        current=(selected,),
        proposed=(selected,),
        added=(),
        removed=(),
        reordered=False,
        duplicate_pdf_parts=(),
        duplicate_docx_parts=(),
        missing_pdf_parts=(),
        missing_docx_parts=(),
    )


@pytest.mark.integration
def test_project_sync_window_exposes_accessible_action(
    qt_app: QApplication,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del qt_app
    monkeypatch.setattr(ui_main, "settings_path", lambda: tmp_path / "settings.json")
    monkeypatch.setattr(ui_main, "recent_projects_path", lambda: tmp_path / "recent.json")
    monkeypatch.setattr(ui_main, "recovery_dir", lambda: tmp_path / "recovery")

    window = desktop_entry.ProjectSyncMainWindow()
    buttons = window.findChildren(QPushButton)
    sync_buttons = [item for item in buttons if item.accessibleName() == "Synchronize project sources"]

    assert len(sync_buttons) == 1
    assert sync_buttons[0].accessibleDescription()
    window.close()


@pytest.mark.integration
def test_project_sync_dialog_exposes_complete_review_and_apply_state(
    qt_app: QApplication,
    tmp_path: Path,
) -> None:
    del qt_app
    plan = _plan(tmp_path, removed=True)
    project_path = tmp_path / "Book.json"
    dialog = ProjectSyncDialog(project_path, plan)

    apply_button = dialog.buttons.button(QDialogButtonBox.StandardButton.Save)
    assert dialog.accessibleName() == "Synchronize project sources"
    assert dialog.preview.accessibleName() == "Project synchronization preview"
    assert apply_button.isEnabled()
    assert apply_button.accessibleName() == "Apply project source synchronization"

    text = format_project_sync_plan(project_path, plan)
    assert f"Project: {project_path}" in text
    assert "Added to selected_files" in text
    assert "Removed from selected_files" in text
    assert "Synchronization changes only project metadata" in text
    dialog.close()


@pytest.mark.integration
def test_project_sync_dialog_blocks_ambiguous_duplicate_parts(
    qt_app: QApplication,
    tmp_path: Path,
) -> None:
    del qt_app
    plan = _plan(tmp_path, duplicate_pdf_parts=(2,))
    dialog = ProjectSyncDialog(tmp_path / "Book.json", plan)

    apply_button = dialog.buttons.button(QDialogButtonBox.StandardButton.Save)
    assert not plan.safe_to_apply
    assert not apply_button.isEnabled()
    assert "cannot be applied" in dialog.guidance.text().lower()
    dialog.close()


@pytest.mark.integration
def test_desktop_sync_requires_removal_approval_and_carries_revision(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project_path = tmp_path / "Book.json"
    project = MergeProject("Book", [tmp_path / "source"], tmp_path / "output")
    plan = _plan(tmp_path, removed=True)
    project.selected_files = list(plan.current)
    events: list[str] = []

    monkeypatch.setattr(
        desktop_entry.QFileDialog,
        "getOpenFileName",
        lambda *_args, **_kwargs: (str(project_path), ""),
    )
    monkeypatch.setattr(
        desktop_entry,
        "load_project_snapshot",
        lambda _path: (project, "revision-123"),
    )
    monkeypatch.setattr(desktop_entry, "plan_project_sync", lambda _project: plan)

    class AcceptedDialog:
        DialogCode = QDialog.DialogCode

        def __init__(self, path: Path, proposed: ProjectSyncPlan) -> None:
            assert path == project_path
            assert proposed is plan

        def exec(self) -> int:
            events.append("preview-approved")
            return int(QDialog.DialogCode.Accepted)

    monkeypatch.setattr(desktop_entry, "ProjectSyncDialog", AcceptedDialog)

    def approve_removals(*_args: object, **_kwargs: object) -> QMessageBox.StandardButton:
        events.append("removals-approved")
        return QMessageBox.StandardButton.Yes

    monkeypatch.setattr(desktop_entry.QMessageBox, "question", approve_removals)
    monkeypatch.setattr(
        desktop_entry.QMessageBox,
        "information",
        lambda *_args, **_kwargs: events.append("success-dialog"),
    )

    def apply_sync(
        saved_project: MergeProject,
        path: Path,
        proposed: ProjectSyncPlan,
        *,
        expected_revision: str | None = None,
    ) -> Path:
        assert saved_project is project
        assert path == project_path
        assert proposed is plan
        assert expected_revision == "revision-123"
        events.append("applied")
        saved_project.selected_files = list(proposed.proposed)
        return tmp_path / "Book.json.bak"

    monkeypatch.setattr(desktop_entry, "apply_project_sync", apply_sync)

    class FakeStatusBar:
        def showMessage(self, _message: str, _timeout: int = 0) -> None:
            events.append("status")

    class FakeLogger:
        def info(self, *_args: object) -> None:
            events.append("logged")

    class FakeWindow:
        logger = FakeLogger()
        bar = FakeStatusBar()

        def statusBar(self) -> FakeStatusBar:
            return self.bar

        def _record_error(self, _message: str) -> None:
            events.append("error")

        def _remember_project(self, saved_project: MergeProject, path: Path) -> None:
            assert saved_project is project
            assert path == project_path
            events.append("remembered")

    desktop_entry.ProjectSyncMainWindow._synchronize_project(FakeWindow())

    assert events.index("preview-approved") < events.index("removals-approved")
    assert events.index("removals-approved") < events.index("applied")
    assert "remembered" in events
    assert "success-dialog" in events
    assert "error" not in events


@pytest.mark.integration
def test_desktop_sync_declined_removals_do_not_write_project(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project_path = tmp_path / "Book.json"
    project = MergeProject("Book", [tmp_path / "source"], tmp_path / "output")
    plan = _plan(tmp_path, removed=True)
    project.selected_files = list(plan.current)

    monkeypatch.setattr(
        desktop_entry.QFileDialog,
        "getOpenFileName",
        lambda *_args, **_kwargs: (str(project_path), ""),
    )
    monkeypatch.setattr(
        desktop_entry,
        "load_project_snapshot",
        lambda _path: (project, "revision-123"),
    )
    monkeypatch.setattr(desktop_entry, "plan_project_sync", lambda _project: plan)

    class AcceptedDialog:
        DialogCode = QDialog.DialogCode

        def __init__(self, _path: Path, _plan: ProjectSyncPlan) -> None:
            pass

        def exec(self) -> int:
            return int(QDialog.DialogCode.Accepted)

    monkeypatch.setattr(desktop_entry, "ProjectSyncDialog", AcceptedDialog)
    monkeypatch.setattr(
        desktop_entry.QMessageBox,
        "question",
        lambda *_args, **_kwargs: QMessageBox.StandardButton.No,
    )

    def unexpected_apply(*_args: object, **_kwargs: object) -> Path:
        raise AssertionError("apply_project_sync must not run after removal approval is declined")

    monkeypatch.setattr(desktop_entry, "apply_project_sync", unexpected_apply)

    class FakeStatusBar:
        def __init__(self) -> None:
            self.messages: list[str] = []

        def showMessage(self, message: str, _timeout: int = 0) -> None:
            self.messages.append(message)

    class FakeWindow:
        bar = FakeStatusBar()

        def statusBar(self) -> FakeStatusBar:
            return self.bar

        def _record_error(self, _message: str) -> None:
            raise AssertionError("no error should be recorded for an intentional cancellation")

    window = FakeWindow()
    desktop_entry.ProjectSyncMainWindow._synchronize_project(window)

    assert window.bar.messages[-1] == "Project synchronization cancelled."


@pytest.mark.integration
def test_desktop_sync_unchanged_plan_is_noop(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project_path = tmp_path / "Book.json"
    project = MergeProject("Book", [tmp_path / "source"], tmp_path / "output")
    plan = _unchanged_plan(tmp_path)
    project.selected_files = list(plan.current)

    monkeypatch.setattr(
        desktop_entry.QFileDialog,
        "getOpenFileName",
        lambda *_args, **_kwargs: (str(project_path), ""),
    )
    monkeypatch.setattr(
        desktop_entry,
        "load_project_snapshot",
        lambda _path: (project, "revision-123"),
    )
    monkeypatch.setattr(desktop_entry, "plan_project_sync", lambda _project: plan)

    class ClosedDialog:
        DialogCode = QDialog.DialogCode

        def __init__(self, _path: Path, _plan: ProjectSyncPlan) -> None:
            pass

        def exec(self) -> int:
            return int(QDialog.DialogCode.Rejected)

    monkeypatch.setattr(desktop_entry, "ProjectSyncDialog", ClosedDialog)

    def unexpected_apply(*_args: object, **_kwargs: object) -> Path:
        raise AssertionError("unchanged synchronization must not write the project")

    monkeypatch.setattr(desktop_entry, "apply_project_sync", unexpected_apply)

    class FakeStatusBar:
        def __init__(self) -> None:
            self.messages: list[str] = []

        def showMessage(self, message: str, _timeout: int = 0) -> None:
            self.messages.append(message)

    class FakeWindow:
        bar = FakeStatusBar()

        def statusBar(self) -> FakeStatusBar:
            return self.bar

        def _record_error(self, _message: str) -> None:
            raise AssertionError("unchanged synchronization is not an error")

    window = FakeWindow()
    desktop_entry.ProjectSyncMainWindow._synchronize_project(window)

    assert window.bar.messages[-1] == "Project sources are already synchronized."


@pytest.mark.integration
def test_desktop_sync_surfaces_stale_revision_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project_path = tmp_path / "Book.json"
    project = MergeProject("Book", [tmp_path / "source"], tmp_path / "output")
    plan = _plan(tmp_path)
    errors: list[str] = []

    monkeypatch.setattr(
        desktop_entry.QFileDialog,
        "getOpenFileName",
        lambda *_args, **_kwargs: (str(project_path), ""),
    )
    monkeypatch.setattr(
        desktop_entry,
        "load_project_snapshot",
        lambda _path: (project, "revision-123"),
    )
    monkeypatch.setattr(desktop_entry, "plan_project_sync", lambda _project: plan)

    class AcceptedDialog:
        DialogCode = QDialog.DialogCode

        def __init__(self, _path: Path, _plan: ProjectSyncPlan) -> None:
            pass

        def exec(self) -> int:
            return int(QDialog.DialogCode.Accepted)

    monkeypatch.setattr(desktop_entry, "ProjectSyncDialog", AcceptedDialog)

    def stale_apply(*_args: object, **_kwargs: object) -> Path:
        raise ValueError("project changed on disk")

    monkeypatch.setattr(desktop_entry, "apply_project_sync", stale_apply)
    monkeypatch.setattr(
        desktop_entry.QMessageBox,
        "critical",
        lambda _parent, _title, message: errors.append(message),
    )

    class FakeStatusBar:
        def showMessage(self, _message: str, _timeout: int = 0) -> None:
            pass

    class FakeWindow:
        bar = FakeStatusBar()

        def statusBar(self) -> FakeStatusBar:
            return self.bar

        def _record_error(self, message: str) -> None:
            errors.append(message)

    desktop_entry.ProjectSyncMainWindow._synchronize_project(FakeWindow())

    assert errors == ["project changed on disk", "project changed on disk"]
