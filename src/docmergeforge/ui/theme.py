from __future__ import annotations

from PySide6.QtWidgets import QApplication

_DARK = """
QWidget { background: #111827; color: #f9fafb; }
QPushButton { background: #1f2937; border: 1px solid #4b5563; border-radius: 7px; padding: 8px; }
QPushButton:hover { background: #374151; }
QPushButton:focus { border: 2px solid #93c5fd; }
QLineEdit, QPlainTextEdit, QListWidget, QComboBox, QSpinBox {
    background: #0f172a; color: #f9fafb; border: 1px solid #6b7280; border-radius: 5px; padding: 5px;
}
QProgressBar { border: 1px solid #6b7280; border-radius: 5px; text-align: center; }
QProgressBar::chunk { background: #2563eb; }
"""

_LIGHT = """
QWidget { background: #ffffff; color: #111827; }
QPushButton { background: #f3f4f6; border: 1px solid #9ca3af; border-radius: 7px; padding: 8px; }
QPushButton:hover { background: #e5e7eb; }
QPushButton:focus { border: 2px solid #1d4ed8; }
QLineEdit, QPlainTextEdit, QListWidget, QComboBox, QSpinBox {
    background: #ffffff; color: #111827; border: 1px solid #6b7280; border-radius: 5px; padding: 5px;
}
QProgressBar { border: 1px solid #6b7280; border-radius: 5px; text-align: center; }
QProgressBar::chunk { background: #2563eb; }
"""


def apply_theme(app: QApplication, theme: str) -> None:
    if theme == "dark":
        app.setStyleSheet(_DARK)
    elif theme == "light":
        app.setStyleSheet(_LIGHT)
    else:
        app.setStyleSheet("")
