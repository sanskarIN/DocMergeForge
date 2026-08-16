from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from docmergeforge.app.service import MergeApplicationService
from docmergeforge.presets.sql_full_mastery import create_sql_full_mastery_project
from docmergeforge.ui.about_dialog import AboutDialog


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("DocMergeForge")
        self.resize(1040, 700)
        self.setAcceptDrops(True)
        root = QWidget()
        outer = QVBoxLayout(root)

        heading = QLabel(
            "<h1>DocMergeForge</h1>"
            "<p>Discover correctly. Order correctly. Merge safely. Validate everything.</p>"
        )
        heading.setTextFormat(Qt.TextFormat.RichText)
        outer.addWidget(heading)

        grid = QGridLayout()
        actions = [
            ("New Merge Project", self._not_yet),
            ("Merge PDFs", self._not_yet),
            ("Merge DOCX", self._not_yet),
            ("SQL Full Mastery 120-Part Preset", self._sql_preset),
            ("Validate Files", self._not_yet),
            ("Publication Audit", self._not_yet),
            ("Compare Output with Inputs", self._not_yet),
            ("Resume Project", self._not_yet),
            ("Recent Projects", self._not_yet),
            ("Settings", self._not_yet),
            ("Help", self._not_yet),
            ("About", self._about),
        ]
        for index, (label, callback) in enumerate(actions):
            button = QPushButton(label)
            button.setMinimumHeight(54)
            button.clicked.connect(callback)
            grid.addWidget(button, index // 3, index % 3)
        outer.addLayout(grid)

        support_row = QHBoxLayout()
        support_row.addWidget(QLabel("<b>Made by the Sanskar</b>"))
        support_row.addStretch(1)
        bmc = QPushButton("☕ Buy Me a Coffee")
        bmc.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl("https://buymeacoffee.com/sanskarIN"))
        )
        support_row.addWidget(bmc)
        outer.addLayout(support_row)

        self.setCentralWidget(root)
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Local-first. Originals are never overwritten.")

    def _about(self) -> None:
        AboutDialog().exec()

    def _not_yet(self) -> None:
        QMessageBox.information(
            self,
            "DocMergeForge",
            "This screen is wired into the architecture, while the guided SQL preset "
            "is the primary v0.1 workflow.",
        )

    def _sql_preset(self) -> None:
        source = QFileDialog.getExistingDirectory(
            self,
            "Select root folder containing Parts 1–120",
        )
        if not source:
            return
        output = QFileDialog.getExistingDirectory(self, "Select output folder")
        if not output:
            return
        project = create_sql_full_mastery_project(Path(source), Path(output))
        service = MergeApplicationService()
        try:
            dry = service.dry_run(project)
            if not dry.pdf.ready or not dry.docx.ready:
                QMessageBox.warning(
                    self,
                    "Validation required",
                    f"PDF ready: {dry.pdf.ready}\nDOCX ready: {dry.docx.ready}\n"
                    "Resolve missing or duplicate parts before merge.",
                )
                return
            service.run_sql_preset(project)
            QMessageBox.information(
                self,
                "Complete",
                f"Validated outputs created in:\n{output}",
            )
        except Exception as exc:
            QMessageBox.critical(self, "Merge failed safely", str(exc))


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("DocMergeForge")
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
