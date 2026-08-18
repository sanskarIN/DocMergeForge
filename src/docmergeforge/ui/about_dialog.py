from __future__ import annotations

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout

from docmergeforge.ui.resources import (
    APP_NAME,
    BMC_URL,
    BRAND,
    BUSINESS_EMAIL,
    BUSINESS_EMAIL_SECONDARY,
    GITHUB_PROFILE_URL,
    LINKEDIN_URL,
    REPOSITORY_URL,
    SUPPORT_EMAIL,
    X_URL,
    YOUTUBE_URL,
)

LINKS = {
    "GitHub": GITHUB_PROFILE_URL,
    "LinkedIn": LINKEDIN_URL,
    "Buy Me a Coffee": BMC_URL,
    "YouTube": YOUTUBE_URL,
    "X": X_URL,
    "Repository": REPOSITORY_URL,
}


class AboutDialog(QDialog):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"About {APP_NAME}")
        self.setMinimumWidth(430)
        layout = QVBoxLayout(self)
        title = QLabel(f"<h2>{APP_NAME}</h2><p><b>{BRAND}</b></p>")
        title.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(title)
        layout.addWidget(QLabel("Local-first document merging with source-integrity validation."))
        for label, url in LINKS.items():
            button = QPushButton(label)
            button.clicked.connect(
                lambda _checked=False, value=url: QDesktopServices.openUrl(QUrl(value))
            )
            layout.addWidget(button)
        layout.addWidget(QLabel(f"Business: {BUSINESS_EMAIL} · {BUSINESS_EMAIL_SECONDARY}"))
        layout.addWidget(QLabel(f"Support: {SUPPORT_EMAIL}"))
