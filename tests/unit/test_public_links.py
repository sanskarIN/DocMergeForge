"""Prevent removed social and outdated project links from returning."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEXT_SUFFIXES = {".md", ".py", ".toml", ".yml", ".yaml", ".svg", ".txt", ".ps1"}
RETIRED_REFERENCES = (
    "linkedin.com/",
    "youtube.com/",
    "youtu.be/",
    "twitter.com/",
    "x.com/",
    "buymeacoffee.com/sanskarIN",
    "github.com/sanskarIN/DocMergeForge",
    "sanskarin.business@gmail.com",
)


def test_retired_public_links_are_absent_from_project_text() -> None:
    tracked_like_files = [
        ROOT / "README.md",
        ROOT / "SECURITY.md",
        ROOT / "pyproject.toml",
        ROOT / "CONTRIBUTING.md",
        ROOT / "what_changed.md",
    ]
    for directory in (".github", "assets", "docs", "scripts", "src", "tests"):
        tracked_like_files.extend(
            path
            for path in (ROOT / directory).rglob("*")
            if path.is_file() and path.suffix in TEXT_SUFFIXES
        )

    matches = []
    for path in tracked_like_files:
        if path == Path(__file__):
            continue
        text = path.read_text(encoding="utf-8").lower()
        for retired in RETIRED_REFERENCES:
            if retired.lower() in text:
                matches.append(f"{path.relative_to(ROOT)}: {retired}")

    assert not matches, "Retired project references remain:\n" + "\n".join(matches)


def test_funding_configuration_lists_official_donation_links() -> None:
    funding = (ROOT / ".github" / "FUNDING.yml").read_text(encoding="utf-8")
    assert "https://buymeacoffee.com/SanskarCodes" in funding
    assert "https://razorpay.me/@SanskarCodes" in funding
    assert "https://paypal.me/SanskarCodes" in funding
