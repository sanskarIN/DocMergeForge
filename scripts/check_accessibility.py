from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QDialogButtonBox, QWidget

from docmergeforge.core.models import DocumentKind, InputDocument, PartIdentity
from docmergeforge.ui.order_dialog import OrderEditorDialog


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


def main() -> int:
    app = QApplication.instance()
    if not isinstance(app, QApplication):
        app = QApplication([])

    dialog = OrderEditorDialog(
        [_sample_document(1), _sample_document(2)],
        1,
        2,
    )
    issues: list[str] = []

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

    dialog.close()
    app.processEvents()

    if issues:
        print("Desktop accessibility smoke failed:")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print(
        "Desktop accessibility smoke passed: order editor labels, descriptions, "
        "buddy navigation, and keyboard shortcuts are present."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
