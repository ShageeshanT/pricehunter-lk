from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import Protocol
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from difflib import SequenceMatcher
from html.parser import HTMLParser
from time import perf_counter
from typing import Any
from urllib.parse import quote_plus, urljoin
from urllib.request import Request, urlopen

from .models import PriceCandidate, ResearchItem

_PRICE_RE = re.compile(r"(?:rs\.?|lkr|රු)\s*([0-9][0-9,]*(?:\.\d{1,2})?)|([0-9][0-9,]*(?:\.\d{1,2})?)\s*(?:rs\.?|lkr)", re.IGNORECASE)
_SPACE_RE = re.compile(r"\s+")


@dataclass(frozen=True)
class SourceMeta:
    name: str
    site_name: str
    base_url: str
    enabled: bool = True
    timeout_seconds: float = 6.0
    max_retries: int = 1
    source_type: str = "adapter"


@dataclass
class RawListing:
    source_name: str
    site_name: str
    title: str
    price: Decimal
    url: str | None = None
    availability: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class SourceSearchResult:
    source: SourceMeta
    candidates: list[PriceCandidate] = field(default_factory=list)
    ok: bool = True
    error: str | None = None
    elapsed_ms: int = 0


class RawSearchProvider(Protocol):
    meta: SourceMeta

    def search_raw(self, item: ResearchItem, limit: int = 10) -> list[RawListing]:
        ...


class PriceAdapter(ABC):
    meta: SourceMeta

    @abstractmethod
    def search_raw(self, item: ResearchItem, limit: int = 10) -> list[RawListing]:
        raise NotImplementedError

    def search(self, item: ResearchItem, limit: int = 10) -> SourceSearchResult:
        started = perf_counter()
        try:
            raw_listings = self.search_raw(item, limit=limit)
            candidates = [normalize_listing(item, listing) for listing in raw_listings]
            candidates = [candidate for candidate in candidates if candidate.price >= 0]
            candidates.sort(key=lambda candidate: (-candidate.confidence, candidate.price, candidate.vendor))
            return SourceSearchResult(
                source=self.meta,
                candidates=candidates[:limit],
                ok=True,
                elapsed_ms=int((perf_counter() - started) * 1000),
            )
        except Exception as exc:  # pragma: no cover - defensive adapter boundary
            return SourceSearchResult(
                source=self.meta,
                ok=False,
                error=str(exc),
                elapsed_ms=int((perf_counter() - started) * 1000),
            )


def clean_text(value: str) -> str:
    return _SPACE_RE.sub(" ", value.replace("\xa0", " ")).strip()


def query_tokens(value: str) -> list[str]:
    cleaned = re.sub(r"[^a-z0-9\s]", " ", value.lower())
    return [token for token in cleaned.split() if token]


def parse_price(value: str | int | float | Decimal) -> Decimal | None:
    if isinstance(value, Decimal):
        return value
    if isinstance(value, int | float):
        return Decimal(str(value))
    text = clean_text(str(value))
    match = _PRICE_RE.search(text)
    if not match:
        text = text.replace(",", "")
        if not re.fullmatch(r"[0-9]+(?:\.\d{1,2})?", text):
            return None
        raw = text
    else:
        raw = (match.group(1) or match.group(2) or "").replace(",", "")
    try:
        return Decimal(raw)
    except (InvalidOperation, ValueError):
        return None


def relevance_score(query: str, title: str) -> float:
    q_tokens = query_tokens(query)
    t_tokens = set(query_tokens(title))
    if not q_tokens:
        return 0
    overlap = len([token for token in q_tokens if token in t_tokens]) / len(q_tokens)
    phrase_bonus = 0.15 if query.lower() in title.lower() else 0
    ratio = SequenceMatcher(None, query.lower(), title.lower()).ratio()
    return round(min(1.0, overlap * 0.68 + ratio * 0.22 + phrase_bonus), 3)


def normalize_listing(item: ResearchItem, listing: RawListing) -> PriceCandidate:
    confidence = relevance_score(item.name, listing.title)
    return PriceCandidate(
        item_name=item.name,
        vendor=listing.site_name,
        title=clean_text(listing.title),
        price=listing.price,
        url=listing.url,
        availability=listing.availability,
        confidence=confidence,
        notes=f"{listing.source_name} normalized adapter result.",
        raw={
            "source": listing.source_name,
            "site_name": listing.site_name,
            **listing.raw,
        },
    )


