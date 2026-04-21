---
name: electricity
description: >
  Monthly electricity payment calculator for Daniel's rental in Groningen.
  Use this skill whenever the user asks to run `/electricity`, calculate this month's electricity bill,
  log a new meter reading, record the landlord's price-per-kWh for the month, figure out how much to
  pay the landlord for electricity, process the latest Energierapport, or set the initial baseline
  meter reading.
  The skill automatically fetches the latest "Fwd: Maandelijks Energierapport" email from Gmail
  (sender info@prblom.nl, Pure Energie forwarded by landlord Pieter Blom), parses the Dutch tariff
  breakdown, asks for the current kWh meter reading, computes usage × effective rate, updates the
  state file, and reports the amount owed.
---

# Electricity Payment Skill

Run this skill whenever a new monthly electricity report arrives from the landlord. It reads the latest "Energierapport" email automatically from Gmail, extracts the tariffs, takes Daniel's current meter reading, and computes what he owes Pieter Blom.

## Quick reference

| Parameter | Value |
|-----------|-------|
| State file | `Project Alpha/Utility/electricity/electricity-state.json` |
| Reports archive | `Project Alpha/Utility/electricity/reports/` |
| Config reference | `Project Alpha/Utility/electricity/electricity-config.md` |
| Landlord email sender | `info@prblom.nl` (Pieter Blom) |
| Energy supplier | Pure Energie (`info@pure-energie.nl`) |
| Subject pattern | `Fwd: Maandelijks Energierapport <month> <year>` |
| Currency | EUR |
| Language | Dutch (report), responses in English |
| Rounding | Amounts to 2 decimals; kWh used to 1 decimal |

## Core formula

```
effective_price_per_kwh = tarief_levering + energiebelasting
kwh_used    = current_reading - previous_reading
amount_owed = kwh_used × effective_price_per_kwh
```

This is the variable cost per kWh consumed (delivery tariff + energy tax, BTW inclusive). Fixed costs (netbeheer, leveringskosten, vermindering energiebelasting) are the landlord's responsibility — Daniel only pays for the electricity he actually uses.

If Daniel and Pieter agree a different formula (e.g. include/exclude energy tax), the skill can be told once and it will remember the preference.

---

## Step-by-step workflow

### 0. Read current state

Read `Project Alpha/Utility/electricity/electricity-state.json`. The `readings[]` array is ordered oldest → newest. The last entry is the previous baseline (if any). Note `price_formula` if present — defaults to `"levering_plus_belasting"`.

### 1. Determine mode

- **Bootstrap mode** — if `readings[]` is empty. Only ask for the current meter reading. Do not fetch any email. Save a single reading entry with `kwh_used`, `price_per_kwh_eur`, `amount_owed_eur` all `null` and `notes` explaining this is the baseline. Tell the user no payment is due yet and the next run will produce the first bill.
- **Monthly mode** — if at least one reading exists. Proceed with the full flow below.

### 2. Fetch the latest report from Gmail

Use `search_threads` with query:

```
from:info@prblom.nl subject:Energierapport
```

Pick the most recent thread whose subject matches `Fwd: Maandelijks Energierapport <month> <year>`.

Check the state's `readings[]` — if the latest reading already references this same period (check `period_month`), tell the user the report has already been processed and ask whether to re-run or skip.

Fetch the full plaintext body with `get_thread` using `messageFormat: FULL_CONTENT`.

If no matching email is found, fall back to asking the user to paste the report text or attach a screenshot.

### 3. Parse the report (Pure Energie Dutch format)

Regex patterns below match the actual email body layout (verified against the 2026-03 archived report). Variable whitespace between field name and value is common — the report pads columns with spaces for visual alignment, so use `\s+` liberally.

