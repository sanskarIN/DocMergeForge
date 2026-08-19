from __future__ import annotations

import os
from pathlib import Path
from types import SimpleNamespace

import pytest

from docmergeforge.core.models import DocumentKind, InputDocument, MergeProject, PartIdentity

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QDialogButtonBox  # noqa: E402

from docmergeforge.ui import main as ui_main  # noqa: E402
from docmergeforge.ui.order_dialog import OrderEditorDialog  # noqa: E402


def _document(path: Path, part: int) -> InputDocument:
    return InputDocument(
        path,
        DocumentKind.PDF,
        PartIdentity(part, f"Part {part}"),
        1,
        f"{part:064x}",
        1,
    )


@pytest.fixture(scope="module")
def qt_app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


@pytest.mark.integration
def test_order_editor_exposes_labels_descriptions_and_shortcuts(
    qt_app: QApplication,
    tmp_path: Path,
) -> None:
    del qt_app
    documents = [
        _document(tmp_path / "Part 1.pdf", 1),
        _document(tmp_path / "Part 2.pdf", 2),
    ]
    dialog = OrderEditorDialog(documents, 1, 2)

    assert dialog.accessibleName() == "Confirm file order"
    assert dialog.search_label.buddy() is dialog.search
    assert dialog.search.accessibleName()
    assert dialog.search.accessibleDescription()
    assert dialog.lock.accessibleName()
    assert not dialog.lock.shortcut().isEmpty()
    assert dialog.list.accessibleName()
    assert dialog.list.accessibleDescription()
    assert dialog.validation.accessibleName()
    assert dialog.boundary.accessibleName()

    for button in dialog._manual_buttons:
        assert button.accessibleName()
        assert button.accessibleDescription()
        assert not button.shortcut().isEmpty()

    confirm = dialog.buttons.button(QDialogButtonBox.StandardButton.Ok)
    cancel = dialog.buttons.button(QDialogButtonBox.StandardButton.Cancel)
    assert confirm.accessibleName() == "Confirm file order"
    assert cancel.accessibleName() == "Cancel file order changes"

    dialog.close()


@pytest.mark.integration
def test_resume_project_checkpoints_only_after_guarded_save(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project_path = tmp_path / "Book.json"
    project = MergeProject("Book", [tmp_path / "source"], tmp_path / "output")
    events: list[str] = []

    monkeypatch.setattr(
        ui_main.QFileDialog,
        "getOpenFileName",
        lambda *_args, **_kwargs: (str(project_path), ""),
    )
    monkeypatch.setattr(
        ui_main,
        "load_project_snapshot",
        lambda _path: (project, "revision"),
    )

    def guarded_save(
        saved_project: MergeProject,
        path: Path,
        revision: str,
    ) -> None:
        assert saved_project is project
        assert path == project_path
        assert revision == "revision"
        events.append("guarded-save")

    monkeypatch.setattr(ui_main, "save_project_if_revision", guarded_save)

    fake_window = SimpleNamespace()
    fake_window._record_error = lambda _message: None

    def confirm_order(
        confirmed_project: MergeProject,
        *,
        checkpoint: bool = True,
    ) -> bool:
        assert confirmed_project is project
        assert checkpoint is False
        events.append("order-confirmed")
        return True

    def checkpoint(checked_project: MergeProject, name: str) -> bool:
        assert checked_project is project
        assert name == "ordering"
        events.append("checkpoint")
        return True

    fake_window._confirm_project_order = confirm_order
    fake_window._checkpoint_project = checkpoint
    fake_window._remember_project = lambda *_args: events.append("remember")
    fake_window._run_project = lambda *_args: events.append("run")

    ui_main.MainWindow._resume_project(fake_window)

    assert events == ["order-confirmed", "guarded-save", "checkpoint", "remember", "run"]
