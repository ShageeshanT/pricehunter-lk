from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from .engine import ResearchEngine
from .exporters import sheets_rows, write_csv, write_json
from .parser import parse_items_file

app = typer.Typer(help="PriceHunter LK research tools")


@app.command()
def research(
    input_file: Path = typer.Argument(..., help="Text or CSV file containing item names and quantities"),
    csv_output: Optional[Path] = typer.Option(None, "--csv", help="Write Google Sheets-ready CSV output"),
    json_output: Optional[Path] = typer.Option(None, "--json", help="Write full JSON report"),
    max_candidates: int = typer.Option(5, help="Maximum candidates per item"),
) -> None:
    items = parse_items_file(input_file)
    engine = ResearchEngine()
    report = engine.research(items, max_candidates_per_item=max_candidates)

    if csv_output:
        write_csv(report, csv_output)
    if json_output:
        write_json(report, json_output)

    typer.echo(f"Researched {len(report.items)} items")
    typer.echo(f"Estimated grand total: LKR {report.grand_total}")
    for row in sheets_rows(report)[1:-1]:
        typer.echo(f"- {row[0]} x {row[1]}: LKR {row[5]} via {row[2] or 'no match'}")


if __name__ == "__main__":
    app()
