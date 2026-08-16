from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from threading import Event
from typing import Any

from PySide6.QtCore import QThread, Signal

from docmergeforge.app.service import CancellationCallback, ProgressCallback

WorkerRunner = Callable[[ProgressCallback, CancellationCallback], Any]


class MergeWorker(QThread):
    progress_changed = Signal(str, int, int, str)
    completed = Signal(object)
    failed = Signal(str)
    cancelled = Signal()

    def __init__(self, runner: WorkerRunner) -> None:
        super().__init__()
        self._runner = runner
        self._cancel_event = Event()

    def request_cancel(self) -> None:
        self._cancel_event.set()

    def is_cancelled(self) -> bool:
        return self._cancel_event.is_set()

    def _progress(self, stage: str, current: int, total: int, path: Path | None) -> None:
        self.progress_changed.emit(stage, current, total, str(path) if path else "")

    def run(self) -> None:
        try:
            result = self._runner(self._progress, self.is_cancelled)
            if self.is_cancelled():
                self.cancelled.emit()
            else:
                self.completed.emit(result)
        except Exception as exc:
            if self.is_cancelled():
                self.cancelled.emit()
            else:
                self.failed.emit(str(exc))
