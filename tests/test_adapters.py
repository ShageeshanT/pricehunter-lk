from decimal import Decimal

from pricehunter.adapters import RawListing, clean_text, dedupe_candidates, normalize_listing, parse_price, relevance_score
from pricehunter.models import PriceCandidate, ResearchItem
from pricehunter.source_registry import default_adapters


def test_parse_price_supports_lkr_formats():
    assert parse_price("Rs. 1,450") == Decimal("1450")
    assert parse_price("LKR 5,850.50") == Decimal("5850.50")
    assert parse_price("4900") == Decimal("4900")


def test_normalize_listing_scores_relevant_titles():
    item = ResearchItem(name="wireless mouse")
    candidate = normalize_listing(
        item,
        RawListing(
            source_name="test",
            site_name="Test Store",
            title="Wireless Mouse 2.4GHz",
            price=Decimal("1450"),
            url="https://example.lk/item",
        ),
    )
    assert candidate.vendor == "Test Store"
    assert candidate.confidence > 0.75


def test_dedupe_candidates_keeps_unique_vendor_title_price():
    candidate = PriceCandidate(item_name="mouse", vendor="A", title="Wireless Mouse", price=Decimal("1000"), confidence=0.9)
    duplicate = PriceCandidate(item_name="mouse", vendor="A", title="Wireless Mouse", price=Decimal("1000"), confidence=0.8)
    different = PriceCandidate(item_name="mouse", vendor="B", title="Wireless Mouse", price=Decimal("1000"), confidence=0.7)
    assert dedupe_candidates([candidate, duplicate, different]) == [candidate, different]


def test_default_adapters_return_multiple_sources():
    adapters = default_adapters()
    assert len(adapters) >= 3
    assert {adapter.meta.site_name for adapter in adapters}


def test_clean_text_and_relevance_score():
    assert clean_text("  A4\xa0 File   ") == "A4 File"
    assert relevance_score("rice cooker", "Premium Rice Cooker") > relevance_score("rice cooker", "Wireless Mouse")
