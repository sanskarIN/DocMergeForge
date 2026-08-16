from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout


class FirstRunDialog(QDialog):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Welcome to DocMergeForge")
        self.setMinimumWidth(560)
        layout = QVBoxLayout(self)

        title = QLabel("<h2>Welcome to DocMergeForge</h2><p><b>Made by the Sanskar</b></p>")
        title.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(title)

        message = QLabel(
            "<p><b>Local-first privacy:</b> document content stays on this device by default.</p>"
            "<p><b>Original safety:</b> source manuscripts are never intentionally overwritten.</p>"
            "<p><b>Separate pipelines:</b> PDF and DOCX files are merged independently.</p>"
            "<p><b>Companion-code guarantee:</b> code packages remain separate and are never "
            "combined into the books.</p>"
            "<p><b>SQL Full Mastery:</b> a dedicated 120-Part preset is available from the home "
            "screen.</p>"
            "<p>No account is required to use the local application.</p>"
        )
        message.setTextFormat(Qt.TextFormat.RichText)
        message.setWordWrap(True)
        message.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(message)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Continue")
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)
