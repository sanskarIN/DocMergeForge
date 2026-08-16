from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True, frozen=True)
class AuditFinding:
    code: str
    message: str
    path: Path
    severity: str = "WARNING"


_PATTERNS = {
    "stale_next_part": re.compile(r"(?i)\bnext\s*:?\s*part\s+121\b"),
    "github_url": re.compile(r"https?://(?:www\.)?github\.com/[A-Za-z0-9_.-]+"),
    "email": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
}


def audit_text(path: Path, text: str) -> list[AuditFinding]:
    findings: list[AuditFinding] = []
    if _PATTERNS["stale_next_part"].search(text):
        findings.append(
            AuditFinding(
                "stale-next-part",
                "Found a stale 'Next: Part 121' reference.",
                path,
            )
        )
    githubs = set(_PATTERNS["github_url"].findall(text))
    if len(githubs) > 1:
        findings.append(
            AuditFinding(
                "github-inconsistent",
                f"Multiple GitHub URLs detected: {sorted(githubs)}",
                path,
            )
        )
    emails = set(_PATTERNS["email"].findall(text))
    if len(emails) > 3:
        findings.append(
            AuditFinding(
                "email-review",
                f"Many email variants detected: {sorted(emails)}",
                path,
            )
        )
    return findings
