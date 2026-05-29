# Phase 2: Source Adapter Layer

Phase 2 turns PriceHunter LK from a polished UI demo into a backend with a real adapter architecture.

## What this phase adds

- `PriceAdapter` abstraction for all future sources.
- Source metadata with site name, timeout, retry count, and source type.
- Raw listing shape before normalization.
- Normalized `PriceCandidate` output shared by all adapters.
- Source health reporting per search.
- Candidate deduplication by vendor, title, and price.
- Price parsing for common Sri Lankan formats like `Rs. 1,450` and `LKR 5,850.50`.
- Relevance scoring using query token overlap and string similarity.
- Fixture adapters representing multiple Sri Lankan source groups.
- Search URL handoff adapter for stores where scraping is not yet enabled.
- Basic HTML link parser adapter for future allowed static pages.

## Why fixtures still exist

The first working model must be stable and testable. Real ecommerce pages often block automated scraping, change markup, or require browser rendering. Phase 2 therefore creates the adapter layer now, keeps deterministic fixtures for product behavior, and gives us clean slots to add real site-specific adapters in Phase 3 without wrecking the UX.

## Current default source groups

- Daraz LK fixture group
- Sri Lankan tech retailers fixture group
- Home and office stores fixture group

## API impact

`POST /price-range` now returns:

- cheapest result
- most expensive result
- number of active sources
- candidate count
- per-source health
- warnings if a source fails

## Next adapter targets

- Daraz search result parser or safe search handoff
- Singer search result parser
- Abans or SimplyTek parser where allowed
- Google/Brave search API based candidate discovery
- Store whitelist and source config file
