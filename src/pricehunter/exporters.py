from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .models import ResearchReport


def sheets_rows(report: ResearchReport) -> list[list[Any]]:
    rows: list[list[Any]] = [[
        "Item",
        "Quantity",
        "Recommended vendor",
        "Recommended title",
        "Unit price LKR",
        "Estimated total LKR",
        "Confidence",
        "URL",
        "Warnings",
    ]]
    for recommendation in report.items:
        candidate = recommendation.recommended
        rows.append([
            recommendation.item.name,
            recommendation.item.quantity,
            candidate.vendor if candidate else "",
            candidate.title if candidate else "",
            str(candidate.price) if candidate else "",
            str(recommendation.estimated_total),
            recommendation.confidence,
            candidate.url if candidate else "",
            "; ".join(recommendation.warnings),
        ])
    rows.append(["Grand total", "", "", "", "", str(report.grand_total), "", "", ""])
    return rows


def write_csv(report: ResearchReport, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerows(sheets_rows(report))


def write_json(report: ResearchReport, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report.model_dump(mode="json"), indent=2), encoding="utf-8")
