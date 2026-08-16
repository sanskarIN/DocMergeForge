from pathlib import Path

from docmergeforge.discovery.part_detection import detect_part, sort_documents_naturally


def test_120_part_shuffled_names_are_ordered() -> None:
    paths = [Path(f"SQL_Full_Mastery_Part_{i}_Ram_Sandesh.pdf") for i in range(120, 0, -1)]
    ordered = sort_documents_naturally(paths)
    assert [detect_part(path).number for path in ordered] == list(range(1, 121))
