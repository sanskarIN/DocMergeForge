from docmergeforge.ui.resources import (
    BMC_URL,
    BUSINESS_EMAIL,
    DOCS_URL,
    REPOSITORY_URL,
    SUPPORT_EMAIL,
    X_URL,
)


def test_desktop_support_links_match_canonical_project_values() -> None:
    assert REPOSITORY_URL == "https://github.com/sanskarIN/DocMergeForge"
    assert DOCS_URL == f"{REPOSITORY_URL}/tree/main/docs"
    assert BMC_URL == "https://buymeacoffee.com/sanskarIN"
    assert X_URL == "https://x.com/x_sanskarIN"
    assert BUSINESS_EMAIL == "sanskarin@outlook.in"
    assert SUPPORT_EMAIL == "supportramsandesh@gmail.com"
