from __future__ import annotations

import json
import platform
from datetime import UTC, datetime
from pathlib import Path

from docmergeforge import __version__
from docmergeforge.utilities.atomic import atomic_write_text


def export_diagnostics(path: Path, warnings: list[str], recent_errors: list[str]) -> Path:
    payload = {
        "app_version": __version__,
        "generated_at": datetime.now(UTC).isoformat(),
        "platform": platform.platform(),
        "warnings": warnings,
        "recent_errors": recent_errors,
        "privacy_note": "Document body text and passwords are intentionally excluded.",
    }
    atomic_write_text(path, json.dumps(payload, indent=2))
    return path
