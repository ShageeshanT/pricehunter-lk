from __future__ import annotations

from .adapters import FixtureAdapter, PriceAdapter, SearchUrlAdapter

DARAZ_FIXTURES = [
    {"title": "Wireless Mouse 2.4GHz Silent Click", "price": "Rs. 1,450", "url": "https://www.daraz.lk/catalog/?q=wireless+mouse", "availability": "in stock"},
    {"title": "Bluetooth Speaker Portable Bass", "price": "Rs. 6,490", "url": "https://www.daraz.lk/catalog/?q=bluetooth+speaker", "availability": "in stock"},
    {"title": "USB C iPhone Charger 20W", "price": "Rs. 4,900", "url": "https://www.daraz.lk/catalog/?q=iphone+charger", "availability": "in stock"},
    {"title": "A4 Plastic File Folder", "price": "Rs. 80", "url": "https://www.daraz.lk/catalog/?q=a4+file", "availability": "in stock"},
    {"title": "1.8L Electric Rice Cooker", "price": "Rs. 8,650", "url": "https://www.daraz.lk/catalog/?q=rice+cooker", "availability": "in stock"},
]

TECH_FIXTURES = [
    {"title": "Premium Wireless Mouse Rechargeable", "price": "LKR 5,850", "url": "https://www.simplytek.lk/search?q=wireless+mouse", "availability": "store listing"},
    {"title": "Gaming Mouse RGB Wired", "price": "LKR 7,200", "url": "https://redlinetech.lk/?s=gaming+mouse", "availability": "store listing"},
    {"title": "Original Fast iPhone Charger Adapter", "price": "LKR 11,900", "url": "https://example.lk/premium-charger", "availability": "store listing"},
    {"title": "Portable Bluetooth Speaker Waterproof", "price": "LKR 18,990", "url": "https://www.buyabans.com/search?q=bluetooth+speaker", "availability": "store listing"},
]

HOME_FIXTURES = [
    {"title": "Premium Fuzzy Logic Rice Cooker", "price": "Rs. 32,990", "url": "https://www.singer.lk/catalogsearch/result/?q=rice+cooker", "availability": "retail listing"},
    {"title": "Rice Cooker 1.8L Basic Model", "price": "Rs. 9,990", "url": "https://www.singer.lk/catalogsearch/result/?q=rice+cooker", "availability": "retail listing"},
    {"title": "Plastic A4 File Clear", "price": "Rs. 140", "url": "https://example.lk/stationery/a4-file", "availability": "office supply listing"},
]


def default_adapters(include_search_handoffs: bool = False) -> list[PriceAdapter]:
    adapters: list[PriceAdapter] = [
        FixtureAdapter("daraz-fixture", "Daraz LK", DARAZ_FIXTURES),
        FixtureAdapter("tech-retail-fixture", "Sri Lankan Tech Retailers", TECH_FIXTURES),
        FixtureAdapter("home-office-fixture", "Home and Office Stores", HOME_FIXTURES),
    ]
    if include_search_handoffs:
        adapters.extend(
            [
                SearchUrlAdapter("daraz-search", "Daraz LK", "https://www.daraz.lk/catalog/?q={query}"),
                SearchUrlAdapter("singer-search", "Singer", "https://www.singer.lk/catalogsearch/result/?q={query}"),
                SearchUrlAdapter("google-shopping-handoff", "Web Search", "https://www.google.com/search?q={query}+price+Sri+Lanka"),
            ]
        )
    return adapters
