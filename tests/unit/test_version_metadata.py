import tomllib
from pathlib import Path

from docmergeforge import __version__


def _pyproject() -> dict[str, object]:
    root = Path(__file__).resolve().parents[2]
    return tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))


def test_pyproject_version_matches_package_version() -> None:
    pyproject = _pyproject()
    project = pyproject["project"]
    assert isinstance(project, dict)
    assert project["version"] == __version__


def test_public_console_scripts_use_maintained_entry_points() -> None:
    pyproject = _pyproject()
    project = pyproject["project"]
    assert isinstance(project, dict)
    scripts = project["scripts"]
    assert isinstance(scripts, dict)

    assert scripts["docmergeforge"] == "docmergeforge.cli.main:main"
    assert scripts["docmergeforge-gui"] == "docmergeforge.ui.desktop_entry:main"
    assert scripts["docmergeforge-web"] == "docmergeforge.web.main:main"
