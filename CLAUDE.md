# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Project Alpha is the owner's primary sandbox for exploring and learning Claude Code. Expect experimental, in-progress work. There is no build system, package manager, or server — all files run directly in the browser.

## Games

All games must live in the `Games/` folder — always move or create game files there. When working on any game, commit and push to GitHub regularly throughout the session with clean, descriptive commit messages. Don't batch everything into one end-of-session commit; commit at logical milestones (initial scaffold, feature added, bug fixed, design updated, etc.).

## Running Files

Open any HTML file directly in a browser:
```
start "" "Games/set.html"
```

## Structure

- `Games/` — Browser-based games. Currently contains `set.html`, a two-player SET card game.
- `Main/` — Main project area (currently empty).
- `Utility/` — Non-game automation and config. Contains the Workum wind forecast skill, its config reference, and the Service Scheduler.

## Utility/workum-wind

Automated Monday wind forecast for Workum (IJsselmeer, NL). Uses the `/workum-wind` skill. Config and full reference (location, wind filters, calendar IDs, API URL) live in `Utility/workum-wind-config.md`. The scheduled trigger ID is `trig_012qMtXoRFMgBgh59prpDGpv` (runs 08:00 Amsterdam / 06:00 UTC every Monday). A 2-day pre-check trigger is auto-created for each calendar event to re-validate conditions.

## Utility/service-scheduler.html

Single-file browser tool for planning customer service trips. No server or build step — open directly in the browser. Uses SheetJS (`xlsx@0.18.5` via jsDelivr CDN) for Excel parsing and Nominatim (OpenStreetMap) for geocoding.

### What it does
The user is a service technician who drives from **Boerakker** each morning to service medical lifting equipment (plafondliften, tilliften, opstahulpen) at customer homes. The tool reads a customer Excel sheet and produces a day-by-day route schedule optimised for travel efficiency and due-date urgency.

### Five-screen flow
1. **Upload** — drag-and-drop `.xlsx`
2. **Column mapping** — map Excel columns to fields; auto-detects Dutch names (`Naam`, `Postcode`, `Adres`, `Telefoonnummer`, `Laatst gekeurd`, `Type hulpmiddel`)
3. **Config** — home location (default `Boerakker, Netherlands`), workday hours (08:00–17:00), service times (setup per customer + time per device), start date, working days
4. **Geocoding** — async Nominatim lookup per unique postal code, 1.1 s rate limit, results cached in `localStorage` key `ss_geo_v2`; "Cache wissen" button forces re-lookup
5. **Schedule** — timeline view per day with actual clock times, drive legs, and all devices per stop; CSV export

### Key data model
- **`AppState.customers[]`** — one entry per Excel row (one device)
- **`AppState.visits[]`** — customers grouped by `(name + postalCodeFull)`: one stop per unique person/location; `devices[]` array lists all their equipment
- **`AppState.schedule[]`** — array of day objects: `{ date, stops[{visit, travelMin}], returnMin, totalMin }`

### Service time model
`visitServiceMin(visit) = config.setupMin + visit.devices.length × config.deviceMin`
Defaults: 10 min setup + 20 min per device. Both configurable in the config screen.

### Scheduling algorithm (`buildSchedule`)
1. Sort visits by urgency (`nextDueDate` ascending, nulls last)
2. Each day: seed = most urgent unscheduled visit; then greedily add the **nearest** remaining visit that still allows return home within the daily budget (nearest-neighbour TSP)
3. `nextDueDate` = `lastServiceDate + 1 year` (computed; no separate column in the Excel)

### Travel time model (`travelMin`)
Haversine straight-line × road factor ÷ speed:
- < 15 km → factor 1.4, 40 km/h (urban)
- 15–50 km → factor 1.3, 75 km/h
- > 50 km → factor 1.15, 105 km/h (highway)

### Excel format (`Utility/Example.xlsx`)
Columns (in order): `gepland voor keuring` (empty/unused), `Laatst gekeurd` (Excel serial date), `Telefoonnummer`, `Email`, `Postcode` (e.g. `1012JS`), `Adres`, `Naam`, `Type hulpmiddel`. Multiple rows per customer are normal (one per device) — they get merged into one visit stop.

### Known design decisions
- Postal code column is preferred over regex-extraction from address
- `postalCodeFull` (e.g. `1012JS`) is used as the geocoding key; `postalCode` (4-digit prefix, e.g. `1012`) is the fallback
- Customers with no resolvable coordinates appear in an "Niet ingepland" section at the bottom
- The tool is entirely client-side; no backend, no API keys required

## Games/set.html

Single-file vanilla HTML/CSS/JS implementation of the card game SET for two players. All logic, styles, and markup live in one file — no external dependencies except the Inter font (Google Fonts CDN).

Key internals:
- Cards are represented as 4-tuples `[number, color, shading, shape]` (each 0–2), giving 81 unique cards.
- `isValidSet(a, b, c)` — validates a SET by checking each attribute is all-same or all-different.
- `cardSVG(card)` — renders a card as an inline SVG using shared `<pattern>` defs for striped shading.
- Game state: `deck`, `board`, `scores`, `claimingPlayer`, `selected`, timer via `setInterval`.
- Claim flow: player presses Q or P → 8-second countdown starts → player clicks 3 cards → `evaluateSelected()` resolves.
