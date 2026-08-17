from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
)

from docmergeforge.core.models import DocumentKind, InputDocument
from docmergeforge.ordering.editor import OrderEditor
from docmergeforge.validation.service import validate_part_set


class OrderEditorDialog(QDialog):
    """Keyboard- and drag/drop-friendly confirmation of the final document sequence."""

    def __init__(
        self,
        documents: list[InputDocument],
        expected_start: int,
        expected_end: int,
        *,
        allow_manual_order: bool = True,
    ) -> None:
        super().__init__()
        self.setWindowTitle("Confirm File Order")
        self.setAccessibleName("Confirm file order")
        self.resize(920, 680)
        self.editor = OrderEditor(list(documents))
        self.expected_start = expected_start
        self.expected_end = expected_end
        self._refreshing = False

        if not allow_manual_order:
            self.editor.sort_by_part()
            self.editor.locked = True

        layout = QVBoxLayout(self)
        intro = QLabel(
            "Confirm the final document sequence before merge. PDF and DOCX are still "
            "merged independently; companion code is never included in this list."
        )
        intro.setAccessibleName("File order instructions")
        intro.setWordWrap(True)
        layout.addWidget(intro)

        search_row = QHBoxLayout()
        self.search_label = QLabel("&Search")
        self.search_label.setAccessibleName("Search file order label")
        search_row.addWidget(self.search_label)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Filter by filename, format, or part number")
        self.search.setAccessibleName("Filter file order")
        self.search.setAccessibleDescription(
            "Type part numbers, filenames, or formats to filter the order list."
        )
        self.search_label.setBuddy(self.search)
        self.search.textChanged.connect(self._apply_filter)
        search_row.addWidget(self.search, 1)
        self.lock = QCheckBox("Lock order")
        self.lock.setAccessibleName("Lock file order")
        self.lock.setAccessibleDescription(
            "Prevents drag-and-drop and manual order changes while enabled."
        )
        self.lock.setShortcut(QKeySequence("Alt+L"))
        self.lock.setChecked(self.editor.locked)
        self.lock.setEnabled(allow_manual_order)
        self.lock.toggled.connect(self._set_locked)
        search_row.addWidget(self.lock)
        layout.addLayout(search_row)

        self.list = QListWidget()
        self.list.setAccessibleName("Final merge document order")
        self.list.setAccessibleDescription(
            "The ordered PDF and DOCX documents. Select a row before using move commands."
        )
        self.list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.list.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.list.setDragEnabled(allow_manual_order)
        self.list.setAcceptDrops(allow_manual_order)
        self.list.setDropIndicatorShown(allow_manual_order)
        self.list.currentRowChanged.connect(self._update_boundary)
        self.list.model().rowsMoved.connect(self._on_rows_moved)
        layout.addWidget(self.list, 1)

        controls = QGridLayout()
        self._manual_buttons: list[QPushButton] = []
        definitions = [
            ("Part ↑", "Alt+1", lambda: self._sort_part(False), 0, 0),
            ("Part ↓", "Alt+2", lambda: self._sort_part(True), 0, 1),
            ("Filename ↑", "Alt+3", lambda: self._sort_filename(False), 0, 2),
            ("Filename ↓", "Alt+4", lambda: self._sort_filename(True), 0, 3),
            ("Move Up", "Alt+Up", self._move_up, 1, 0),
            ("Move Down", "Alt+Down", self._move_down, 1, 1),
            ("Move Top", "Alt+Home", self._move_top, 1, 2),
            ("Move Bottom", "Alt+End", self._move_bottom, 1, 3),
            ("Undo", "Ctrl+Z", self._undo, 2, 0),
            ("Redo", "Ctrl+Y", self._redo, 2, 1),
            ("Restore Auto Order", "Ctrl+Shift+R", self._restore_auto, 2, 2),
        ]
        for label, shortcut, callback, row, column in definitions:
            button = QPushButton(label)
            button.setAccessibleName(label.replace("↑", "ascending").replace("↓", "descending"))
            button.setAccessibleDescription(f"Keyboard shortcut: {shortcut}")
            button.setShortcut(QKeySequence(shortcut))
            button.setToolTip(f"{label} ({shortcut})")
            button.clicked.connect(callback)
            controls.addWidget(button, row, column)
            self._manual_buttons.append(button)
        layout.addLayout(controls)

        self.validation = QLabel()
        self.validation.setWordWrap(True)
        self.validation.setAccessibleName("Order validation summary")
        layout.addWidget(self.validation)

        self.boundary = QLabel("Select a document to preview its adjacent boundaries.")
        self.boundary.setWordWrap(True)
        self.boundary.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.boundary.setAccessibleName("Adjacent boundary preview")
        layout.addWidget(self.boundary)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok
        )
        ok_button = self.buttons.button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setText("Confirm Order")
        ok_button.setAccessibleName("Confirm file order")
        cancel_button = self.buttons.button(QDialogButtonBox.StandardButton.Cancel)
        cancel_button.setAccessibleName("Cancel file order changes")
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

        self._refresh_list()
        self._set_locked(self.editor.locked)
        if self.list.count():
            self.list.setCurrentRow(0)

    def ordered_paths(self) -> list[Path]:
        return [item.path for item in self.editor.items]

    def _item_text(self, item: InputDocument) -> str:
        part = item.part.number
        part_text = f"Part {part}" if part is not None else "Unnumbered"
        return f"{part_text}  [{item.kind.value.upper()}]  {item.path.name}"

    def _refresh_list(self, selected_path: Path | None = None) -> None:
        self._refreshing = True
        self.list.clear()
        selected_row = -1
        for index, document in enumerate(self.editor.items):
            list_item = QListWidgetItem(self._item_text(document))
            list_item.setData(Qt.ItemDataRole.UserRole, str(document.path))
            list_item.setToolTip(str(document.path))
            self.list.addItem(list_item)
            if selected_path is not None and document.path == selected_path:
                selected_row = index
        self._refreshing = False
        self._apply_filter(self.search.text())
        self._update_validation()
        if selected_row >= 0:
            self.list.setCurrentRow(selected_row)

    def _paths_from_list(self) -> list[Path]:
        return [
            Path(str(self.list.item(index).data(Qt.ItemDataRole.UserRole)))
            for index in range(self.list.count())
        ]

    def _on_rows_moved(self, *_args: object) -> None:
        if self._refreshing or self.editor.locked:
            return
        current = self.list.currentItem()
        selected_path = (
            Path(str(current.data(Qt.ItemDataRole.UserRole))) if current is not None else None
        )
        self.editor.set_order(self._paths_from_list())
        self._update_validation()
        if selected_path is not None:
            for index, item in enumerate(self.editor.items):
                if item.path == selected_path:
                    self.list.setCurrentRow(index)
                    break

    def _apply_filter(self, query: str) -> None:
        needle = query.casefold().strip()
        for index in range(self.list.count()):
            item = self.list.item(index)
            path = str(item.data(Qt.ItemDataRole.UserRole))
            item.setHidden(bool(needle) and needle not in f"{item.text()} {path}".casefold())

    def _set_locked(self, checked: bool) -> None:
        self.editor.locked = checked
        self.list.setDragEnabled(not checked)
        self.list.setAcceptDrops(not checked)
        self.list.setDropIndicatorShown(not checked)
        for button in self._manual_buttons:
            button.setEnabled(not checked)

    def _selected_index(self) -> int:
        return self.list.currentRow()

    def _sort_part(self, descending: bool) -> None:
        self.editor.sort_by_part(descending)
        self._refresh_list()

    def _sort_filename(self, descending: bool) -> None:
        self.editor.sort_by_filename(descending)
        self._refresh_list()

    def _move_up(self) -> None:
        index = self._selected_index()
        if index <= 0:
            return
        path = self.editor.items[index].path
        self.editor.move_up(index)
        self._refresh_list(path)

    def _move_down(self) -> None:
        index = self._selected_index()
        if index < 0 or index >= len(self.editor.items) - 1:
            return
        path = self.editor.items[index].path
        self.editor.move_down(index)
        self._refresh_list(path)

    def _move_top(self) -> None:
        index = self._selected_index()
        if index <= 0:
            return
        path = self.editor.items[index].path
        self.editor.move_to_top(index)
        self._refresh_list(path)

    def _move_bottom(self) -> None:
        index = self._selected_index()
        if index < 0 or index >= len(self.editor.items) - 1:
            return
        path = self.editor.items[index].path
        self.editor.move_to_bottom(index)
        self._refresh_list(path)

    def _undo(self) -> None:
        if self.editor.undo():
            self._refresh_list()

    def _redo(self) -> None:
        if self.editor.redo():
            self._refresh_list()

    def _restore_auto(self) -> None:
        self.editor.sort_by_part()
        self._refresh_list()

    def _update_validation(self) -> None:
        summaries: list[str] = []
        for kind in (DocumentKind.PDF, DocumentKind.DOCX):
            matching = [item for item in self.editor.items if item.kind == kind]
            if not matching:
                summaries.append(f"{kind.value.upper()}: not selected")
                continue
            result = validate_part_set(
                matching,
                kind,
                self.expected_start,
                self.expected_end,
            )
            missing = ", ".join(str(value) for value in result.missing_parts[:8]) or "none"
            if len(result.missing_parts) > 8:
                missing += ", …"
            duplicates = ", ".join(str(value) for value in result.duplicate_parts) or "none"
            summaries.append(
                f"{kind.value.upper()}: {len(matching)} file(s), missing {missing}, "
                f"duplicates {duplicates}"
            )
        self.validation.setText(" | ".join(summaries))

    def _update_boundary(self, index: int) -> None:
        if index < 0 or index >= len(self.editor.items):
            self.boundary.setText("Select a document to preview its adjacent boundaries.")
            return
        current = self.editor.items[index]
        before, after = self.editor.adjacent(index)
        before_text = before.path.name if before is not None else "START OF BOOK"
        after_text = after.path.name if after is not None else "END OF BOOK"
        self.boundary.setText(
            f"Boundary preview: {before_text}  →  {current.path.name}  →  {after_text}"
        )