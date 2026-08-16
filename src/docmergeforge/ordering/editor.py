from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from docmergeforge.core.models import InputDocument
from docmergeforge.discovery.part_detection import natural_key


def _path_key(path: Path) -> str:
    try:
        return str(path.resolve(strict=False)).casefold()
    except OSError:
        return str(path.absolute()).casefold()


@dataclass(slots=True)
class OrderEditor:
    items: list[InputDocument]
    locked: bool = False
    _undo: list[list[InputDocument]] = field(default_factory=list, init=False)
    _redo: list[list[InputDocument]] = field(default_factory=list, init=False)

    def _snapshot(self) -> None:
        if self.locked:
            raise RuntimeError("Order is locked.")
        self._undo.append(list(self.items))
        self._redo.clear()

    def sort_by_part(self, descending: bool = False) -> None:
        self._snapshot()
        self.items.sort(
            key=lambda item: (
                item.part.number is None,
                item.part.number if item.part.number is not None else 10**12,
                natural_key(item.path.name),
            ),
            reverse=descending,
        )

    def sort_by_filename(self, descending: bool = False) -> None:
        self._snapshot()
        self.items.sort(
            key=lambda item: natural_key(item.path.name),
            reverse=descending,
        )

    def set_order(self, ordered_paths: list[Path]) -> None:
        """Replace the complete order after validating a drag/drop result."""
        if len(ordered_paths) != len(self.items):
            raise ValueError("Replacement order must contain every current item exactly once.")

        by_path = {_path_key(item.path): item for item in self.items}
        requested_keys = [_path_key(path) for path in ordered_paths]
        if len(set(requested_keys)) != len(requested_keys):
            raise ValueError("Replacement order contains duplicate paths.")
        if set(requested_keys) != set(by_path):
            raise ValueError("Replacement order must contain the same document paths.")

        self._snapshot()
        self.items = [by_path[key] for key in requested_keys]

    def move(self, source: int, target: int) -> None:
        if source < 0 or source >= len(self.items):
            raise IndexError("Source index is outside the document order.")
        if target < 0 or target >= len(self.items):
            raise IndexError("Target index is outside the document order.")
        self._snapshot()
        item = self.items.pop(source)
        self.items.insert(target, item)

    def move_up(self, index: int) -> None:
        if index <= 0:
            return
        self.move(index, index - 1)

    def move_down(self, index: int) -> None:
        if index >= len(self.items) - 1:
            return
        self.move(index, index + 1)

    def move_to_top(self, index: int) -> None:
        self.move(index, 0)

    def move_to_bottom(self, index: int) -> None:
        self.move(index, len(self.items) - 1)

    def undo(self) -> bool:
        if not self._undo or self.locked:
            return False
        self._redo.append(list(self.items))
        self.items = self._undo.pop()
        return True

    def redo(self) -> bool:
        if not self._redo or self.locked:
            return False
        self._undo.append(list(self.items))
        self.items = self._redo.pop()
        return True

    def filter(self, query: str) -> list[InputDocument]:
        needle = query.casefold().strip()
        if not needle:
            return list(self.items)
        return [item for item in self.items if needle in item.path.name.casefold()]

    def adjacent(self, index: int) -> tuple[InputDocument | None, InputDocument | None]:
        if index < 0 or index >= len(self.items):
            raise IndexError("Index is outside the document order.")
        before = self.items[index - 1] if index > 0 else None
        after = self.items[index + 1] if index < len(self.items) - 1 else None
        return before, after
