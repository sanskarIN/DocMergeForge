import json
from pathlib import Path

from docmergeforge.settings.config import AppSettings


def test_settings_save_load_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "nested" / "settings.json"
    settings = AppSettings(
        theme="dark",
        worker_count=4,
        reduced_motion=True,
        text_scale_percent=125,
        first_run_completed=True,
    )

    settings.save(path)

    assert AppSettings.load(path) == settings
    assert not list(path.parent.glob(f".{path.name}.*.tmp"))


def test_settings_load_ignores_unknown_fields(tmp_path: Path) -> None:
    path = tmp_path / "settings.json"
    path.write_text(
        json.dumps({"theme": "light", "future_setting": "ignored"}),
        encoding="utf-8",
    )

    loaded = AppSettings.load(path)

    assert loaded.theme == "light"
    assert loaded.worker_count == 2


def test_settings_load_recovers_from_malformed_json(tmp_path: Path) -> None:
    path = tmp_path / "settings.json"
    path.write_text("{not valid json", encoding="utf-8")

    assert AppSettings.load(path) == AppSettings()


def test_settings_load_filters_wrong_types_and_clamps_ranges(tmp_path: Path) -> None:
    path = tmp_path / "settings.json"
    path.write_text(
        json.dumps(
            {
                "theme": "neon",
                "worker_count": 999,
                "text_scale_percent": 10,
                "reduced_motion": "yes",
                "logging_level": 123,
                "pdf_optimization": "unknown",
                "docx_fidelity_mode": "unverified-mode",
                "merge_profile": "Unknown Profile",
            }
        ),
        encoding="utf-8",
    )

    loaded = AppSettings.load(path)

    assert loaded.theme == "system"
    assert loaded.worker_count == 64
    assert loaded.text_scale_percent == 80
    assert loaded.reduced_motion is False
    assert loaded.logging_level == "INFO"
    assert loaded.pdf_optimization == "preserve"
    assert loaded.docx_fidelity_mode == "portable"
    assert loaded.merge_profile == "Exact Preservation"
