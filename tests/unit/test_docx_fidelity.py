import pytest

from docmergeforge.core.exceptions import ValidationError
from docmergeforge.docx.fidelity import fidelity_capabilities, require_production_fidelity


def test_portable_fidelity_is_production_ready() -> None:
    capabilities = {item.mode: item for item in fidelity_capabilities()}
    assert capabilities["portable"].available
    assert capabilities["portable"].production_ready
    require_production_fidelity("portable")


def test_nonproduction_fidelity_never_silently_falls_back() -> None:
    for mode in ("libreoffice", "word"):
        with pytest.raises(ValidationError):
            require_production_fidelity(mode)


def test_unknown_fidelity_mode_is_rejected() -> None:
    with pytest.raises(ValidationError, match="Unknown DOCX fidelity mode"):
        require_production_fidelity("mystery")
