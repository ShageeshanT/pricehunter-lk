from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field

from .adapters import AdapterRunner, PriceAdapter, SourceSearchResult, dedupe_candidates
from .models import PriceCandidate, ResearchItem
from .source_registry import default_adapters
from .sources import PriceSource


class PriceExtreme(BaseModel):
    site_name: str
    price: Decimal = Field(ge=0)
    url: str | None = None
    title: str
    confidence: float = Field(ge=0, le=1)
    availability: str | None = None
    source_name: str | None = None


class SourceHealth(BaseModel):
    name: str
    site_name: str
    ok: bool
    candidates: int = 0
    elapsed_ms: int = 0
    error: str | None = None


class PriceRangeResult(BaseModel):
    item_name: str
    cheapest: PriceExtreme | None = None
    most_expensive: PriceExtreme | None = None
    source_count: int = 0
    candidate_count: int = 0
    sources: list[SourceHealth] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class PriceRangeRequest(BaseModel):
    item_name: str = Field(min_length=1)
    max_candidates: int = Field(default=20, ge=1, le=50)
    live: bool = False


class PriceRangeResponse(BaseModel):
    result: PriceRangeResult


def _to_extreme(candidate: PriceCandidate) -> PriceExtreme:
    return PriceExtreme(
        site_name=candidate.vendor,
        price=candidate.price,
        url=candidate.url,
        title=candidate.title,
        confidence=candidate.confidence,
        availability=candidate.availability,
        source_name=str(candidate.raw.get("source", "")) or None,
    )


def _to_source_health(result: SourceSearchResult) -> SourceHealth:
    return SourceHealth(
        name=result.source.name,
        site_name=result.source.site_name,
        ok=result.ok,
        candidates=len(result.candidates),
        elapsed_ms=result.elapsed_ms,
        error=result.error,
    )


class PriceRangeFinder:
    def __init__(self, sources: list[PriceAdapter | AdapterRunner | PriceSource] | None = None, live: bool = False) -> None:
        self.sources = sources or default_adapters(include_live_scrapers=live)

    def find_range(self, item_name: str, max_candidates: int = 20) -> PriceRangeResult:
        item = ResearchItem(name=item_name, quantity=1)
        candidates: list[PriceCandidate] = []
        health: list[SourceHealth] = []
        warnings: list[str] = []

        for source in self.sources:
            if isinstance(source, PriceAdapter | AdapterRunner):
                result = source.search(item, limit=max_candidates)
                health.append(_to_source_health(result))
                candidates.extend(result.candidates)
                if not result.ok:
                    warnings.append(f"{result.source.site_name} failed: {result.error}")
                continue

            source_candidates = source.search(item, limit=max_candidates)
            candidates.extend(source_candidates)
            health.append(
                SourceHealth(
                    name=getattr(source, "name", source.__class__.__name__),
                    site_name=getattr(source, "name", source.__class__.__name__),
                    ok=True,
                    candidates=len(source_candidates),
                )
            )

        candidates = dedupe_candidates([candidate for candidate in candidates if candidate.confidence >= 0.18 and candidate.price > 0])
        if not candidates:
            return PriceRangeResult(
                item_name=item.name,
                source_count=len(health),
                candidate_count=0,
                sources=health,
                warnings=warnings + ["No matching prices found from configured sources."],
            )

        cheapest = min(candidates, key=lambda candidate: candidate.price)
        most_expensive = max(candidates, key=lambda candidate: candidate.price)
        return PriceRangeResult(
            item_name=item.name,
            cheapest=_to_extreme(cheapest),
            most_expensive=_to_extreme(most_expensive),
            source_count=len([source for source in health if source.ok]),
            candidate_count=len(candidates),
            sources=health,
            warnings=warnings,
        )
