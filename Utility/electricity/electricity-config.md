# Electricity Payment Skill — Config & Reference

This file documents the monthly electricity payment automation for Daniel's rental at RUG (Groningen).

## What it does

Every month the landlord (Pieter Blom, `info@prblom.nl`) forwards a "Fwd: Maandelijks Energierapport" from Pure Energie. Daniel reads his current meter, and the `/electricity` skill:

1. Auto-fetches the latest matching email from Gmail,
2. Parses the Dutch tariff breakdown (`tarief levering`, `energiebelasting`, etc.),
3. Computes `amount_owed = (current − previous) × (tarief_levering + energiebelasting)`,
4. Stores the new reading (including full tariff breakdown for audit),
5. Reports the amount owed.

## Files

| File | Purpose |
|------|---------|
| `electricity-state.json` | Full reading history + current baseline. Updated every run. |
| `reports/YYYY-MM.md` | Saved copy of each landlord report (text) for audit. |
| `reports/YYYY-MM.png` (optional) | Saved screenshot, if the report came as an image. |

## State file schema

```json
{
  "schema_version": 2,
  "currency": "EUR",
  "landlord_name": "Name of landlord (optional)",
  "landlord_payment_details": "IBAN / Tikkie link / etc. (optional)",
  "readings": [
    {
      "date": "2026-04-20",
      "reading_kwh": 12345.0,
      "kwh_used": null,
      "price_per_kwh_eur": null,
      "amount_owed_eur": null,
      "period_start": null,
      "period_end": null,
      "notes": "Initial bootstrap reading — no payment due."
    },
    {
      "date": "2026-05-18",
      "reading_kwh": 12567.4,
      "kwh_used": 222.4,
      "price_per_kwh_eur": 0.2805,
      "amount_owed_eur": 62.38,
      "period_start": "2026-04-01",
      "period_end": "2026-04-30",
      "paid": false,
      "paid_on": null,
      "notes": ""
    }
  ]
}
```

Rounding: amounts in EUR are rounded to 2 decimals. Each reading tracks `paid` (bool) and `paid_on` (ISO date or null) so outstanding vs settled months can be told apart.

**Schema migration (v1 → v2):** v2 adds `paid` and `paid_on` fields to each reading. When loading a v1 file, any reading missing `paid` is treated as `paid: false` and is only rewritten on the next normal save.

**Atomic writes:** the skill always writes to `electricity-state.json.tmp` and renames over `electricity-state.json` so an interrupted write can't corrupt history.

## Core formula

```
effective_price_per_kwh = tarief_levering + energiebelasting
kwh_used                = current_reading - previous_reading
amount_owed             = kwh_used × effective_price_per_kwh
```

This is the variable per-kWh cost (delivery tariff + energy tax, BTW inclusive). Fixed costs (netbeheer, leveringskosten, vermindering energiebelasting) are the landlord's responsibility. The formula can be changed via `price_formula` in state: `"levering_plus_belasting"` (default), `"levering_only"`, or `"all_in"` (`totale_kosten / netto_verbruik`).

## Gmail source

- **Sender:** `info@prblom.nl` (Pieter Blom, forwarded from Pure Energie)
- **Subject pattern:** `Fwd: Maandelijks Energierapport <dutch-month> <year>`
- **Gmail search query:** `from:info@prblom.nl subject:Energierapport`
- **Report arrives:** Around the 8th–20th of each month for the preceding month.

## Trigger

A scheduled reminder fires on the **22nd of each month at 09:00 Amsterdam time** (trigger id: `electricity-monthly-reminder`). It nudges Daniel to read his meter and run `/electricity` — the processing itself is still manual/interactive.

## Location

- **Skill:** `~/.claude/skills/electricity/SKILL.md` (user-level, not in the Project Alpha repo)
- **Data:** `Project Alpha/Utility/electricity/` (version-controlled in this repo)
