from __future__ import annotations

import os
import sys
from pathlib import Path


def app_data_dir() -> Path:
    if sys.platform == "win32":
        root = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        return root / "DocMergeForge"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "DocMergeForge"
    root = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return root / "docmergeforge"


def settings_path() -> Path:
    return app_data_dir() / "settings.json"


def recent_projects_path() -> Path:
    return app_data_dir() / "recent-projects.json"


def recovery_dir() -> Path:
    return app_data_dir() / "recovery"
