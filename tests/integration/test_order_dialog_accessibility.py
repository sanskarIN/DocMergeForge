from __future__ import annotations

import os
from pathlib import Path

import pytest

from docmergeforge.core.models import DocumentKind, InputDocument, PartIdentity

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QDialogButtonBox  # noqa: E402

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
