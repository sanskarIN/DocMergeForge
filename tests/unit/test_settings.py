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
