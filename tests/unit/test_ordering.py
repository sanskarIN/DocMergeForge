from pathlib import Path

import pytest

from docmergeforge.core.models import DocumentKind, InputDocument, PartIdentity
from docmergeforge.ordering.editor import OrderEditor


def item(part: int) -> InputDocument:
    return InputDocument(
        Path(f"Part {part}.pdf"),
        DocumentKind.PDF,
        PartIdentity(part, f"Part {part}"),
        1,
        str(part),
    )


def test_reorder_undo_redo_and_lock() -> None:
    editor = OrderEditor([item(10), item(2), item(1)])
    editor.sort_by_part()
    assert [x.part.number for x in editor.items] == [1, 2, 10]
    editor.move_to_bottom(0)
    assert [x.part.number for x in editor.items] == [2, 10, 1]
    assert editor.undo()
    assert [x.part.number for x in editor.items] == [1, 2, 10]
    assert editor.redo()
    editor.locked = True
    assert not editor.undo()


def test_set_order_records_drag_drop_for_undo() -> None:
    editor = OrderEditor([item(1), item(2), item(3)])
    editor.set_order([Path("Part 3.pdf"), Path("Part 1.pdf"), Path("Part 2.pdf")])
    assert [x.part.number for x in editor.items] == [3, 1, 2]
    assert editor.undo()
    assert [x.part.number for x in editor.items] == [1, 2, 3]


def test_set_order_rejects_missing_or_duplicate_paths() -> None:
    editor = OrderEditor([item(1), item(2)])
    with pytest.raises(ValueError, match="every current item"):
        editor.set_order([Path("Part 1.pdf")])
    with pytest.raises(ValueError, match="duplicate"):
        editor.set_order([Path("Part 1.pdf"), Path("Part 1.pdf")])
    with pytest.raises(ValueError, match="same document paths"):
        editor.set_order([Path("Part 1.pdf"), Path("Part 9.pdf")])


def test_move_and_adjacent_validate_indices() -> None:
    editor = OrderEditor([item(1), item(2)])
    with pytest.raises(IndexError):
        editor.move(-1, 0)
    with pytest.raises(IndexError):
        editor.move(0, 2)
    with pytest.raises(IndexError):
        editor.adjacent(2)
