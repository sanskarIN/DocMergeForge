from __future__ import annotations

import json
import platform
from datetime import UTC, datetime
from pathlib import Path

from docmergeforge import __version__


def export_diagnostics(path: Path, warnings: list[str], recent_errors: list[str]) -> Path:
    payload = {
        "app_version": __version__,
        "generated_at": datetime.now(UTC).isoformat(),
        "platform": platform.platform(),
        "warnings": warnings,
        "recent_errors": recent_errors,
        "privacy_note": "Document body text and passwords are intentionally excluded.",
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path
