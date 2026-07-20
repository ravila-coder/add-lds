# Loads — Institutional Reporting Platform (Addem Capital)

Static single-page monitoring dashboard for the Loads relationship (Loads USA, Inc.
consolidated; loan tape across all Loads business units, USD). Same architecture as
the Asaak platform: a Python ETL builds `etl/dashboard_data.json`, which is injected
into `app/template.html` to produce a fully self-contained `index.html`.

## Contents
- `index.html` — deployable app (data embedded, chart.js vendored, no external calls)
- `app/template.html` — UI shell with `/*__DATA__*/` marker
- `app/vendor/chart.umd.min.js` — vendored Chart.js
- `etl/loan_tape_etl.py` — parses `sources/loan_tape.xlsx` (Loan Tape, expected_payments,
  actual_payments) → `loads_loan_tape.json`
- `etl/financials_etl.py` — parses the consolidated FY2025/FY2024 statements →
  `loads_financials.json`
- `etl/build_dashboard_data.py` — merges tape + financials + credit-manual and
  investment-memo fact sheets + workspace seed → `dashboard_data.json`
- `etl/build_app.py` — runs the chain and writes `index.html`
- `sources/` — raw inputs as received

## Build
```
pip install openpyxl
python3 etl/build_app.py
```

## Deploy (Vercel)
1. Push the folder to a GitHub repo (drag & drop works).
2. Vercel → New Project → import repo → Framework preset: **Other** → Deploy.
`vercel.json` serves `index.html` at the root. Login: `Addem` / `Addem12345`.

## Methodology notes
- Outstanding = `totalDueAmount` per open order. DPD is measured net of the 30-day
  commercial grace period standard to Loads' payment terms: effective DPD =
  max(0, `overDueDays` − 30). The first 30 days are not arrears; raw `overDueDays`
  is retained per order. Buckets, PAR, provision and status all use effective DPD.
- Financed volume = `totalWithAdjustments`; trade margin computed on gross order value.
- Provision grid per Credit Manual 2026: 0% ≤60d · 0.5% 61–90 · 10% 91–120 ·
  25% 121–150 · 65% 151–180 · 100% >180. NPL defined as >180 DPD.
- Segments: total book and `loads_finance` business unit, each split active/closed.
- FY2025 financials are pre-audit ("PRE ESTADO") — flagged as preliminary in-app.
- The FACILITY tab reflects the indicative SPV structure from the 2Q2025 investment
  memo; no executed Addem facility exists yet, so all terms are marked indicative.
- As-of date is derived from the tape (currently 2026-06-21).

## Monthly update cycle
See `HOW_TO_UPDATE.txt`.
