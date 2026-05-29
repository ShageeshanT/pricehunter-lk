from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal
from difflib import SequenceMatcher

from .models import PriceCandidate, ResearchItem


class PriceSource(ABC):
    name: str

    @abstractmethod
    def search(self, item: ResearchItem, limit: int = 5) -> list[PriceCandidate]:
        raise NotImplementedError


_FIXTURE_PRODUCTS = [
    {"vendor": "Atlas Lanka", "title": "A4 document file", "price": "85", "keywords": ["a4", "file", "document"], "url": "https://example.lk/a4-file"},
    {"vendor": "OfficeMart LK", "title": "A4 plastic file", "price": "95", "keywords": ["a4", "file", "plastic"], "url": "https://example.lk/plastic-file"},
    {"vendor": "Stationery House", "title": "Blue ballpoint pen", "price": "35", "keywords": ["blue", "pen", "ballpoint"], "url": "https://example.lk/blue-pen"},
    {"vendor": "PrintHub Colombo", "title": "Custom wrist band", "price": "120", "keywords": ["wrist", "band", "custom"], "url": "https://example.lk/wrist-band"},
    {"vendor": "AwardLab", "title": "Wooden plaque medium", "price": "2850", "keywords": ["plaque", "award", "wooden"], "url": "https://example.lk/plaque"},
    {"vendor": "StickerWorks", "title": "Custom sticker sheet", "price": "180", "keywords": ["sticker", "sheet", "custom"], "url": "https://example.lk/sticker-sheet"},
    {"vendor": "EventPrint LK", "title": "OC tag with lanyard", "price": "160", "keywords": ["oc", "tag", "lanyard", "badge"], "url": "https://example.lk/oc-tag"},
    {"vendor": "SnackBox Colombo", "title": "Refreshment pack", "price": "450", "keywords": ["refreshment", "snack", "pack"], "url": "https://example.lk/refreshment-pack"},
]


def _score(query: str, title: str, keywords: list[str]) -> float:
    query_tokens = set(query.lower().replace("-", " ").split())
    keyword_tokens = set(keywords)
    overlap = len(query_tokens & keyword_tokens) / max(len(query_tokens), 1)
    title_ratio = SequenceMatcher(None, query.lower(), title.lower()).ratio()
    return round(min(1.0, overlap * 0.7 + title_ratio * 0.3), 3)


class FixturePriceSource(PriceSource):
    name = "fixture"

    def search(self, item: ResearchItem, limit: int = 5) -> list[PriceCandidate]:
        candidates: list[PriceCandidate] = []
        for product in _FIXTURE_PRODUCTS:
            confidence = _score(item.name, product["title"], product["keywords"])
            if confidence < 0.18:
                continue
            candidates.append(
                PriceCandidate(
                    item_name=item.name,
                    vendor=product["vendor"],
                    title=product["title"],
                    price=Decimal(product["price"]),
                    url=product["url"],
                    availability="sample source",
                    confidence=confidence,
                    notes="Deterministic fixture candidate for MVP testing.",
                    raw=product,
                )
            )
        return sorted(candidates, key=lambda candidate: (-candidate.confidence, candidate.price))[:limit]
