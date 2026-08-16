from __future__ import annotations

from pathlib import Path


def verify_pdf_password(path: Path, password: str) -> bool:
    """Verify a PDF password without persisting or logging it."""
    from pypdf import PdfReader

    reader = PdfReader(str(path), strict=False)
    if not reader.is_encrypted:
        return True
    try:
        result = reader.decrypt(password)
    except Exception:
        return False
    return bool(result)
