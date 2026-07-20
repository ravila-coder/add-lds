"""Loads financials ETL.

Parses sources/financials_consolidated_2025.txt — the consolidated statement of
financial position and income statement by function of LOADS USA, INC. for the
years ended 31 Dec 2025 and 31 Dec 2024 (USD, Chilean statutory presentation:
'.' thousands separator, ',' decimals, parentheses for negatives) — into the
common statement schema used by the dashboard, with a full ratio suite per year.
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "sources" / "financials_consolidated_2025.txt"
OUT = HERE / "loads_financials.json"

NUM = r"\(?-?[\d.]+,\d\)?|\(?-\)?|-"


def parse_num(tok):
    tok = tok.strip()
    if tok in ("-", "", "0,0"):
        return 0.0
    neg = tok.startswith("(") or tok.startswith("-")
    tok = tok.strip("()-")
    return (-1 if neg else 1) * float(tok.replace(".", "").replace(",", "."))


def two_nums(text, label):
    """Return (FY-latest, FY-prior) for a labeled statement line."""
    pat = re.compile(re.escape(label) + r"\s+(" + NUM + r")\s+(" + NUM + r")")
    m = pat.search(text)
    if not m:
        raise ValueError(f"line not found in source statement: {label}")
    return parse_num(m.group(1)), parse_num(m.group(2))


def main():
    text = re.sub(r"\s+", " ", SRC.read_text(encoding="utf-8"))

    BS_LINES = {
        "cash": "Efectivo y equivalentes al efectivo",
        "trade_receivables": "Deudores comerciales y otras cuentas por cobrar",
        "other_fin_assets": "Otros activos financieros",
        "current_tax_assets": "Activos por impuestos corrientes",
        "related_receivables": "Cuentas por cobrar a entidades relacionadas",
        "other_nonfin_assets": "Otros activos no financieros",
        "total_current_assets": "Total de Activos Corrientes",
        "intangibles": "Activos intangibles, distintos de la Plusvalía",
        "deferred_tax_assets": "Activos por impuestos diferidos",
        "ppe": "Propiedades plantas y equipos",
        "total_noncurrent_assets": "Total de Activos No Corrientes",
        "total_assets": "Total de Activos",
        "other_fin_liabilities": "Otros pasivos financieros",
        "trade_payables": "Cuentas comerciales y otras cuentas por pagar",
        "related_payables": "Cuentas por Pagar a Entidades Relacionadas",
        "other_nonfin_liabilities": "Otros pasivos no financieros",
        "employee_provisions": "Provision por beneficios a los empleados",
        "total_current_liabilities": "Total de Pasivos Corrientes",
        "total_liabilities": "Total de Pasivos",
        "paid_in_capital": "Capital pagado",
        "other_reserves": "Otras reservas",
        "accumulated_result": "Resultado Acumulado",
        "total_equity": "Total Patrimonio",
    }
    IS_LINES = {
        "revenue": "Ingresos de actividad ordinaria",
        "cost_of_sales": "Costo de explotación",
        "gross_profit": "Utilidad en operaciones",
        "admin_expenses": "Gastos de administración",
        "other_income": "Otros ingresos (gastos)",
        "financial_result": "Ingresos (costos) financieros",
        "indexation": "Unidades de reajustes",
        "pretax": "Ganancia (pérdida), antes de impuestos",
        "income_tax": "(Gasto)/ingreso por impuesto a las ganancias",
        "net_income": "Resultado neto",
    }

    bs = {k: two_nums(text, lbl) for k, lbl in BS_LINES.items()}
    isb = {k: two_nums(text, lbl) for k, lbl in IS_LINES.items()}

    # Validation: articulation of the statutory statements
    for i, yr in enumerate(("FY2025", "FY2024")):
        ca = sum(bs[k][i] for k in ("cash", "trade_receivables", "other_fin_assets",
                                     "current_tax_assets", "related_receivables", "other_nonfin_assets"))
        assert abs(ca - bs["total_current_assets"][i]) < 1, f"{yr}: current assets do not tie"
        assert abs(bs["total_current_assets"][i] + bs["total_noncurrent_assets"][i] - bs["total_assets"][i]) < 1
        assert abs(bs["total_liabilities"][i] + bs["total_equity"][i] - bs["total_assets"][i]) < 1, f"{yr}: BS does not balance"
        ni = (isb["pretax"][i] + isb["income_tax"][i])
        assert abs(ni - isb["net_income"][i]) < 1, f"{yr}: IS does not tie"

    periods = [("2024", 1, "Consolidated statutory close — LOADS USA, INC. (FY2024)"),
               ("2025", 0, "Consolidated statutory close — LOADS USA, INC. (FY2025)")]
    out = []
    for period, i, source in periods:
        v = lambda k: bs[k][i]
        w = lambda k: isb[k][i]
        opex = -w("admin_expenses")  # positive magnitude
        cost = -w("cost_of_sales")
        other = w("other_income") + w("financial_result") + w("indexation") + w("income_tax")
        operating_income = w("gross_profit") - opex
        quick_assets = v("cash") + v("trade_receivables") + v("other_fin_assets")
        fin_debt = v("other_fin_liabilities")
        prior_i = 1 if i == 0 else None  # prior year available only for FY2025
        rev_growth = (isb["revenue"][0] / isb["revenue"][1] - 1) if i == 0 else None
        interest_exp = -w("financial_result") if w("financial_result") < 0 else None

        entry = {
            "period": period,
            "source": source,
            "preliminary": i == 0,  # FY2025 headed "PRE ESTADO" — pre-audit close
            "is_monthly": {  # schema name kept for template compatibility; values are annual
                "sections": {
                    "income": [{"label": "Revenue from ordinary activities", "value": w("revenue")}],
                    "cost": [{"label": "Cost of operations (Costo de explotación)", "value": cost}],
                    "opex": [{"label": "Administrative expenses", "value": opex}],
                    "other": [
                        {"label": "Other income (expenses)", "value": w("other_income")},
                        {"label": "Financial income (costs)", "value": w("financial_result")},
                        {"label": "Indexation units (Unidades de reajuste)", "value": w("indexation")},
                        {"label": "Income tax (expense) / benefit", "value": w("income_tax")},
                    ],
                },
                "totals": {
                    "revenue": w("revenue"), "cost": cost, "gross_profit": w("gross_profit"),
                    "opex": opex, "operating_income": operating_income,
                    "other": other, "net_income": w("net_income"),
                },
            },
            "ytd_net_income": w("net_income"),
            "financial_debt": fin_debt,
            "bs": {
                "cash": v("cash"),
                "total_assets": v("total_assets"),
                "total_liabilities": v("total_liabilities"),
                "total_equity": v("total_equity"),
                "current_assets": v("total_current_assets"),
                "current_liabilities": v("total_current_liabilities"),
                "trade_receivables": v("trade_receivables"),
                "paid_in_capital": v("paid_in_capital"),
                "detail": {
                    "assets": [
                        {"label": "Cash and cash equivalents", "value": v("cash")},
                        {"label": "Trade and other receivables", "value": v("trade_receivables")},
                        {"label": "Other financial assets", "value": v("other_fin_assets")},
                        {"label": "Current tax assets", "value": v("current_tax_assets")},
                        {"label": "Receivables from related parties", "value": v("related_receivables")},
                        {"label": "Other non-financial assets (current)", "value": v("other_nonfin_assets")},
                        {"label": "Intangible assets (ex-goodwill)", "value": v("intangibles")},
                        {"label": "Deferred tax assets", "value": v("deferred_tax_assets")},
                        {"label": "Property, plant and equipment", "value": v("ppe")},
                    ],
                    "liabilities": [
                        {"label": "Other financial liabilities", "value": v("other_fin_liabilities")},
                        {"label": "Trade and other payables", "value": v("trade_payables")},
                        {"label": "Payables to related parties", "value": v("related_payables")},
                        {"label": "Other non-financial liabilities", "value": v("other_nonfin_liabilities")},
                        {"label": "Employee benefit provisions", "value": v("employee_provisions")},
                    ],
                    "equity": [
                        {"label": "Paid-in capital", "value": v("paid_in_capital")},
                        {"label": "Other reserves", "value": v("other_reserves")},
                        {"label": "Accumulated results", "value": v("accumulated_result")},
                    ],
                },
            },
            "ratios": {
                "gross_margin": w("gross_profit") / w("revenue"),
                "operating_margin": operating_income / w("revenue"),
                "net_margin": w("net_income") / w("revenue"),
                "current_ratio": v("total_current_assets") / v("total_current_liabilities"),
                "quick_ratio": quick_assets / v("total_current_liabilities"),
                "debt_to_equity": v("total_liabilities") / v("total_equity"),
                "debt_to_assets": v("total_liabilities") / v("total_assets"),
                "equity_ratio": v("total_equity") / v("total_assets"),
                "interest_coverage": (operating_income / interest_exp) if interest_exp else None,
                "roa_annualized": w("net_income") / v("total_assets"),
                "roe_annualized": w("net_income") / v("total_equity"),
                "revenue_growth": rev_growth,
            },
        }
        entry["ratios"] = {k: (round(x, 6) if isinstance(x, float) else x) for k, x in entry["ratios"].items()}
        out.append(entry)

    OUT.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"financials ETL ok — {len(out)} annual closes "
          f"(FY2025 revenue ${isb['revenue'][0]:,.0f}, net ${isb['net_income'][0]:,.0f})")


if __name__ == "__main__":
    main()
