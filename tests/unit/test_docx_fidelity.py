import pytest

from docmergeforge.core.exceptions import ValidationError
from docmergeforge.docx import fidelity


def test_portable_fidelity_is_production_ready() -> None:
    capabilities = {item.mode: item for item in fidelity.fidelity_capabilities()}
    assert capabilities["portable"].available
    assert capabilities["portable"].automation_ready
    assert capabilities["portable"].production_ready
    fidelity.require_production_fidelity("portable")


def test_external_fidelity_never_silently_becomes_production_ready() -> None:
    for mode in ("libreoffice", "word"):
        with pytest.raises(ValidationError):
            fidelity.require_production_fidelity(mode)


def test_libreoffice_automation_can_be_available_without_production_claim(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(fidelity, "find_libreoffice", lambda: "/opt/libreoffice")
    monkeypatch.setattr(fidelity, "find_word_powershell_host", lambda: None)

    capability = fidelity.require_fidelity_automation("libreoffice")
    assert capability.available
    assert capability.automation_ready
    assert not capability.production_ready
    assert capability.executable == "/opt/libreoffice"


def test_unavailable_automation_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(fidelity, "find_libreoffice", lambda: None)
    monkeypatch.setattr(fidelity, "find_word_powershell_host", lambda: None)

    with pytest.raises(ValidationError, match="automation 'libreoffice' is unavailable"):
        fidelity.require_fidelity_automation("libreoffice")


def test_unknown_fidelity_mode_is_rejected() -> None:
    with pytest.raises(ValidationError, match="Unknown DOCX fidelity mode"):
        fidelity.require_production_fidelity("mystery")