def dedupe_candidates(candidates: list[PriceCandidate]) -> list[PriceCandidate]:
    seen: set[tuple[str, str, str]] = set()
    deduped: list[PriceCandidate] = []
    for candidate in sorted(candidates, key=lambda item: (-item.confidence, item.price)):
        key = (
            candidate.vendor.lower(),
            clean_text(candidate.title).lower(),
            str(candidate.price.quantize(Decimal("1"))) if candidate.price == candidate.price.to_integral() else str(candidate.price),
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(candidate)
    return deduped


class FixtureAdapter(PriceAdapter):
    def __init__(self, name: str, site_name: str, products: list[dict[str, Any]]) -> None:
        self.meta = SourceMeta(name=name, site_name=site_name, base_url="https://example.lk", source_type="fixture")
        self.products = products

    def search_raw(self, item: ResearchItem, limit: int = 10) -> list[RawListing]:
        rows: list[RawListing] = []
        for product in self.products:
            title = str(product["title"])
            score = relevance_score(item.name, title)
            if score < 0.18:
                continue
            price = parse_price(product["price"])
            if price is None:
                continue
            rows.append(
                RawListing(
                    source_name=self.meta.name,
                    site_name=str(product.get("site_name", self.meta.site_name)),
                    title=title,
                    price=price,
                    url=str(product.get("url", self.meta.base_url)),
                    availability=str(product.get("availability", "sample available")),
                    raw=dict(product),
                )
            )
        return sorted(rows, key=lambda row: (row.price, row.site_name))[:limit]


class SearchUrlAdapter(PriceAdapter):
    def __init__(self, name: str, site_name: str, search_url_template: str, timeout_seconds: float = 6.0) -> None:
        self.meta = SourceMeta(
            name=name,
            site_name=site_name,
            base_url=search_url_template,
            timeout_seconds=timeout_seconds,
            source_type="search-url",
        )
        self.search_url_template = search_url_template

    def search_raw(self, item: ResearchItem, limit: int = 10) -> list[RawListing]:
        url = self.search_url_template.format(query=quote_plus(item.name))
        return [
            RawListing(
                source_name=self.meta.name,
                site_name=self.meta.site_name,
                title=f"Search {item.name} on {self.meta.site_name}",
                price=Decimal("0"),
                url=url,
                availability="search handoff",
                raw={"handoff": True},
            )
        ][:limit]


class SimpleHTMLListingParser(HTMLParser):
    def __init__(self, base_url: str) -> None:
        super().__init__()
        self.base_url = base_url
        self.in_link = False
        self.current_href: str | None = None
        self.links: list[tuple[str, str | None]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        attrs_dict = dict(attrs)
        self.in_link = True
        self.current_href = attrs_dict.get("href")

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a":
            self.in_link = False
            self.current_href = None

    def handle_data(self, data: str) -> None:
        if self.in_link:
            text = clean_text(data)
            if text:
                href = urljoin(self.base_url, self.current_href or "") if self.current_href else None
                self.links.append((text, href))


class AdapterRunner:
    def __init__(self, provider: RawSearchProvider) -> None:
        self.provider = provider
        self.meta = provider.meta

    def search(self, item: ResearchItem, limit: int = 10) -> SourceSearchResult:
        started = perf_counter()
        try:
            raw_listings = self.provider.search_raw(item, limit=limit)
            candidates = [normalize_listing(item, listing) for listing in raw_listings]
            candidates = [candidate for candidate in candidates if candidate.price >= 0]
            candidates.sort(key=lambda candidate: (-candidate.confidence, candidate.price, candidate.vendor))
            return SourceSearchResult(
                source=self.meta,
                candidates=candidates[:limit],
                ok=True,
                elapsed_ms=int((perf_counter() - started) * 1000),
            )
        except Exception as exc:  # pragma: no cover - defensive adapter boundary
            return SourceSearchResult(
                source=self.meta,
                ok=False,
                error=str(exc),
                elapsed_ms=int((perf_counter() - started) * 1000),
            )


class HTMLPageAdapter(PriceAdapter):
    def __init__(self, name: str, site_name: str, url: str, timeout_seconds: float = 6.0) -> None:
        self.meta = SourceMeta(name=name, site_name=site_name, base_url=url, timeout_seconds=timeout_seconds, source_type="html")
        self.url = url

    def search_raw(self, item: ResearchItem, limit: int = 10) -> list[RawListing]:
        request = Request(self.url, headers={"User-Agent": "PriceHunterLK/0.1 (+https://github.com/ShageeshanT/pricehunter-lk)"})
        with urlopen(request, timeout=self.meta.timeout_seconds) as response:  # noqa: S310 - configured public adapter URLs only
            html = response.read(500_000).decode("utf-8", errors="ignore")
        parser = SimpleHTMLListingParser(self.url)
        parser.feed(html)
        listings: list[RawListing] = []
        for text, href in parser.links:
            price = parse_price(text)
            if price is None:
                continue
            listings.append(
                RawListing(
                    source_name=self.meta.name,
                    site_name=self.meta.site_name,
                    title=text,
                    price=price,
                    url=href or self.url,
                    availability="parsed from page",
                    raw={"parser": "link-text-price"},
                )
            )
            if len(listings) >= limit:
                break
        return listings
