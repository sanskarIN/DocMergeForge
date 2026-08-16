import pytest

from docmergeforge.utilities.filename_template import render_filename


def test_template_variables() -> None:
    assert render_filename("{series}_Complete_{part_count}_Part", series="SQL", part_count=120) == "SQL_Complete_120_Part"


def test_unknown_variable_rejected() -> None:
    with pytest.raises(ValueError):
        render_filename("{secret}")
