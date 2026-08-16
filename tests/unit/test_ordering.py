from pathlib import Path

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
