from __future__ import annotations

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QPlainTextEdit, QVBoxLayout


class DryRunDialog(QDialog):
    def __init__(self, text: str, ready: bool) -> None:
        super().__init__()
        self.setWindowTitle("DocMergeForge Dry Run")
        self.resize(900, 680)
        layout = QVBoxLayout(self)

        heading = QLabel(
            "Review the detected files, final order, expected outputs, conflicts, and storage "
            "estimate before any final book is written."
        )
        heading.setWordWrap(True)
        layout.addWidget(heading)

        evidence = QPlainTextEdit()
        evidence.setReadOnly(True)
        evidence.setPlainText(text)
        evidence.setAccessibleName("Dry run evidence")
        layout.addWidget(evidence, 1)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok
        )
        continue_button = buttons.button(QDialogButtonBox.StandardButton.Ok)
        continue_button.setText("Continue to Merge")
        continue_button.setEnabled(ready)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
