#!/usr/bin/env python3
"""Generate compounder-screen markdown reports from compounder_fmp_data.json."""
import json
import sys
from pathlib import Path

DATE = "2025-03-07"
WS = Path(__file__).resolve().parents[1]
DATA_PATH = WS / "outputs" / "compounder_fmp_data.json"
OUT = WS / "outputs"


def pct(x):
    if x is None:
        return None
    return x * 100 if abs(x) < 1.5 else x


def get_latest(lst, key, default=None):
    if not lst or not isinstance(lst, list):
        return default
    for item in lst:
        if isinstance(item, dict) and key in item and item[key] is not None:
            return item[key]
    return default


def get_series(lst, key, n=5):
    if not lst or not isinstance(lst, list):
        return []
    out = []
    for item in lst[:n]:
        if isinstance(item, dict):
            out.append(item.get(key))
    return out


def score_ticker(ticker, data):
    if "error" in data:
        return None, None, str(data["error"])
    profile = (data.get("profile") or [{}])[0] if data.get("profile") else {}
    quote = (data.get("quote") or [{}])[0] if data.get("quote") else {}
    income = data.get("income") or []
    balance = data.get("balance") or []
    cashflow = data.get("cashflow") or []
    km = data.get("key_metrics") or []
    ratios = data.get("ratios") or []
    dividends = data.get("dividends") or []
    rev_seg = data.get("revenue_seg") or []

    name = profile.get("companyName") or quote.get("name") or ticker
    sector = profile.get("sector") or "N/A"
    industry = profile.get("industry") or "N/A"
    price = quote.get("price")
    mkt_cap = quote.get("marketCap") or profile.get("mktCap")

    # Latest year = index 0 (FMP newest first)
    inc0 = income[0] if income else {}
    bal0 = balance[0] if balance else {}
    cf0 = cashflow[0] if cashflow else {}
    km0 = km[0] if km else {}

    # ROIC series (key_metrics uses 'roic' lowercase)
    roic_series = get_series(km, "roic", 5) or get_series(ratios, "returnOnInvestedCapital", 5)
    roic_latest = roic_series[0] if roic_series else None
    roic_pct = pct(roic_latest)

    # EBITDA & debt
    ebitda = inc0.get("ebitda") or km0.get("ebitda")
    total_debt = bal0.get("totalDebt") or (bal0.get("longTermDebt") or 0) + (bal0.get("shortTermDebt") or 0)
    lt_debt = bal0.get("longTermDebt") or total_debt
    debt_ebitda = (lt_debt / ebitda) if ebitda and lt_debt and ebitda > 0 else None

    # FCF yield
    fcf_yield = km0.get("freeCashFlowYield")
    if fcf_yield is None and mkt_cap and cf0:
        fcf = cf0.get("freeCashFlow") or (cf0.get("operatingCashFlow") or 0) - abs(cf0.get("capitalExpenditure") or 0)
        if mkt_cap > 0 and fcf:
            fcf_yield = fcf / mkt_cap
    fcf_yield_pct = pct(fcf_yield)

    # Margins 5y (for cyclicality and franchise)
    op_margin_series = []
    for inc in income[:5]:
        rev = inc.get("revenue") or 1
        op = inc.get("operatingIncome")
        if op is not None:
            op_margin_series.append(op / rev * 100 if rev else None)
    net_margin_series = []
    for inc in income[:5]:
        rev = inc.get("revenue") or 1
        ni = inc.get("netIncome")
        if ni is not None:
            net_margin_series.append(ni / rev * 100 if rev else None)

    # Dividend growth (dividends: list of {date, dividend, adjDividend})
    div_dates = sorted([d for d in dividends if isinstance(d, dict) and d.get("date")], key=lambda x: x["date"], reverse=True)[:5]
    div_values = [float(d.get("dividend") or d.get("adjDividend") or 0) for d in div_dates if d.get("dividend") or d.get("adjDividend")]
    dividend_growing = len(div_values) >= 2 and div_values[0] >= div_values[-1] and div_values[0] > 0
    has_dividend = len(div_values) > 0 and div_values[0] > 0
    # Buybacks
    buyback_positive = any((cf.get("commonStockRepurchased") or 0) < 0 for cf in cashflow[:3])  # negative = repurchase

    desc = (profile.get("description") or "")[:500]

    # --- Score each criterion ---
    results = []

    # 1. Strong franchise durability
    gross_ratio = inc0.get("grossProfitRatio") or (inc0.get("grossProfit") / inc0["revenue"] if inc0.get("revenue") and inc0.get("grossProfit") else None)
    if gross_ratio is not None and abs(gross_ratio) < 1:
        gross_ratio *= 100
    op_ratio = inc0.get("operatingIncomeRatio")
    if op_ratio is not None and abs(op_ratio) < 1:
        op_ratio *= 100
    if (gross_ratio and gross_ratio >= 40) and (roic_pct and roic_pct >= 12):
        r1 = ("Pass", "Strong margins and ROIC support durable franchise.")
    elif (gross_ratio and gross_ratio >= 30) or (roic_pct and roic_pct >= 10):
        r1 = ("Partial", "Solid margins or ROIC but not both exceptional.")
    else:
        r1 = ("Fail", "Margins or ROIC below compounder bar.")
    results.append(("Strong franchise durability", r1[0], r1[1]))

    # 2. High return on capital
    roic_above_10 = all(r and (r >= 0.10 if r < 1.5 else r >= 10) for r in roic_series if r is not None)
    roic_above_12 = roic_latest and (roic_latest >= 0.12 if abs(roic_latest) < 1.5 else roic_latest >= 12)
    if roic_series and roic_above_12 and (len(roic_series) < 2 or (roic_series[0] or 0) >= (roic_series[-1] or 0) * 0.9):
        r2 = ("Pass", f"ROIC consistently above cost of capital (latest {roic_pct:.1f}%).")
    elif roic_above_10:
        r2 = ("Partial", f"ROIC above 10% but not consistently >> cost of capital (latest {roic_pct:.1f}%).")
    else:
        r2 = ("Fail", f"ROIC below or inconsistent vs cost of capital (latest {f'{roic_pct:.1f}%' if roic_pct is not None else 'N/A'}).")
    results.append(("High return on capital (ROIC >> cost of capital)", r2[0], r2[1]))

    # 3. Recurring revenue
    recurring_keywords = ["subscription", "recurring", "repeat", "recurring revenue", "saas", "software", "pharmaceutical", "drug", "payment", "transaction", "network", "platform", "license", "maintenance", "consumer", "brand"]
    desc_lower = desc.lower()
    has_recurring = any(k in desc_lower for k in recurring_keywords)
    if has_recurring and ("one-time" not in desc_lower and "blockbuster" not in desc_lower):
        r3 = ("Pass", "Business model indicates recurring/repeat revenue.")
    elif has_recurring:
        r3 = ("Partial", "Some recurring elements but mixed with one-off or cyclical.")
    else:
        r3 = ("Fail", "Revenue appears contract or product-cycle driven.")
    results.append(("Recurring revenue", r3[0], r3[1]))

    # 4. High FCF (4-6%)
    if fcf_yield_pct is not None:
        if 4 <= fcf_yield_pct <= 6:
            r4 = ("Pass", f"FCF yield in target range ({fcf_yield_pct:.1f}%).")
        elif fcf_yield_pct >= 6:
            r4 = ("Pass", f"FCF yield above target ({fcf_yield_pct:.1f}%).")
        elif 3 <= fcf_yield_pct < 4:
            r4 = ("Partial", f"FCF yield slightly below 4% ({fcf_yield_pct:.1f}%).")
        else:
            r4 = ("Fail", f"FCF yield below target ({fcf_yield_pct:.1f}%).")
    else:
        r4 = ("Partial", "FCF yield not available or not meaningful.")
    results.append(("High FCF (4-6% yield)", r4[0], r4[1]))

    # 5. Minimal leverage (Debt < 3x EBITDA)
    if debt_ebitda is not None:
        if debt_ebitda < 3:
            r5 = ("Pass", f"Debt/EBITDA = {debt_ebitda:.2f}x (< 3x).")
        else:
            r5 = ("Fail", f"Debt/EBITDA = {debt_ebitda:.2f}x (≥ 3x).")
    else:
        r5 = ("Partial", "Debt or EBITDA missing; assume conservative.")
    results.append(("Minimal leverage (Debt < 3× EBITDA)", r5[0], r5[1]))

    # 6. Low cyclicality
    if len(op_margin_series) >= 4 and all(op_margin_series[i] and op_margin_series[i] > 0 for i in range(min(4, len(op_margin_series)))):
        min_op = min(x for x in op_margin_series if x is not None)
        max_op = max(x for x in op_margin_series if x is not None)
        if max_op - min_op < 15 and min_op > 5:
            r6 = ("Pass", "Operating margins stable across 5y.")
        elif max_op - min_op < 25:
            r6 = ("Partial", "Some margin variability over cycle.")
        else:
            r6 = ("Fail", "High margin cyclicality.")
    else:
        r6 = ("Partial", "Insufficient margin history.")
    results.append(("Low cyclicality", r6[0], r6[1]))

    # 7. Returns capital
    if has_dividend and dividend_growing and buyback_positive:
        r7 = ("Pass", "Growing dividends and buybacks.")
    elif has_dividend and dividend_growing:
        r7 = ("Pass", "Growing dividends.")
    elif buyback_positive or has_dividend:
        r7 = ("Partial", "Dividends or buybacks but not both growing.")
    else:
        r7 = ("Fail", "No meaningful dividend or buyback.")
    results.append(("Returns capital (dividends and/or buybacks)", r7[0], r7[1]))

    pass_count = sum(1 for _, res, _ in results if res == "Pass")
    partial_count = sum(1 for _, res, _ in results if res == "Partial")
    fail_count = sum(1 for _, res, _ in results if res == "Fail")

    if pass_count >= 6:
        overall = "Strong compounder"
    elif pass_count >= 4:
        overall = "Compounder"
    elif pass_count >= 3:
        overall = "Marginal"
    else:
        overall = "Not a compounder"

    if pass_count >= 5 and fail_count == 0:
        verdict = "Add to watchlist"
    elif pass_count >= 4 or (pass_count >= 3 and partial_count >= 2):
        verdict = "Consider for watchlist"
    else:
        verdict = "Do not add"

    # Supporting data strings
    roic_str = f"5y: {[round(pct(r), 1) if r is not None else 'N/A' for r in roic_series]}; latest {roic_pct:.1f}%" if roic_pct is not None else "N/A"
    fcf_str = f"{fcf_yield_pct:.1f}%" if fcf_yield_pct is not None else "N/A"
    debt_str = f"{debt_ebitda:.2f}x" if debt_ebitda is not None else "N/A"
    div_str = f"Dividend: {'Growing' if dividend_growing else 'Flat/None'}; Buybacks: {'Yes' if buyback_positive else 'No'}"

    return {
        "name": name,
        "sector": sector,
        "industry": industry,
        "price": price,
        "results": results,
        "overall": overall,
        "verdict": verdict,
        "pass_count": pass_count,
        "partial_count": partial_count,
        "fail_count": fail_count,
        "roic_str": roic_str,
        "fcf_str": fcf_str,
        "debt_str": debt_str,
        "div_str": div_str,
        "recurring_note": desc[:300] + "..." if len(desc) > 300 else desc or "N/A",
    }


