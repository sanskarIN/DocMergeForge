from pathlib import Path

from docmergeforge.core.part_range import MAX_PART_NUMBER
from docmergeforge.discovery.part_detection import detect_part, sort_documents_naturally


def test_detects_common_part_names() -> None:
    cases = {
        "Part_1.pdf": 1,
        "Part 01.docx": 1,
        "Part-001.pdf": 1,
        "Chapter_42.docx": 42,
        "Volume_120.pdf": 120,
        "SQL_Full_Mastery_Part_118_Ram_Sandesh.pdf": 118,
    }
    for name, expected in cases.items():
        assert detect_part(Path(name)).number == expected


def test_detector_boundary_matches_supported_part_number_limit() -> None:
    assert detect_part(Path(f"Part {MAX_PART_NUMBER}.pdf")).number == MAX_PART_NUMBER
    assert detect_part(Path(f"Part {MAX_PART_NUMBER + 1}.pdf")).number is None


def test_natural_sort_orders_2_before_10() -> None:
    values = [Path("Part 10.pdf"), Path("Part 2.pdf"), Path("Part 1.pdf"), Path("Part 100.pdf")]
    assert [item.name for item in sort_documents_naturally(values)] == [
        "Part 1.pdf",
        "Part 2.pdf",
        "Part 10.pdf",
        "Part 100.pdf",
    ]
