from __future__ import annotations

from fastapi import FastAPI

from .engine import ResearchEngine
from .exporters import sheets_rows
from .models import ResearchRequest, ResearchResponse

app = FastAPI(title="PriceHunter LK", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "pricehunter-lk"}


@app.post("/research", response_model=ResearchResponse)
def research(request: ResearchRequest) -> ResearchResponse:
    engine = ResearchEngine()
    report = engine.research(request.items, max_candidates_per_item=request.max_candidates_per_item)
    return ResearchResponse(report=report)


@app.post("/research/sheets-rows")
def research_sheets_rows(request: ResearchRequest) -> dict[str, list[list[object]]]:
    engine = ResearchEngine()
    report = engine.research(request.items, max_candidates_per_item=request.max_candidates_per_item)
    return {"rows": sheets_rows(report)}
