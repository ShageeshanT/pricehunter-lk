# PriceHunter LK

Sri Lankan price research assistant for event budgets, procurement lists, and student club planning.

PriceHunter LK takes an item list such as files, pens, wrist bands, plaques, stickers, refreshments, or OC tags, finds matching price candidates from configured sources, ranks them, and exports a clean budget comparison.


## Main product flow

PriceHunter LK is a universal item price range finder. It is not only for events or Young Protege budgets.

User enters an item name. The app returns only:

1. Cheapest site name, price, and URL
2. Most expensive site name, price, and URL

CLI:

```bash
pricehunter range "A4 file"
```

API endpoint:

`POST /price-range` with JSON body `{ "item_name": "A4 file" }`

## MVP status

Active build. The current model is local-first and deterministic so it can be tested reliably before live vendor search is added.

## Planned workflow

```bash
pricehunter examples/young_protege_items.txt --csv out/budget.csv --json out/report.json
```

## API preview

```bash
uvicorn pricehunter.api:app --reload
```

Then POST to `/research` with:

```json
{
  "items": [
    {"name": "A4 file", "quantity": 100},
    {"name": "blue pen", "quantity": 100}
  ]
}
```

## Why this exists

Manual price research is slow, messy, and weirdly good at eating entire nights. This tool is meant to turn that chaos into a spreadsheet before the spreadsheet starts demanding blood sacrifice.


## Current MVP command

```bash
python -m pip install -e ".[dev]"
pytest
pricehunter examples/young_protege_items.txt --csv out/budget.csv --json out/report.json
```

Sample output total for the included Young Protege-style list: LKR 157500.

## Phased roadmap

See `PROJECT_PLAN.md` for the end-of-day build phases.


## Frontend

The polished web UI lives in `web/` and uses Next.js, Tailwind, Mantine UI, Mantine notifications, and Tabler icons.

```bash
cd web
npm install
npm run dev
```

The UI currently uses deterministic mock results while the backend source adapters are upgraded to real ecommerce/search adapters.
