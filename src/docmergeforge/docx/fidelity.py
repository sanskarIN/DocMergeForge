from __future__ import annotations

import shutil
import sys
from dataclasses import dataclass

from docmergeforge.core.exceptions import ValidationError


@dataclass(slots=True, frozen=True)
class FidelityCapability:
    mode: str
    available: bool
    production_ready: bool
    detail: str


def fidelity_capabilities() -> list[FidelityCapability]:
    libreoffice_executable = shutil.which("libreoffice") or shutil.which("soffice")
    word_detectable = sys.platform == "win32"
    return [
        FidelityCapability(
            mode="portable",
            available=True,
            production_ready=True,
            detail="Portable OOXML merge engine bundled with DocMergeForge.",
        ),
        FidelityCapability(
            mode="libreoffice",
            available=libreoffice_executable is not None,
            production_ready=False,
            detail=(
                f"LibreOffice detected at {libreoffice_executable}. "
                "High-fidelity merge automation is not yet production-ready."
                if libreoffice_executable
                else "LibreOffice was not detected on PATH."
            ),
        ),
        FidelityCapability(
            mode="word",
            available=word_detectable,
            production_ready=False,
            detail=(
                "Microsoft Word automation requires the Windows high-fidelity adapter, "
                "which is not yet production-ready."
            ),
        ),
    ]


def require_production_fidelity(mode: str) -> None:
    capabilities = {item.mode: item for item in fidelity_capabilities()}
    capability = capabilities.get(mode)
    if capability is None:
        raise ValidationError(f"Unknown DOCX fidelity mode: {mode}")
    if capability.production_ready:
        return
    if not capability.available:
        raise ValidationError(
            f"DOCX fidelity mode '{mode}' is unavailable: {capability.detail}"
        )
    raise ValidationError(
        f"DOCX fidelity mode '{mode}' is not production-ready: {capability.detail} "
        "Choose portable mode instead of silently falling back."
    )
