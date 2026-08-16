from pathlib import Path

from docmergeforge.audit.publication import audit_text


def test_flags_part_121_reference() -> None:
    findings = audit_text(Path("part120.txt"), "Next: Part 121")
    assert any(item.code == "stale-next-part" for item in findings)
