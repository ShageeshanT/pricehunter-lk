# PriceHunter LK Project Plan

PriceHunter LK is a Sri Lankan price research assistant that turns messy event or procurement item lists into sourced vendor comparisons, confidence scores, and Google Sheets-ready budgets.

## Product goal

Help students, clubs, event teams, and small businesses quickly research prices from Sri Lankan vendors without manually copying product names, links, estimates, and notes into spreadsheets.

## Complete working model target

By end of day the app should provide a full local workflow:

1. Accept an item list through CLI and API.
2. Normalize item names and quantities.
3. Search configured vendor sources or sample/local source fixtures.
4. Extract candidate prices, currency, vendor, URL, and notes.
5. Rank candidates by relevance and confidence.
6. Produce a comparison report.
7. Export CSV and Google Sheets-ready rows.
8. Include tests and documentation.

## Phase 1: Foundation

Status: in progress

Deliverables:

- Repository scaffold
- Python package layout
- CLI entrypoint
- FastAPI app
- Core domain models
- Sample vendor source fixtures
- Basic tests

## Phase 2: Research engine

Deliverables:

- Item parser
- Vendor source abstraction
- Fixture source for deterministic tests
- Search query builder
- Price parsing and LKR normalization
- Candidate ranking and confidence scoring

## Phase 3: Reporting and exports

Deliverables:

- CSV export
- JSON report export
- Google Sheets-ready value matrix
- Budget summary totals
- Missing or low confidence item flags

## Phase 4: API and UX

Deliverables:

- FastAPI endpoints for research jobs
- Request and response schemas
- Health endpoint
- Example item list
- Clear README usage

## Phase 5: Real vendor adapters

Deliverables:

- Pluggable HTTP source adapter
- Robots/rate-limit friendly fetch layer
- Optional Brave/search integration later
- Vendor notes for Sri Lankan shops

## Phase 6: Polish

Deliverables:

- More tests
- Better docs
- Demo data
- Release checklist
- Optional Google Sheets push integration through Composio

## Definition of done for MVP

- CLI can run a research job from a text file.
- API can run the same research job.
- Output includes candidate prices and recommended price per item.
- CSV export works.
- Tests pass.
- Repo is pushed to GitHub with meaningful commits.
