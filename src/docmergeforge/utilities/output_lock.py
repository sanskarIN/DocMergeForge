from __future__ import annotations

import importlib
import os
from pathlib import Path
from types import TracebackType
from typing import BinaryIO, Protocol, Self, cast

from docmergeforge.core.exceptions import OutputLockError

LOCK_FILENAME = ".docmergeforge-output.lock"


class _MsvcrtModule(Protocol):
    LK_NBLCK: int
    LK_UNLCK: int

    def locking(self, fd: int, mode: int, nbytes: int, /) -> None: ...


def _windows_locking_module() -> _MsvcrtModule:
    return cast(_MsvcrtModule, importlib.import_module("msvcrt"))


class OutputDirectoryLock:
    """Hold a non-blocking OS-level exclusive lock for one output directory."""

    def __init__(self, output_folder: Path) -> None:
        self.output_folder = output_folder
        self.path = output_folder / LOCK_FILENAME
        self._handle: BinaryIO | None = None

    def __enter__(self) -> Self:
        self.acquire()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        del exc_type, exc, traceback
        self.release()

    @property
    def acquired(self) -> bool:
        return self._handle is not None

    def acquire(self) -> None:
        if self._handle is not None:
            raise RuntimeError("Output-directory lock is already acquired.")

        self.output_folder.mkdir(parents=True, exist_ok=True)
        handle = self.path.open("a+b")
        try:
            if handle.seek(0, os.SEEK_END) == 0:
                handle.write(b"\0")
                handle.flush()
                os.fsync(handle.fileno())
            handle.seek(0)
            self._lock_handle(handle)
        except Exception:
            handle.close()
            raise
        self._handle = handle

    def release(self) -> None:
        handle = self._handle
        if handle is None:
            return
        self._handle = None
        try:
            self._unlock_handle(handle)
        finally:
            handle.close()

    def _lock_handle(self, handle: BinaryIO) -> None:
        try:
            if os.name == "nt":
                msvcrt = _windows_locking_module()
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            raise OutputLockError(
                "Another DocMergeForge process is already using this output directory: "
                f"{self.output_folder}"
            ) from exc

    @staticmethod
    def _unlock_handle(handle: BinaryIO) -> None:
        if os.name == "nt":
            msvcrt = _windows_locking_module()
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
