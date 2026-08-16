from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QInputDialog, QLineEdit, QMessageBox, QWidget

from docmergeforge.core.models import DocumentKind, InputDocument
from docmergeforge.pdf.passwords import verify_pdf_password


def collect_pdf_passwords(
    parent: QWidget,
    documents: list[InputDocument],
) -> dict[Path, str] | None:
    """Collect and verify encrypted-PDF passwords only in process memory."""
    encrypted = [item for item in documents if item.kind == DocumentKind.PDF and item.encrypted]
    passwords: dict[Path, str] = {}
    for item in encrypted:
        while True:
            password, accepted = QInputDialog.getText(
                parent,
                "Encrypted PDF password required",
                f"Enter the password for:\n{item.path}",
                QLineEdit.EchoMode.Password,
            )
            if not accepted:
                passwords.clear()
                return None
            if verify_pdf_password(item.path, password):
                passwords[item.path] = password
                break
            QMessageBox.warning(
                parent,
                "Incorrect password",
                f"The password could not unlock {item.path.name}. Try again or cancel.",
            )
    return passwords
