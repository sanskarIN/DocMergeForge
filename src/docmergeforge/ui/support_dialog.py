from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from docmergeforge.diagnostics.export import export_diagnostics

_REPOSITORY = "https://github.com/sanskarIN/DocMergeForge"
_LINKS = {
    "Open Documentation": f"{_REPOSITORY}/tree/main/docs",
    "Report a Bug": f"{_REPOSITORY}/issues/new?template=bug_report.yml",
    "Request a Feature": f"{_REPOSITORY}/issues/new?template=feature_request.yml",
    "Open GitHub Repository": _REPOSITORY,
    "Business Email": "mailto:sanskarin@outlook.in",
    "Support Email": "mailto:supportramsandesh@gmail.com",
    "☕ Buy Me a Coffee": "https://buymeacoffee.com/sanskarIN",
}


class SupportDialog(QDialog):
    def __init__(
        self,
        warnings: list[str] | None = None,
        recent_errors: list[str] | None = None,
    ) -> None:
        super().__init__()
        self.setWindowTitle("DocMergeForge Support")
        self.setMinimumWidth(520)
        self._warnings = list(warnings or [])
        self._recent_errors = list(recent_errors or [])

        layout = QVBoxLayout(self)
        intro = QLabel(
            "Support tools are local-first. Exported diagnostics intentionally exclude document "
            "body text and passwords. Never publish sensitive manuscripts in a public issue."
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)

        export_button = QPushButton("Export Privacy-Safe Diagnostics")
        export_button.clicked.connect(self._export_diagnostics)
        layout.addWidget(export_button)

        for label, url in _LINKS.items():
            button = QPushButton(label)
            button.clicked.connect(
                lambda _checked=False, value=url: QDesktopServices.openUrl(QUrl(value))
            )
            layout.addWidget(button)

        close = QPushButton("Close")
        close.clicked.connect(self.accept)
        layout.addWidget(close)

    def _export_diagnostics(self) -> None:
        destination, _ = QFileDialog.getSaveFileName(
            self,
            "Export Diagnostics",
            "DocMergeForge_Diagnostics.json",
            "JSON (*.json)",
        )
        if not destination:
            return
        try:
            path = export_diagnostics(
                Path(destination),
                self._warnings,
                self._recent_errors,
            )
        except OSError as exc:
            QMessageBox.critical(self, "Diagnostics export failed", str(exc))
            return
        QMessageBox.information(self, "Diagnostics exported", str(path))
