from __future__ import annotations

import csv
import re
from pathlib import Path

from .models import ResearchItem

_QUANTITY_RE = re.compile(r"^(?P<name>.+?)(?:\s*[xX]\s*|,\s*|\s+-\s+)(?P<qty>\d+)\s*$")


def parse_item_line(line: str) -> ResearchItem | None:
    cleaned = line.strip()
    if not cleaned or cleaned.startswith("#"):
        return None

    match = _QUANTITY_RE.match(cleaned)
    if match:
        return ResearchItem(name=match.group("name"), quantity=int(match.group("qty")))
    return ResearchItem(name=cleaned, quantity=1)


def parse_items_text(text: str) -> list[ResearchItem]:
    items: list[ResearchItem] = []
    for line in text.splitlines():
        item = parse_item_line(line)
        if item:
            items.append(item)
    return items


def parse_items_file(path: str | Path) -> list[ResearchItem]:
    path = Path(path)
    if path.suffix.lower() == ".csv":
        with path.open(newline="", encoding="utf-8") as handle:
            rows = csv.DictReader(handle)
            return [ResearchItem(name=row["name"], quantity=int(row.get("quantity") or 1), notes=row.get("notes") or None) for row in rows]
    return parse_items_text(path.read_text(encoding="utf-8"))
