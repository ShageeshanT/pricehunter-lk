# PriceHunter LK Five Phase Build Plan

PriceHunter LK is a universal price range finder. The user enters an item name and the app returns the cheapest and most expensive prices found across supported sites.

The main product rule is intentionally simple: no spreadsheet-first flow, no bloated comparison table by default, no procurement essay. Just the two extremes with enough proof to trust them.

## Phase 1: Premium MVP Shell and Interaction Flow

Goal: make the product feel like a real polished site, not a backend wearing a Halloween costume.

### Features

- Public landing page with strong product positioning.
- Single search box as the primary interaction.
- Two-card result layout:
  - Cheapest found
  - Most expensive found
- Source count indicator.
- Confidence score display.
- Loading state with smooth feedback.
- Empty state and no-result state.
- Mobile-first layout.
- GitHub/demo links.

### UI and smoothness

- Mantine UI provider and theme.
- Mantine Button, TextInput, Badge, Card, Container, Group, Stack, Paper, Loader, Skeleton, ActionIcon, Tooltip, RingProgress, ThemeIcon, SimpleGrid.
- Framer-motion-style CSS transitions without adding heavy animation dependency yet.
- Glassmorphism cards.
- Gradient background blobs.
- Hover lift on result cards.
- Focus ring and keyboard accessibility.
- Responsive spacing and typography.

### Acceptance criteria

- User can type an item and see min/max result cards.
- UI feels premium on phone and desktop.
- Page does not jump awkwardly during loading.
- Build passes.

## Phase 2: Real Search Adapter Layer

Goal: replace the local fixture illusion with real source adapters.

### Features

- Source adapter interface:
  - search(itemName)
  - normalizeProduct(raw)
  - extractPrice(raw)
  - source metadata
- Multiple source types:
  - Direct ecommerce adapter
  - Search-engine based adapter
  - HTML page adapter
  - Manual fallback adapter
- Per-source timeout.
- Per-source retry policy.
- Result deduplication by title, URL, and normalized price.
- Store domain whitelist.
- Robots/rate-limit friendly fetch policy.

### Data extracted

- Site name
- Product title
- Price
- Currency
- URL
- Availability if visible
- Timestamp
- Confidence score
- Extraction method

### Acceptance criteria

- At least 3 real or semi-real source adapters can return candidates.
- Bad source failure does not break the whole search.
- Search completes within a reasonable timeout.

## Phase 3: Ranking, Validation, and Trust Layer

Goal: stop the app from returning garbage prices with a straight face like a LinkedIn influencer.

### Features

- Query normalization:
  - brand/model tokens
  - unit tokens
  - synonym expansion
  - typo tolerance
- Relevance scoring:
  - token overlap
  - title similarity
  - category hints
  - exact model match boost
  - suspicious mismatch penalty
- Price validation:
  - currency normalization to LKR
  - outlier detection
  - impossible price warnings
  - duplicate listing collapse
- Confidence labels:
  - high confidence
  - medium confidence
  - needs manual check
- Result proof drawer/modal:
  - title
  - URL
  - matched tokens
  - extraction source

### UI and smoothness

- Animated confidence ring.
- Expandable proof panel using Mantine Collapse/Drawer.
- Toast notifications for partial source failure.
- Skeleton cards while validating.

### Acceptance criteria

- App does not pick unrelated products as min/max when better matches exist.
- User can see why a result was selected.
- Suspicious prices are flagged, not silently trusted.

## Phase 4: Product Experience and History

Goal: make the app sticky and useful beyond one search.

### Features

- Recent searches saved locally.
- Popular Sri Lankan product shortcuts.
- Compare previous search result with current result.
- Shareable result link.
- Copy result summary.
- Price alert placeholder flow:
  - notify if cheapest price goes below target
- Optional category filters:
  - electronics
  - stationery
  - groceries
  - fashion
  - home appliances
- Optional region/store filter.

### UI and smoothness

- Mantine Tabs for Search, Recent, Alerts.
- Mantine Modal for share/copy result.
- Animated recent-search chips.
- Command-palette style search shortcut later.
- Light/dark theme toggle if useful.

### Acceptance criteria

- User can search repeatedly without retyping common items.
- Results can be copied or shared easily.
- UX remains simple and not dashboard-bloated.

## Phase 5: Production Platform

Goal: deploy as a real product with reliable infrastructure.

### Features

- Backend API deployment.
- Frontend deployment.
- Cache layer for repeated searches.
- Background refresh jobs.
- Source health monitoring.
- Admin source configuration.
- Basic analytics:
  - most searched items
  - source response time
  - search success rate
  - no-result rate
- Abuse protection:
  - rate limits
  - bot protection
  - per-IP caps
- Logging and audit trail.

### Technical polish

- E2E tests for search flow.
- API contract tests.
- Source adapter tests with fixtures.
- Error monitoring.
- Environment config docs.
- Deployment docs.

### Acceptance criteria

- Production URL works.
- Search is stable under normal user load.
- Source failures are visible to admin and graceful to users.
- The product feels fast, smooth, and trustworthy.
