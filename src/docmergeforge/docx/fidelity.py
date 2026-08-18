from __future__ import annotations

from dataclasses import dataclass

from docmergeforge.core.exceptions import ValidationError
from docmergeforge.docx.libreoffice import find_libreoffice
from docmergeforge.docx.word import find_word_powershell_host


@dataclass(slots=True, frozen=True)
class FidelityCapability:
    mode: str
    available: bool
    production_ready: bool
    detail: str
    automation_ready: bool = False
    executable: str | None = None


def fidelity_capabilities() -> list[FidelityCapability]:
    libreoffice_executable = find_libreoffice()
    word_host = find_word_powershell_host()
    return [
        FidelityCapability(
            mode="portable",
            available=True,
            production_ready=True,
            detail="Portable OOXML merge engine bundled with DocMergeForge.",
            automation_ready=True,
        ),
        FidelityCapability(
            mode="libreoffice",
            available=libreoffice_executable is not None,
            production_ready=False,
            detail=(
                f"LibreOffice detected at {libreoffice_executable}. Explicit round-trip "
                "automation is available for fidelity acceptance, but production merge "
                "fidelity is not yet certified."
                if libreoffice_executable
                else "LibreOffice was not detected on PATH."
            ),
            automation_ready=libreoffice_executable is not None,
            executable=libreoffice_executable,
        ),
        FidelityCapability(
            mode="word",
            available=word_host is not None,
            production_ready=False,
            detail=(
                "Windows PowerShell automation host detected. Word COM availability is "
                "verified only when the explicit adapter runs; production merge fidelity "
                "is not yet certified."
                if word_host
                else "Microsoft Word automation requires Windows PowerShell and installed Word."
            ),
            automation_ready=word_host is not None,
            executable=word_host,
        ),
    ]


def fidelity_capability(mode: str) -> FidelityCapability:
    capabilities = {item.mode: item for item in fidelity_capabilities()}
    capability = capabilities.get(mode)
    if capability is None:
        raise ValidationError(f"Unknown DOCX fidelity mode: {mode}")
    return capability


def require_fidelity_automation(mode: str) -> FidelityCapability:
    capability = fidelity_capability(mode)
    if capability.automation_ready and capability.available:
        return capability
    raise ValidationError(f"DOCX fidelity automation '{mode}' is unavailable: {capability.detail}")


def require_production_fidelity(mode: str) -> None:
    capability = fidelity_capability(mode)
    if capability.production_ready:
        return
    if not capability.available:
        raise ValidationError(f"DOCX fidelity mode '{mode}' is unavailable: {capability.detail}")
    raise ValidationError(
        f"DOCX fidelity mode '{mode}' is not production-ready: {capability.detail} "
        "Choose portable mode instead of silently falling back."
    )
