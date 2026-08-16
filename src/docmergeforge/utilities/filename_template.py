from __future__ import annotations

import string
from datetime import date

_ALLOWED = {"series", "author", "part_count", "edition", "date", "profile", "version"}


def render_filename(template: str, **values: object) -> str:
    fields = [field for _, field, _, _ in string.Formatter().parse(template) if field]
    unknown = {field.split("!")[0].split(":")[0] for field in fields} - _ALLOWED
    if unknown:
        raise ValueError(f"Unsupported filename template variables: {sorted(unknown)}")
    defaults: dict[str, object] = {
        "series": "Document",
        "author": "",
        "part_count": "",
        "edition": "",
        "date": date.today().isoformat(),
        "profile": "",
        "version": "",
    }
    defaults.update(values)
    return template.format(**defaults)
