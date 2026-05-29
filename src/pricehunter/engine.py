from __future__ import annotations

from decimal import Decimal

from .models import ItemRecommendation, ResearchItem, ResearchReport
from .sources import FixturePriceSource, PriceSource


class ResearchEngine:
    def __init__(self, sources: list[PriceSource] | None = None) -> None:
        self.sources = sources or [FixturePriceSource()]

    def research_item(self, item: ResearchItem, max_candidates: int = 5) -> ItemRecommendation:
        candidates = []
        for source in self.sources:
            candidates.extend(source.search(item, limit=max_candidates))

        candidates = sorted(candidates, key=lambda candidate: (-candidate.confidence, candidate.price))[:max_candidates]
        recommended = candidates[0] if candidates else None
        warnings: list[str] = []
        confidence = recommended.confidence if recommended else 0
        estimated_total = Decimal("0")

        if recommended:
            estimated_total = recommended.price * item.quantity
            if recommended.confidence < 0.45:
                warnings.append("Low confidence match. Verify manually before buying.")
        else:
            warnings.append("No price candidates found.")

        return ItemRecommendation(
            item=item,
            candidates=candidates,
            recommended=recommended,
            estimated_total=estimated_total,
            confidence=confidence,
            warnings=warnings,
        )

    def research(self, items: list[ResearchItem], max_candidates_per_item: int = 5) -> ResearchReport:
        recommendations = [self.research_item(item, max_candidates_per_item) for item in items]
        grand_total = sum((recommendation.estimated_total for recommendation in recommendations), Decimal("0"))
        warnings = [f"{recommendation.item.name}: {warning}" for recommendation in recommendations for warning in recommendation.warnings]
        return ResearchReport(items=recommendations, grand_total=grand_total, warnings=warnings)
