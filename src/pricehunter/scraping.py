from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from decimal import Decimal
from html.parser import HTMLParser
from typing import Any
from urllib.parse import quote_plus, urljoin
from urllib.robotparser import RobotFileParser
from urllib.request import Request, urlopen

from .adapters import RawListing, SourceMeta, clean_text, parse_price, relevance_score
from .models import ResearchItem

_PRICE_CONTEXT_RE = re.compile(
    r"(?P<title>[A-Za-z0-9][A-Za-z0-9\s\-+.,()/'\"]{4,120}?)\s+(?P<price>(?:Rs\.?|LKR|රු)\s*[0-9][0-9,]*(?:\.\d{1,2})?)",
    re.IGNORECASE,
)
_JSON_LD_RE = re.compile(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.IGNORECASE | re.DOTALL)


@dataclass(frozen=True)
class ScrapeSourceConfig:
    name: str
    site_name: str
    search_url: str
    enabled: bool = True
    timeout_seconds: float = 7.0
    max_bytes: int = 750_000
    obey_robots: bool = True
    min_confidence: float = 0.22
    headers: dict[str, str] = field(default_factory=dict)

    def build_url(self, query: str) -> str:
        return self.search_url.format(query=quote_plus(query))

    @property
    def base_url(self) -> str:
        parts = self.search_url.split("/")
        return "/".join(parts[:3]) if len(parts) >= 3 else self.search_url


class ProductHTMLParser(HTMLParser):
    def __init__(self, base_url: str) -> None:
        super().__init__()
        self.base_url = base_url
        self._tag_stack: list[str] = []
        self._link_stack: list[str | None] = []
        self._current_link: str | None = None
        self.links: list[tuple[str, str | None]] = []
        self.text_chunks: list[str] = []
        self.meta: dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {key.lower(): value for key, value in attrs if key}
        self._tag_stack.append(tag.lower())
        if tag.lower() == "a":
            href = attrs_dict.get("href")
            self._current_link = urljoin(self.base_url, href) if href else None
            self._link_stack.append(self._current_link)
        if tag.lower() == "meta":
            key = attrs_dict.get("property") or attrs_dict.get("name") or ""
            content = attrs_dict.get("content")
            if key and content:
                self.meta[key.lower()] = clean_text(content)

    def handle_endtag(self, tag: str) -> None:
        if self._tag_stack:
            self._tag_stack.pop()
        if tag.lower() == "a":
            if self._link_stack:
                self._link_stack.pop()
            self._current_link = self._link_stack[-1] if self._link_stack else None

    def handle_data(self, data: str) -> None:
        text = clean_text(data)
        if not text:
            return
        self.text_chunks.append(text)
        if self._current_link:
            self.links.append((text, self._current_link))


def _user_agent() -> str:
    return "PriceHunterLK/0.2 research bot (+https://github.com/ShageeshanT/pricehunter-lk)"


def robots_allows(config: ScrapeSourceConfig, url: str) -> bool:
    if not config.obey_robots:
        return True
    parser = RobotFileParser()
    parser.set_url(urljoin(config.base_url, "/robots.txt"))
    try:
        parser.read()
    except Exception:
        return True
    return parser.can_fetch(_user_agent(), url)


def fetch_html(config: ScrapeSourceConfig, query: str) -> str:
    url = config.build_url(query)
    if not robots_allows(config, url):
        raise PermissionError(f"robots.txt disallows fetching {config.site_name}")
    headers = {"User-Agent": _user_agent(), "Accept": "text/html,application/xhtml+xml"}
    headers.update(config.headers)
    request = Request(url, headers=headers)
    with urlopen(request, timeout=config.timeout_seconds) as response:  # noqa: S310 - source URLs are configured, not user supplied
        return response.read(config.max_bytes).decode("utf-8", errors="ignore")


def _flatten_json(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, dict):
        rows = [value]
        for nested in value.values():
            rows.extend(_flatten_json(nested))
        return rows
    if isinstance(value, list):
        rows: list[dict[str, Any]] = []
        for item in value:
            rows.extend(_flatten_json(item))
        return rows
    return []


