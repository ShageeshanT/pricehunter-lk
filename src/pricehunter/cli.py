from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from .engine import ResearchEngine
from .exporters import sheets_rows, write_csv, write_json
from .parser import parse_items_file
from .ranges import PriceRangeFinder

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


@app.command("range")
def price_range(
    item_name: str = typer.Argument(..., help="Item name to search"),
    max_candidates: int = typer.Option(20, help="Maximum candidates to inspect"),
) -> None:
    result = PriceRangeFinder().find_range(item_name, max_candidates=max_candidates)
    if not result.cheapest or not result.most_expensive:
        typer.echo(f"No prices found for {result.item_name}")
        raise typer.Exit(code=1)
    typer.echo(f"Item: {result.item_name}")
    typer.echo(f"Cheapest: {result.cheapest.site_name} | LKR {result.cheapest.price} | {result.cheapest.url or 'no url'}")
    typer.echo(f"Most expensive: {result.most_expensive.site_name} | LKR {result.most_expensive.price} | {result.most_expensive.url or 'no url'}")
