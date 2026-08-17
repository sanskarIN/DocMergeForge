from __future__ import annotations

import os
import sys

PACKAGED_SMOKE_ARGUMENT = "--packaged-smoke"


def _run_packaged_smoke() -> int:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    from PySide6.QtWidgets import QApplication

    from docmergeforge.diagnostics.logging import configure_logging
    from docmergeforge.settings.config import AppSettings
    from docmergeforge.ui.main import MainWindow
    from docmergeforge.ui.paths import log_path, settings_path
    from docmergeforge.ui.theme import apply_text_scale, apply_theme

    app = QApplication.instance()
    if not isinstance(app, QApplication):
        app = QApplication(sys.argv)
    app.setApplicationName("DocMergeForge")
    app.setOrganizationName("Sanskar")

    settings = AppSettings.load(settings_path())
    configure_logging(log_path(), settings.logging_level)
    apply_theme(app, settings.theme)
    apply_text_scale(app, settings.text_scale_percent)

    window = MainWindow()
    window.close()
    app.processEvents()
    return 0


def main() -> int:
    if PACKAGED_SMOKE_ARGUMENT in sys.argv[1:]:
        return _run_packaged_smoke()

    from docmergeforge.ui.main import main as desktop_main

    return desktop_main()


if __name__ == "__main__":
    raise SystemExit(main())
