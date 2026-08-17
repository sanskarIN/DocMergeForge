from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class SourcePicker(QWidget):
    """Collect multiple source folders and individual files without modifying them."""

    def __init__(self) -> None:
        super().__init__()
        self.setAccessibleName("Project sources")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.list = QListWidget()
        self.list.setAccessibleName("Project source folders and files")
        self.list.setAccessibleDescription(
            "Selected source folders and individual files. Multiple rows may be selected."
        )
        self.list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        layout.addWidget(self.list)

        controls = QHBoxLayout()
        self.add_folder_button = QPushButton("Add Folder…")
        self.add_folder_button.setAccessibleName("Add source folder")
        self.add_folder_button.setShortcut(QKeySequence("Ctrl+Shift+O"))
        self.add_folder_button.clicked.connect(self._add_folder)
        self.add_files_button = QPushButton("Add Files…")
        self.add_files_button.setAccessibleName("Add source files")
        self.add_files_button.setShortcut(QKeySequence("Ctrl+O"))
        self.add_files_button.clicked.connect(self._add_files)
        self.remove_button = QPushButton("Remove Selected")
        self.remove_button.setAccessibleName("Remove selected sources")
        self.remove_button.setShortcut(QKeySequence("Delete"))
        self.remove_button.clicked.connect(self._remove_selected)
        self.clear_button = QPushButton("Clear")
        self.clear_button.setAccessibleName("Clear all sources")
        self.clear_button.setShortcut(QKeySequence("Ctrl+Shift+Delete"))
        self.clear_button.clicked.connect(self.list.clear)
        controls.addWidget(self.add_folder_button)
        controls.addWidget(self.add_files_button)
        controls.addWidget(self.remove_button)
        controls.addWidget(self.clear_button)
        layout.addLayout(controls)

    def paths(self) -> list[Path]:
        return [
            Path(str(self.list.item(index).data(Qt.ItemDataRole.UserRole)))
            for index in range(self.list.count())
        ]

    def add_path(self, path: Path) -> None:
        normalized = path.expanduser()
        existing = {str(item).casefold() for item in self.paths()}
        if str(normalized).casefold() in existing:
            return
        item = QListWidgetItem(str(normalized))
        item.setData(Qt.ItemDataRole.UserRole, str(normalized))
        item.setToolTip(str(normalized))
        self.list.addItem(item)

    def _add_folder(self) -> None:
        selected = QFileDialog.getExistingDirectory(self, "Add source folder")
        if selected:
            self.add_path(Path(selected))

    def _add_files(self) -> None:
        selected, _ = QFileDialog.getOpenFileNames(
            self,
            "Add source files",
            "",
            "Supported Documents (*.pdf *.docx *.zip *.7z *.rar *.tar *.gz *.tgz);;All Files (*)",
        )
        for value in selected:
            self.add_path(Path(value))

    def _remove_selected(self) -> None:
        rows = sorted({self.list.row(item) for item in self.list.selectedItems()}, reverse=True)
        for row in rows:
            self.list.takeItem(row)