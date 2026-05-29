from pricehunter.scraping import ScrapeSourceConfig, extract_json_ld_listings, extract_listings, extract_text_price_listings
from pricehunter.models import ResearchItem


def test_extract_json_ld_product_offer():
    html = '''
    <html><head><script type="application/ld+json">
    {"@type":"Product","name":"Wireless Mouse Silent Click","url":"https://shop.lk/mouse","offers":{"price":"1450","availability":"InStock"}}
    </script></head></html>
    '''
    config = ScrapeSourceConfig("test", "Test Shop", "https://shop.lk/search?q={query}", enabled=True)
    listings = extract_json_ld_listings(html, config, ResearchItem(name="wireless mouse"))
    assert len(listings) == 1
    assert listings[0].title == "Wireless Mouse Silent Click"
    assert listings[0].price == 1450


def test_extract_text_price_context():
    html = "<html><body><div>Premium Rice Cooker 1.8L Rs. 9,990</div></body></html>"
    config = ScrapeSourceConfig("test", "Test Shop", "https://shop.lk/search?q={query}", enabled=True)
    listings = extract_text_price_listings(html, config, ResearchItem(name="rice cooker"))
    assert listings
    assert listings[0].price == 9990


def test_extract_listings_combines_extractors():
    html = '''
    <script type="application/ld+json">
    {"@type":"Product","name":"Bluetooth Speaker Mini","offers":{"price":"6490"}}
    </script>
    <div>Bluetooth Speaker Waterproof LKR 18990</div>
    '''
    config = ScrapeSourceConfig("test", "Test Shop", "https://shop.lk/search?q={query}", enabled=True)
    listings = extract_listings(html, config, ResearchItem(name="bluetooth speaker"), limit=5)
    assert len(listings) >= 2
    assert {listing.raw["extractor"] for listing in listings} >= {"json-ld", "text-price-context"}
