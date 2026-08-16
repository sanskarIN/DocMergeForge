from __future__ import annotations

from datetime import date


_ALLOWED = {"series", "author", "part_count", "edition", "date", "profile", "version"}


def render_filename(template: str, **values: object) -> str:
    unknown = {field.split("!")[0].split(":")[0] for _, field, _, _ in _fields(template) if field} - _ALLOWED
    if unknown:
        raise ValueError(f"Unsupported filename template variables: {sorted(unknown)}")
    defaults = {
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


def _fields(template: str):
    import string

    return list(string.Formatter().parse(template))
