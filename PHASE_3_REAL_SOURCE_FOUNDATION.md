# Phase 3: Real Source Scraping Foundation

Phase 3 adds the first serious live-source foundation without pretending unreliable scraping is already magic.

## Research notes from strong scraper projects

Useful ideas to reuse from popular scraper ecosystems:

- Scrapy: source pipelines, retry boundaries, explicit request settings, and per-source spiders.
- Crawlee / Apify style crawlers: concurrency limits, session management, browser fallback, and dataset outputs.
- Crawl4AI: clean markdown/text extraction for LLM-friendly downstream processing.
- Scrapling: resilient selectors and adaptive element matching when markup changes.
- Playwright: browser rendering fallback for JavaScript-heavy ecommerce pages.
- BeautifulSoup / selectolax style parsing: fast static HTML extraction before using heavy browser automation.

Phase 3 implements the safe local version of those ideas: config-driven sources, robots-aware fetching, structured extractors, source health, and clean adapter boundaries.

## Implemented now

- `ScrapeSourceConfig` for configured ecommerce search pages.
- `ConfigurableScrapeAdapter` for live HTML source fetching.
- Robots.txt check before fetching live source URLs.
- Request timeouts and max byte caps.
- HTML parser for text and link extraction.
- JSON-LD product/offer extraction.
- Text price context extraction for common `Rs` and `LKR` patterns.
- Live scraper adapter registration.
- API `live` flag on `/price-range` to include live source adapters.

## Important default behavior

Live scraper configs are currently registered but disabled by default. This keeps tests, demos, and UI fast and deterministic.

To enable real scraping safely in a later phase:

1. Add a source config with `enabled=True`.
2. Confirm the site's robots.txt and terms allow the requested fetch behavior.
3. Add a source-specific parser test using saved HTML fixtures.
4. Add rate limits and cache before scaling requests.

## Planned Phase 6 and 7 scope

### Phase 6: Production scraping engine

- Async HTTP client with connection pooling.
- Per-domain rate limiter.
- Retry with backoff.
- Disk or SQLite cache for recent searches.
- Source-specific parser fixtures.
- Search API fallback using Brave or other approved APIs.
- More Sri Lankan stores and marketplaces.

### Phase 7: Browser and accuracy layer

- Playwright fallback for JavaScript-heavy pages.
- Selector resilience inspired by Scrapling-style matching.
- Product validation against title, breadcrumbs, image alt text, and structured data.
- Outlier filtering and duplicate cluster detection.
- Confidence explanation per result.
- Source reliability scoring.

## Accuracy policy

PriceHunter should not claim a price is accurate unless it has a source URL, extraction method, timestamp, and confidence reason. If the source blocks scraping or the match is weak, the UI should say so instead of hallucinating a bargain like a coupon goblin on Red Bull.
