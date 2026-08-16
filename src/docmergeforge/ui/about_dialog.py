from __future__ import annotations

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout

LINKS = {
    "GitHub": "https://www.github.com/sanskarIN",
    "LinkedIn": "https://www.linkedin.com/in/sanskarIN",
    "Buy Me a Coffee": "https://buymeacoffee.com/sanskarIN",
    "YouTube": "https://youtube.com/@Sanskar-in",
    "X": "https://www.x.com/Sanskar_in",
    "Repository": "https://github.com/sanskarIN/DocMergeForge",
}


class AboutDialog(QDialog):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("About DocMergeForge")
        self.setMinimumWidth(430)
        layout = QVBoxLayout(self)
        title = QLabel("<h2>DocMergeForge</h2><p><b>Made by the Sanskar</b></p>")
        title.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(title)
        layout.addWidget(QLabel("Local-first document merging with source-integrity validation."))
        for label, url in LINKS.items():
            button = QPushButton(label)
            button.clicked.connect(lambda _checked=False, value=url: QDesktopServices.openUrl(QUrl(value)))
            layout.addWidget(button)
        layout.addWidget(QLabel("Business: sanskarin@outlook.in · sanskarin.business@gmail.com"))
        layout.addWidget(QLabel("Support: supportramsandesh@gmail.com"))
