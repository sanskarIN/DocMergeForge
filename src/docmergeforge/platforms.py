from __future__ import annotations

import os
import platform
import sys
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(slots=True, frozen=True)
class PlatformTarget:
    """Document one supported user-facing platform target."""

    id: str
    label: str
    native_desktop: bool
    cli: bool
    web_client: bool
    delivery: str
    notes: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


_TARGETS: tuple[PlatformTarget, ...] = (
    PlatformTarget(
        "windows",
        "Windows 10/11",
        True,
        True,
        True,
        "PyInstaller desktop app, Python CLI, or browser",
        "Native desktop builds are produced on Windows.",
    ),
    PlatformTarget(
        "macos",
        "macOS",
        True,
        True,
        True,
        "PyInstaller desktop app, Python CLI, or browser",
        "Native desktop builds are produced on macOS; release signing/notarization is separate.",
    ),
    PlatformTarget(
        "linux",
        "Linux",
        True,
        True,
        True,
        "PyInstaller desktop app, Python CLI, or browser",
        "Desktop Qt runtime libraries can vary by distribution.",
    ),
    PlatformTarget(
        "android",
        "Android",
        False,
        False,
        True,
        "Responsive web client",
        "Use a modern browser against a DocMergeForge web host; no APK is claimed.",
    ),
    PlatformTarget(
        "ios",
        "iPhone (iOS)",
        False,
        False,
        True,
        "Responsive web client",
        "Use Safari or another modern browser against a DocMergeForge web host; no IPA is claimed.",
    ),
    PlatformTarget(
        "ipados",
        "iPad (iPadOS)",
        False,
        False,
        True,
        "Responsive web client",
        "Uses the same responsive browser interface as iOS.",
    ),
    PlatformTarget(
        "chromeos",
        "ChromeOS",
        False,
        False,
        True,
        "Responsive web client",
        "Runs in a modern browser; Linux container use is optional rather than required.",
    ),
    PlatformTarget(
        "web",
        "Modern web browsers",
        False,
        False,
        True,
        "Responsive web client",
        "The browser is a client; PDF/DOCX processing remains on the Python host.",
    ),
)


def support_matrix() -> tuple[PlatformTarget, ...]:
    """Return the maintained platform-support matrix."""

    return _TARGETS


def current_runtime() -> dict[str, object]:
    """Return privacy-safe runtime details for diagnostics and the web status endpoint."""

    if hasattr(sys, "getandroidapilevel") or "ANDROID_ROOT" in os.environ:
        platform_id = "android"
    elif sys.platform == "ios":
        platform_id = "ios"
    elif sys.platform == "win32":
        platform_id = "windows"
    elif sys.platform == "darwin":
        platform_id = "macos"
    elif sys.platform.startswith("linux"):
        platform_id = "linux"
    elif sys.platform in {"emscripten", "wasi"}:
        platform_id = "web-runtime"
    else:
        platform_id = "other"

    return {
        "platform": platform_id,
        "system": platform.system() or "unknown",
        "machine": platform.machine() or "unknown",
        "python": platform.python_version(),
    }
