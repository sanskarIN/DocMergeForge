import tomllib
from pathlib import Path

from docmergeforge import __version__


def test_pyproject_version_matches_package_version() -> None:
    root = Path(__file__).resolve().parents[2]
    pyproject = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))

    assert pyproject["project"]["version"] == __version__
