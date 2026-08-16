from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
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
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.list = QListWidget()
        self.list.setAccessibleName("Project source folders and files")
        self.list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        layout.addWidget(self.list)

        controls = QHBoxLayout()
        add_folder = QPushButton("Add Folder…")
        add_folder.clicked.connect(self._add_folder)
        add_files = QPushButton("Add Files…")
        add_files.clicked.connect(self._add_files)
        remove = QPushButton("Remove Selected")
        remove.clicked.connect(self._remove_selected)
        clear = QPushButton("Clear")
        clear.clicked.connect(self.list.clear)
        controls.addWidget(add_folder)
        controls.addWidget(add_files)
        controls.addWidget(remove)
        controls.addWidget(clear)
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