| Field | Regex | Example match |
|-------|-------|---------------|
| `period_month_dutch` | `Periode:\s*(\w+\s+\d{4})` | `"maart 2026"` |
| `bruto_verbruik_kwh` | `Bruto elektraverbruik:\s*(\d+)\s*kWh` | `1570` |
| `bruto_teruglevering_kwh` | `Bruto teruglevering:\s*(\d+)\s*kWh` | `147` |
| `netto_verbruik_kwh` | `Netto elektraverbruik:\s*(\d+)\s*kWh` | `1423` |
| `verbruiksafhankelijke_kosten_eur` | `Verbruiksafhankelijke kosten:\s*€\s*([\d.,]+)` (first match) | `417,68` |
| `totale_kosten_eur` | `Totale kosten:\s*€\s*([\d.,]+)` (first match) | `411,03` |
| `tarief_levering_eur` | `tarief levering:\s*€([\d.,]+)\s*per\s*kWh` | `0,155193` |
| `tarief_teruglevering_eur` | `tarief teruglevering:\s*€([\d.,]+)\s*per\s*kWh` | `0,028976` |
| `energiebelasting_eur` | `Energiebelasting:\s*€([\d.,]+)\s*per\s*kWh` (electricity — anchor on `per kWh` so you don't pick up the gas `per m³` line) | `0,11085` |

Notes:
- Dutch uses `,` as decimal separator — convert to `.` before parsing as float (e.g. `"0,155193"` → `0.155193`).
- "Verbruiksafhankelijke kosten" and "Totale kosten" appear twice (electricity + gas); always take the **first** match, which is electricity.
- Gas lines (`per m³`) are ignored — Daniel doesn't pay for gas.
- Store period as `"YYYY-MM"` format internally (e.g. `"2026-03"` for "maart 2026").

**Dutch month map** (for `period_month_dutch` → `YYYY-MM`):

| Dutch | Number |
|-------|--------|
| januari | 01 |
| februari | 02 |
| maart | 03 |
| april | 04 |
| mei | 05 |
| juni | 06 |
| juli | 07 |
| augustus | 08 |
| september | 09 |
| oktober | 10 |
| november | 11 |
| december | 12 |

### 4. Compute the effective price

```
price_per_kwh_eur = tarief_levering_eur + energiebelasting_eur
```

Sanity check — flag if outside €0.15 – €0.45 (plausible 2025–2026 Dutch range).

### 5. Archive the report

Save the raw plaintext to `Project Alpha/Utility/electricity/reports/YYYY-MM.md` (using `period_month`). Include a header with the parsed fields:

```markdown
# Energierapport YYYY-MM

Source: Pure Energie (via info@prblom.nl Gmail thread <thread_id>)
Fetched: <today ISO>

Extracted tariffs:
- Tarief levering: €0.155193/kWh
- Energiebelasting: €0.11085/kWh
- Tarief teruglevering: €0.028976/kWh
- Effective price (levering + belasting): €0.266043/kWh

Household totals (landlord's account):
- Bruto verbruik: 1570 kWh
- Teruglevering: 147 kWh
- Netto verbruik: 1423 kWh
- Totale kosten: €411.03

---

<full plaintext body here>
```

### 6. Show the user what was extracted, and ask for the meter reading

Format a concise summary like:

```
📧 Found report: Fwd: Maandelijks Energierapport maart 2026 (sent 2026-04-20)

Tariffs for March 2026:
  Tarief levering:       €0.155193/kWh
  Energiebelasting:      €0.11085/kWh
  → Effective price:     €0.26604/kWh

Previous reading (2026-03-18): 12,345.0 kWh

What is your current meter reading?
```

### 7. Validate the meter reading

Prompt the user for the current reading in kWh. Accept decimal values. Validate:

- Must be **greater than** the previous reading. If lower, warn and ask to reconfirm (possibly a typo, a meter replacement, or a rollover).
- Must be a plausible monthly delta: 50–400 kWh is typical for a single person in a shared rental. Outside this range, flag it and ask the user to confirm before saving.

### 8. Compute and save

```
kwh_used    = round(current_reading - previous_reading, 1)
amount_owed = round(kwh_used × price_per_kwh_eur, 2)
```

Append a new reading entry with all fields:

```json
{
  "date": "2026-04-20",
  "period_month": "2026-03",
  "reading_kwh": 12567.4,
  "kwh_used": 222.4,
  "price_per_kwh_eur": 0.266043,
  "amount_owed_eur": 59.17,
  "tariffs": {
    "tarief_levering_eur": 0.155193,
    "tarief_teruglevering_eur": 0.028976,
    "energiebelasting_eur": 0.11085
  },
  "household_totals": {
    "bruto_verbruik_kwh": 1570,
    "teruglevering_kwh": 147,
    "netto_verbruik_kwh": 1423,
    "totale_kosten_eur": 411.03
  },
  "gmail_thread_id": "19daa3ecb8f378ea",
  "paid": false,
  "paid_on": null,
  "notes": ""
}
```

Write back the full state file, preserving `schema_version`, `currency`, `landlord_name`, `landlord_payment_details`, and `price_formula`.

**Write atomically.** Write the new JSON to `electricity-state.json.tmp` first, verify it parses as valid JSON, then rename/move it over `electricity-state.json`. If the write is interrupted, the original file is still intact and the `.tmp` can be inspected or discarded. Never overwrite the state file in place.

Each reading carries a `paid` boolean (default `false`) and `paid_on` date (ISO, or `null`). New entries default to `paid: false`. If the user later says things like "mark March paid" or "paid all", set `paid: true` and `paid_on` to today's ISO date on the matching entries.

**Schema migration:** current `schema_version` is `2` (added `paid` / `paid_on` to reading entries). If loading a file with `schema_version: 1` or readings missing the `paid` field, treat those readings as `paid: false` without rewriting them. Only migrate on the next normal save.

### 9. Report to the user

Before printing, compute rolling totals from `readings[]`:

- `ytd_kwh` — sum of `kwh_used` for readings in the current calendar year
- `ytd_paid_eur` — sum of `amount_owed_eur` where `paid == true`, current year
- `outstanding_eur` — sum of `amount_owed_eur` where `paid == false` (any year)
- `lifetime_kwh` — sum of all non-null `kwh_used`
- `lifetime_paid_eur` — sum of all paid `amount_owed_eur`

Output a clear summary:

```
Electricity bill — March 2026
─────────────────────────────
Previous reading (2026-03-18): 12,345.0 kWh
Current  reading (2026-04-20): 12,567.4 kWh
Usage this period:               222.4 kWh
Effective price per kWh:       €0.26604
  (levering €0.155193 + energiebelasting €0.11085)

💶 Amount owed to Pieter Blom: €59.17

Totals
  YTD (2026):       222.4 kWh · €0.00 paid · €59.17 outstanding
  Lifetime:         222.4 kWh · €0.00 paid

Saved as reading #N in electricity-state.json.
Report archived to Utility/electricity/reports/2026-03.md.
```

**Payment line.** If `landlord_payment_details` is set in state, append a ready-to-paste line **after** the totals block, formatted exactly like this:

```
💸 Payment: "Stroom maart 2026 — €59.17" → <landlord_payment_details>
```

Use the Dutch month name (not the ISO code) in the description string — it matches what Pieter will see in his bank feed. If `landlord_payment_details` is `null`, omit the payment line entirely.

---

## Editing a previous reading

If the user says they typed a reading wrong or wants to correct a past month, read the state file, edit the specific entry by `date` or `period_month`, recompute any downstream `kwh_used` (the next reading depends on this one), and write back. Always confirm the change with the user before saving.

## Setting landlord details

If the user ever says "my landlord's IBAN is X" or "send to Tikkie link Y", update `landlord_name` and `landlord_payment_details` in the state file.

## Changing the price formula

If the user wants a different formula (e.g. only tarief_levering without energy tax, or the all-in total_costs / netto_kwh), set `price_formula` in state to one of:

- `"levering_plus_belasting"` (default) — `tarief_levering + energiebelasting`
- `"levering_only"` — just `tarief_levering`
- `"all_in"` — `totale_kosten / netto_verbruik` (includes fixed costs proportionally)

Apply the chosen formula going forward. Do NOT retroactively rewrite old readings unless explicitly asked.

## Error handling

- **Gmail auth failure:** Report it. Fall back to asking the user to paste the report text.
- **State file missing or corrupt:** Do not overwrite blindly. Show the user what's there and ask before resetting.
- **Price looks wrong (e.g. €28 per kWh instead of €0.28):** Flag it. Most Dutch rates in 2025–2026 are in the €0.15–€0.40 range.
- **Negative usage:** Stop and ask — likely a typo or a reset meter. Never save a negative `kwh_used`.
- **Report already processed:** If the latest entry's `period_month` matches the fetched email's period, tell the user and ask to confirm re-processing.

## Notes

- All dates in ISO format (YYYY-MM-DD), timezone Europe/Amsterdam.
- All monetary values in EUR, tariffs stored with full precision (6 decimals), amounts rounded to cents.
- A monthly reminder fires on the **22nd of each month at 09:00 Amsterdam time** (trigger id: `electricity-monthly-reminder`) prompting Daniel to read his meter and run `/electricity`. The actual processing is still manual / interactive — the trigger only nudges.
