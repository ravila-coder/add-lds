"""Assemble etl/dashboard_data.json for the Loads reporting platform.

Merges the loan-tape and financials extracts, computes the credit-policy
compliance board (Manual de Credito 2026 + Loads Finance underwriting benchmarks
from the 2Q2025 Investment Memorandum), and attaches the facility / credit-manual
fact sheets, the data-room index and the Workspace seed.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    lt = json.loads((HERE / "loads_loan_tape.json").read_text(encoding="utf-8"))
    fin = json.loads((HERE / "loads_financials.json").read_text(encoding="utf-8"))
    segs = lt["segments"]
    tact = segs["total_active"]
    latest = fin[-1]

    policy = {
        "as_of": lt["as_of"],
        # Manual de Credito 2026 §6.2 expected-loss provisioning
        "expected_loss": tact["provision"]["expected_loss"],
        "net_receivable": tact["provision"]["net_receivable"],
        "provision_coverage": tact["provision"]["coverage_pct"],
        # Investment memo underwriting benchmarks (Loads Finance)
        "npl_pct": tact["credit_quality"]["npl"]["pct"],          # > 180 DPD definition
        "npl_target": 0.02,                                        # "NPL < 2%" memo benchmark
        "collection_rate": segs["total"]["collections"]["collection_rate"],
        "collection_benchmark": 0.869,                             # 86.9% collected on USD 11.2M memo book
        "wa_tenor_days": segs["total"]["weighted_averages"]["wa_tenor_days"],
        "tenor_benchmark_days": 33,                                # memo average credit cycle
        "min_advance_rate": 0.20,                                  # structured facility: minimum 20% retention
        "importer_top1": lt["concentration"]["importers_active_ob"][0],
        "servicer_debt_to_equity": latest["ratios"]["debt_to_equity"],
        "servicer_equity": latest["bs"]["total_equity"],
        "provision_grid": [
            {"bucket": "1–30 days past due", "rate": 0.0},
            {"bucket": "31–60 days past due", "rate": 0.0},
            {"bucket": "61–90 days past due", "rate": 0.005},
            {"bucket": "91–120 days past due", "rate": 0.10},
            {"bucket": "121–150 days past due", "rate": 0.25},
            {"bucket": "151–180 days past due", "rate": 0.65},
            {"bucket": "> 180 days past due", "rate": 1.0},
        ],
    }

    contracts = {
        "FACILITY": {
            "name": "Loads Finance SPV — Structured Trade-Receivables Facility (indicative)",
            "status": "Indicative — under structuring; no executed Addem credit agreement in the data room",
            "borrower": "Loads Finance SPV (ring-fenced vehicle; Loads USA, Inc. platform)",
            "lender": "Addem Capital (prospective senior debt provider)",
            "obligor": "End importers — payment obligation sits with the buyer of each shipment",
            "structure": "Invoice assignment into a dedicated SPV at a pre-agreed discount; "
                          "importers repay at maturity (typically 30–45 days); the SPV pays "
                          "suppliers at the point of shipment",
            "equity_contribution": "Loads contributes 10–30% first-loss equity per structure "
                                    "(50–70% target annualized ROE on equity, 10–12 reinvestment cycles/yr)",
            "advance_rate": "Minimum 20% retention (advance ≤ 80% of the assigned invoice)",
            "discount_rate": "≈ 4% per transaction cycle (origination discount)",
            "annualized_yield": "≈ 35% – 40% annualized on deployed capital",
            "coupon_structure": "1–4 payments per order tied to operational milestones "
                                 "(invoice issuance, documents against payment, arrival, arrival + x days)",
            "typical_ticket": "≈ USD 40k (produce) · ≈ USD 200k (commodities)",
            "wal": "30 – 45 days weighted average life",
            "collateral": "Assigned trade receivables; goods in transit controlled through the "
                           "documentary set (negotiable Bill of Lading held to order)",
            "insurance": "100% freight insurance on every shipment; trade credit insurance "
                          "(post-Coface programme) with up to 90% coverage per qualified operation; "
                          "AVLA-approved lines substitute for missing importer financials",
            "assignment": "Cession of collection rights per order, released on full payment at close "
                           "(Manual de Credito FASE 5)",
            "funding_process": "Commercial Invoice is the disbursement trigger — the single document "
                                "required for the SPV to fund a shipment",
            "eligibility": [
                "Order approved through the four-block Credit Scoring (0–1000) with tier-driven payment structure",
                "Full documentary set required: Bill of Lading, Packing List, Commercial Invoice, "
                "Certificate of Origin, Phytosanitary Certificate",
                "Payment conditions tied to verifiable operational milestones (~20% advance / ~30% "
                "against documents / ~50% at destination as the reference structure)",
                "Tier E counterparties (score 0–151, no information or adverse signals) trade fully prepaid only",
                "New-client credit decision within 72h; new order for an existing client within 24h",
                "Non-payment triggers immediate suspension of new shipments to the counterparty",
            ],
            "concentration_limits": [
                {"limit": "Single-importer exposure (largest active receivable)", "threshold": "Monitored — no hard limit documented"},
                {"limit": "Tier E (fully-prepaid-only) share of financed volume", "threshold": "0% financed by policy"},
                {"limit": "Trade credit insurance coverage on qualified operations", "threshold": "Up to 90%"},
                {"limit": "Loads first-loss equity per SPV structure", "threshold": "10% – 30%"},
            ],
            "key_defaults": [
                "Importer non-payment past 90 days moves the account to judicial collection with external counsel",
                "Accounts are written off only when no reasonable recovery expectation remains, against the "
                "expected-loss provision",
                "Publication in the credit bureau evaluated case-by-case from 31 days past due",
            ],
            "reporting": [
                "Weekly delinquency segmentation from the Back Office order-control sheet "
                "(Preventive −7–0 · Administrative 1–30 · Extrajudicial 31–90 · Judicial 90+)",
                "Weekly Commercial Collections Committee (preventive/administrative buckets) and "
                "Judicial Committee (extrajudicial/judicial buckets) with per-account action plans",
                "Automated preventive and delinquency dunning from the finance platform",
                "Provision rates reviewed annually or on a material portfolio-mix change",
            ],
        },
        "MANUAL": {
            "name": "Manual de Crédito, Recuperación y Cobranza 2026",
            "status": "In force — signed by Larry Andrés Gil Bertucci, Legal Representative",
            "scope": "Single operating standard for Commercial, Back Office, Finance & Risk and "
                      "Collections across origination, execution and recovery",
            "origination": "Four-stage CRM (HubSpot) flow: client onboarding → order intake "
                            "(PO, proforma, incoterms, agency/transport costs, margin, payment terms) → "
                            "Finance runs the Credit Scoring → decision logged with required remediations",
            "scoring_blocks": [
                {"block": "A — Market intelligence", "weight": "40%",
                 "detail": "Datamyne export volume and trend; to be complemented with public registries, "
                            "top-3 suppliers, market position, public financial health, country/FX risk, press and litigation signals"},
                {"block": "B — Credit insurer", "weight": "30%",
                 "detail": "Approved line, risk rating, claims history, recent coverage changes, response time"},
                {"block": "C — Loads historical data", "weight": "10%",
                 "detail": "Payment behavior, 24-month volumes, import trend, client tenure, product "
                            "diversification, order recurrence — weight grows as internal history accumulates"},
                {"block": "D — Deal structure", "weight": "20%",
                 "detail": "Advance percentage and credit term up to 30 days post-arrival"},
            ],
            "tiers": [
                {"tier": "AAA", "range": "723+", "profile": "Full credit insurance, zero arrears, top-tier diversified importer",
                 "structure": "100% financed, 45–75 days post-arrival"},
                {"tier": "AA", "range": "606–722", "profile": "Insured, arrears < 30d, good history, financials delivered",
                 "structure": "100% financed, up to 45 days post-arrival"},
                {"tier": "A", "range": "546–605", "profile": "Arrears < 60d but paying, fiscal & financial info, known importer",
                 "structure": "20% against documents / 80% post-arrival (30 days)"},
                {"tier": "B", "range": "475–545", "profile": "Arrears < 60d, fiscal certificate only, acceptable importer",
                 "structure": "50% against documents / 50% post-arrival (30 days)"},
                {"tier": "C", "range": "252–474", "profile": "Arrears 60–90d, corporate e-mail only, acceptable importer",
                 "structure": "50% against documents / 50% on arrival"},
                {"tier": "D", "range": "152–251", "profile": "Arrears 60–90d, new importer or declining imports",
                 "structure": "70% against documents / 30% on arrival"},
                {"tier": "E", "range": "0–151", "profile": "No information or adverse signals",
                 "structure": "Fully prepaid (100% in advance)"},
            ],
            "collections": [
                {"bucket": "Preventive (−7 to 0 days)", "plan": "Weekly upcoming-maturity reminders, "
                  "minimum 5–7 days before due date, from estimated shipping/arrival dates"},
                {"bucket": "Administrative (1–30 DPD)", "plan": "Weekly monitoring and payment statements "
                  "with the Commercial team; Commercial Collections Committee decides escalation"},
                {"bucket": "Extrajudicial (31–90 DPD)", "plan": "Risk & Collections leads with weekly "
                  "committee, statements and calls; bureau publication and external collection agencies evaluated case-by-case"},
                {"bucket": "Judicial (> 90 DPD)", "plan": "Legal process with external counsel evaluated; "
                  "weekly tracking of legal milestones per case"},
            ],
            "mitigation": "Orders structured with advances, guarantees or letters of credit; immediate "
                           "suspension of shipments on non-payment; credit insurance covering delinquency losses",
            "sla": "Credit decision SLAs — new client 72 hours; new order for an existing client 24 hours",
            "documents": "Bill of Lading (title to goods), Packing List, Commercial Invoice (disbursement "
                          "trigger and support of the collection right), Certificate of Origin, Phytosanitary "
                          "Certificate; credit/debit notes at close for volume, quality, shrinkage, FX and logistics adjustments",
        },
    }

    documents = [
        {"name": "Loads Loan Tape (orders + expected & actual payments)", "cat": "Loan Tape",
         "date": lt["as_of"], "fmt": "XLSX",
         "note": "120 trade orders, 6 business units, USD — order-level exposure, DPD and settled cash"},
        {"name": "Consolidated Financial Statements FY2025 / FY2024 — Loads USA, Inc.", "cat": "Financial Statements",
         "date": "2025-12-31", "fmt": "PDF/TXT",
         "note": "Pre-audit consolidated statement of financial position and income statement by function (USD)"},
        {"name": "Manual de Crédito, Recuperación y Cobranza 2026", "cat": "Contracts",
         "date": "2026-01-01", "fmt": "PDF/TXT",
         "note": "Credit scoring model, tier-based financing structures, collections buckets and expected-loss provisioning"},
        {"name": "Investment Memorandum 2Q2025", "cat": "Investment Memo",
         "date": "2025-06-30", "fmt": "PDF/TXT",
         "note": "Trade / Move / Finance platform overview, SPV model, unit economics and structured-facility profile"},
        {"name": "Loads Reporting Platform dataset", "cat": "Supporting Documents",
         "date": lt["as_of"], "fmt": "JSON",
         "note": "ETL output backing this application (portfolio, financials, policy board, fact sheets)"},
    ]

    workspace_seed = [
        {"id": 1, "title": "Q2 2026 loan-tape refresh and DPD reconciliation",
         "desc": "Load the next tape cut, reconcile settled payments vs expected schedule and re-run the provision grid.",
         "status": "In Progress", "priority": "High", "area": "Portfolio", "due": "2026-07-31",
         "created": "2026-07-01", "assignee": "Portfolio Monitoring", "tags": ["monthly-cycle"],
         "subtasks": [{"t": "Request tape + payment extract from Loads Back Office", "done": True},
                       {"t": "Run build_app.py and review deltas", "done": False},
                       {"t": "Circulate PAR / provision summary to deal team", "done": False}],
         "comments": []},
        {"id": 2, "title": "Follow up: FY2025 audited consolidated financials",
         "desc": "FY2025 statements in the data room are the pre-audit close (PRE ESTADO). Obtain the audited version and tie equity roll-forward.",
         "status": "Waiting", "priority": "High", "area": "Finance", "due": "2026-08-15",
         "created": "2026-06-20", "assignee": "Finance", "tags": ["financials"],
         "subtasks": [{"t": "Confirm auditor and expected sign-off date", "done": True},
                       {"t": "Reconcile pre-audit vs audited balance sheet", "done": False}],
         "comments": [{"a": "Addem", "t": "2026-07-02 10:14",
                        "m": "Loads confirms the audit is in fieldwork; sign-off expected mid-August."}]},
        {"id": 3, "title": "Facility term sheet — SPV structure and advance mechanics",
         "desc": "Draft the Addem term sheet against the indicative structured-facility profile: 20% minimum retention, milestone-linked payments, insurance assignment.",
         "status": "In Progress", "priority": "Critical", "area": "Capital Markets", "due": "2026-08-07",
         "created": "2026-06-15", "assignee": "Capital Markets", "tags": ["structuring"],
         "subtasks": [{"t": "Benchmark advance rate vs 86.9% historical collection rate", "done": True},
                       {"t": "Define borrowing-base formula on eligible receivables", "done": False},
                       {"t": "Align interest reserve with 30–45d WAL", "done": False}],
         "comments": []},
        {"id": 4, "title": "Legal review — Manual de Crédito 2026 vs facility covenants",
         "desc": "Map the manual's provisioning grid, SLAs and collections committees into facility reporting covenants and events of default.",
         "status": "Not Started", "priority": "High", "area": "Legal", "due": "2026-08-21",
         "created": "2026-07-05", "assignee": "Legal", "tags": ["documentation"],
         "subtasks": [{"t": "Confirm enforceability of invoice assignment per jurisdiction", "done": False},
                       {"t": "Review credit-insurance loss-payee designation", "done": False}],
         "comments": []},
        {"id": 5, "title": "Trade credit insurance diligence (post-Coface programme)",
         "desc": "Validate the up-to-90% coverage per operation, claims history and the AVLA-approved-line fallback for importers without financials.",
         "status": "In Progress", "priority": "High", "area": "Investments", "due": "2026-07-28",
         "created": "2026-06-25", "assignee": "Investments", "tags": ["insurance", "diligence"],
         "subtasks": [{"t": "Obtain policy wording and exclusions", "done": True},
                       {"t": "Sample-test insured vs uninsured orders in the tape", "done": False}],
         "comments": []},
        {"id": 6, "title": "Importer concentration review — top obligor at 18% of receivables",
         "desc": "Largest active importer holds ~18% of the outstanding receivable. Assess single-obligor limit for the facility borrowing base.",
         "status": "Not Started", "priority": "Medium", "area": "Portfolio", "due": "2026-08-10",
         "created": "2026-07-08", "assignee": "Portfolio Monitoring", "tags": ["concentration"],
         "subtasks": [], "comments": []},
        {"id": 7, "title": "91–180 DPD accounts — judicial-bucket action plans",
         "desc": "Five active orders sit past 90 DPD. Confirm each is in the weekly Judicial Committee with a documented action plan per the manual.",
         "status": "In Progress", "priority": "High", "area": "Portfolio", "due": "2026-07-24",
         "created": "2026-07-06", "assignee": "Portfolio Monitoring", "tags": ["collections"],
         "subtasks": [{"t": "Obtain Judicial Committee minutes", "done": False},
                       {"t": "Verify shipment suspension on non-paying accounts", "done": False}],
         "comments": []},
        {"id": 8, "title": "Investment memo refresh — 3Q2025 KPIs onward",
         "desc": "Request updated origination, NPL and GMV series beyond the 2Q2025 memo for the IC deck.",
         "status": "Not Started", "priority": "Medium", "area": "Investments", "due": "2026-08-14",
         "created": "2026-07-10", "assignee": "Investments", "tags": ["ic-materials"],
         "subtasks": [], "comments": []},
        {"id": 9, "title": "Google Drive sync — service account for the Loads data room",
         "desc": "Provision read access to the shared folder and schedule the ETL in a GitHub Action so index.html rebuilds on new files.",
         "status": "Not Started", "priority": "Low", "area": "Capital Markets", "due": "2026-09-01",
         "created": "2026-07-12", "assignee": "Platform", "tags": ["automation"],
         "subtasks": [], "comments": []},
        {"id": 10, "title": "FY2025 loss drivers — administrative expense bridge",
         "desc": "Net result moved from breakeven (FY2024) to −$1.13M on admin expenses nearly doubling. Build the expense bridge and runway view.",
         "status": "In Progress", "priority": "High", "area": "Finance", "due": "2026-08-05",
         "created": "2026-07-03", "assignee": "Finance", "tags": ["financials"],
         "subtasks": [{"t": "Request FY2025 admin-expense detail by nature", "done": False},
                       {"t": "Tie capital reduction ($200k) and reserves movement", "done": False}],
         "comments": []},
        {"id": 11, "title": "Weekly collections committee minutes — standing request",
         "desc": "Standing monitoring item: obtain Commercial and Judicial committee outputs weekly per the manual's §5 cadence.",
         "status": "In Progress", "priority": "Medium", "area": "Portfolio", "due": "2026-07-23",
         "created": "2026-07-01", "assignee": "Portfolio Monitoring", "tags": ["monitoring", "recurring"],
         "subtasks": [], "comments": []},
        {"id": 12, "title": "Scoring model validation — Block A/B data lineage",
         "desc": "Validate Datamyne and credit-insurer feeds behind the 0–1000 score; back-test tier assignment against realized DPD in the tape.",
         "status": "Not Started", "priority": "Medium", "area": "Investments", "due": "2026-08-28",
         "created": "2026-07-15", "assignee": "Investments", "tags": ["underwriting"],
         "subtasks": [{"t": "Back-test tiers C–E vs realized arrears", "done": False}],
         "comments": []},
    ]
    for t in workspace_seed:
        t.setdefault("archived", False)

    data = {
        "meta": {
            "borrower": "Loads",
            "entity": "Loads USA, Inc. (consolidated)",
            "as_of_date": lt["as_of"],
            "financials_through": "2025",
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "currency": "USD",
            "definitions": {
                "financed_exposure": "totalWithAdjustments — order value net of credit/debit notes",
                "outstanding": "totalDueAmount — open receivable per order as reported in the tape",
                "active": "orders with an open receivable (totalDueAmount > 0)",
                "dpd": "overDueDays as reported; buckets follow the Manual de Credito 2026 grid",
                "npl": "receivables > 180 days past due (Loads definition)",
                "expected_loss": "Manual de Credito §6.2 rates applied to the open receivable by DPD bucket",
                "collections": "Settled rows in the actual-payments extract (advance + regular)",
            },
        },
        "loan_tape": lt["segments"],
        "concentration": lt["concentration"],
        "outstanding_series": lt["outstanding_series"],
        "financials": fin,
        "policy": policy,
        "contracts": contracts,
        "documents": documents,
        "workspace_seed": workspace_seed,
    }
    (HERE / "dashboard_data.json").write_text(json.dumps(data, indent=1), encoding="utf-8")
    print("dashboard_data.json built —", len(json.dumps(data)) // 1024, "KB")


if __name__ == "__main__":
    main()
