from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field

from .models import PriceCandidate, ResearchItem
from .sources import FixturePriceSource, PriceSource


class PriceExtreme(BaseModel):
    site_name: str
    price: Decimal = Field(ge=0)
    url: str | None = None
    title: str
    confidence: float = Field(ge=0, le=1)


class PriceRangeResult(BaseModel):
    item_name: str
    cheapest: PriceExtreme | None = None
    most_expensive: PriceExtreme | None = None
    source_count: int = 0
    warnings: list[str] = Field(default_factory=list)


class PriceRangeRequest(BaseModel):
    item_name: str = Field(min_length=1)
    max_candidates: int = Field(default=20, ge=1, le=50)


class PriceRangeResponse(BaseModel):
    result: PriceRangeResult


def _to_extreme(candidate: PriceCandidate) -> PriceExtreme:
    return PriceExtreme(
        site_name=candidate.vendor,
        price=candidate.price,
        url=candidate.url,
        title=candidate.title,
        confidence=candidate.confidence,
    )


class PriceRangeFinder:
    def __init__(self, sources: list[PriceSource] | None = None) -> None:
        self.sources = sources or [FixturePriceSource()]

    def find_range(self, item_name: str, max_candidates: int = 20) -> PriceRangeResult:
        item = ResearchItem(name=item_name, quantity=1)
        candidates: list[PriceCandidate] = []
        for source in self.sources:
            candidates.extend(source.search(item, limit=max_candidates))

        candidates = [candidate for candidate in candidates if candidate.confidence >= 0.18]
        if not candidates:
            return PriceRangeResult(
                item_name=item.name,
                source_count=0,
                warnings=["No matching prices found from configured sources."],
            )

        cheapest = min(candidates, key=lambda candidate: candidate.price)
        most_expensive = max(candidates, key=lambda candidate: candidate.price)
        return PriceRangeResult(
            item_name=item.name,
            cheapest=_to_extreme(cheapest),
            most_expensive=_to_extreme(most_expensive),
            source_count=len(candidates),
        )
