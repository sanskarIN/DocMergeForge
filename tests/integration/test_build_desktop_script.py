from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def test_desktop_build_preflight_succeeds_for_repository() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/build_desktop.py", "--check"],
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "Desktop build configuration OK:" in result.stdout