def extract_json_ld_listings(html: str, config: ScrapeSourceConfig, item: ResearchItem, limit: int = 20) -> list[RawListing]:
    listings: list[RawListing] = []
    for block in _JSON_LD_RE.findall(html):
        try:
            payload = json.loads(block.strip())
        except json.JSONDecodeError:
            continue
        for row in _flatten_json(payload):
            name = row.get("name") or row.get("headline")
            offers = row.get("offers") if isinstance(row.get("offers"), dict) else {}
            price = parse_price(offers.get("price") or row.get("price") or row.get("lowPrice"))
            if not name or price is None:
                continue
            title = clean_text(str(name))
            if relevance_score(item.name, title) < config.min_confidence:
                continue
            listings.append(
                RawListing(
                    source_name=config.name,
                    site_name=config.site_name,
                    title=title,
                    price=price,
                    url=str(row.get("url") or offers.get("url") or config.build_url(item.name)),
                    availability=str(offers.get("availability", "json-ld offer")),
                    raw={"extractor": "json-ld"},
                )
            )
            if len(listings) >= limit:
                return listings
    return listings


def extract_text_price_listings(html: str, config: ScrapeSourceConfig, item: ResearchItem, limit: int = 20) -> list[RawListing]:
    parser = ProductHTMLParser(config.base_url)
    parser.feed(html)
    listings: list[RawListing] = []

    merged = " ".join(parser.text_chunks)
    for match in _PRICE_CONTEXT_RE.finditer(merged):
        title = clean_text(match.group("title"))
        price = parse_price(match.group("price"))
        if price is None or relevance_score(item.name, title) < config.min_confidence:
            continue
        listings.append(
            RawListing(
                source_name=config.name,
                site_name=config.site_name,
                title=title,
                price=price,
                url=config.build_url(item.name),
                availability="text price match",
                raw={"extractor": "text-price-context"},
            )
        )
        if len(listings) >= limit:
            break

    for text, href in parser.links:
        price = parse_price(text)
        if price is None:
            continue
        title = clean_text(text)
        if relevance_score(item.name, title) < config.min_confidence:
            continue
        listings.append(
            RawListing(
                source_name=config.name,
                site_name=config.site_name,
                title=title,
                price=price,
                url=href or config.build_url(item.name),
                availability="link price match",
                raw={"extractor": "link-text"},
            )
        )
        if len(listings) >= limit:
            break
    return listings[:limit]


def extract_listings(html: str, config: ScrapeSourceConfig, item: ResearchItem, limit: int = 20) -> list[RawListing]:
    json_ld = extract_json_ld_listings(html, config, item, limit=limit)
    if len(json_ld) >= limit:
        return json_ld[:limit]
    text_matches = extract_text_price_listings(html, config, item, limit=limit - len(json_ld))
    return (json_ld + text_matches)[:limit]


def default_scrape_configs() -> list[ScrapeSourceConfig]:
    return [
        ScrapeSourceConfig("daraz-live-search", "Daraz LK", "https://www.daraz.lk/catalog/?q={query}", enabled=False),
        ScrapeSourceConfig("singer-live-search", "Singer", "https://www.singer.lk/catalogsearch/result/?q={query}", enabled=False),
        ScrapeSourceConfig("abans-live-search", "Abans", "https://www.buyabans.com/search?q={query}", enabled=False),
        ScrapeSourceConfig("simplytek-live-search", "SimplyTek", "https://www.simplytek.lk/search?q={query}", enabled=False),
    ]


class ConfigurableScrapeAdapter:
    def __init__(self, config: ScrapeSourceConfig) -> None:
        self.config = config
        self.meta = SourceMeta(
            name=config.name,
            site_name=config.site_name,
            base_url=config.base_url,
            enabled=config.enabled,
            timeout_seconds=config.timeout_seconds,
            source_type="live-html-scraper",
        )

    def search_raw(self, item: ResearchItem, limit: int = 10) -> list[RawListing]:
        if not self.config.enabled:
            return []
        html = fetch_html(self.config, item.name)
        return extract_listings(html, self.config, item, limit=limit)