def main():
    with open(DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)
    tickers = list(data.keys())
    report_date = DATE
    summaries = []
    for ticker in tickers:
        out_dict = score_ticker(ticker, data[ticker])
        if out_dict is None:
            continue
        summary = out_dict
        summaries.append((ticker, summary))
        md = f"""# Compounder Screen — {summary['name']} ({ticker})

**Report date:** {report_date}
**Current price:** {f"${summary['price']:.2f}" if summary.get('price') is not None else 'N/A'} (FMP)
**Sector / Industry:** {summary['sector']} / {summary['industry']}

---

## Compounder checklist scorecard

| # | Criterion | Result | Reason |
|---|-----------|--------|--------|
"""
        for i, (crit, res, reason) in enumerate(summary["results"], 1):
            md += f"| {i} | {crit} | {res} | {reason} |\n"
        md += f"""
**Overall:** {summary['overall']}
**Verdict:** {summary['verdict']}

---

## Supporting data

- **ROIC / ROCE:** {summary['roic_str']}
- **FCF yield:** {summary['fcf_str']}
- **Debt / EBITDA:** {summary['debt_str']}
- **Dividend / buyback:** {summary['div_str']}
- **Recurring revenue:** {summary['recurring_note']}

---

## Next steps

- If Add/Consider: run `/stockscore {ticker}`, `/moat {ticker}`, `/company-growth {ticker}`; optionally `/buffett-intrinsic-value-calculator {ticker}`. Update `context/watchlist.md` when adding.
- If Do not add: note why; re-screen after 1–2 quarters if thesis changes.
"""
        out_path = OUT / f"compounder-screen-{ticker}-{report_date}.md"
        out_path.write_text(md, encoding="utf-8")
        print(f"Wrote {out_path}")

    # Summary report
    summary_md = f"""# Compounder Screen Summary — {report_date}

| Ticker | Company | Pass | Partial | Fail | Overall | Verdict |
|--------|---------|------|---------|------|---------|---------|
"""
    for ticker, s in sorted(summaries, key=lambda x: -x[1]["pass_count"]):
        summary_md += f"| {ticker} | {s['name'][:30]} | {s['pass_count']} | {s['partial_count']} | {s['fail_count']} | {s['overall']} | {s['verdict']} |\n"
    summary_path = OUT / f"compounder-screen-summary-{report_date}.md"
    summary_path.write_text(summary_md, encoding="utf-8")
    print(f"Wrote {summary_path}")


if __name__ == "__main__":
    main()
