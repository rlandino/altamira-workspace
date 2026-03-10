# Market Monitoring Workflow Design Document

**Document:** Automated Market Monitoring Workflows for Altamira Capital
**Author:** Ricardo Landino
**Date:** 2026-02-18
**Version:** 1.0
**Status:** Design Phase

---

## Executive Summary

Altamira Capital currently runs 1 automated daily report (Market Commenter v3.1) across ~15 active n8n workflows. This document designs 5 new automated monitoring workflows that will scale the firm to 6 total automated monitoring systems, covering price alerts, options flow, sector rotation, portfolio risk, and volatility regime detection.

**Goal:** Transform Altamira from reactive monitoring (checking screens manually) to proactive alerting (the system tells Ricardo what matters, when it matters). This is the single highest-leverage automation investment for a solo founder managing a multi-strategy portfolio.

**Core universe:** AAPL, MSFT, GOOGL, AMZN, AVGO, COST, V, MA, META, NVDA, SPY

**Infrastructure stack:**
- n8n cloud (~15 active workflows)
- FMP API (fundamentals, quotes, earnings, ratios, SEC filings)
- Massive.com OPRA feed (options data, greeks, IV, historical tick)
- Google Sheets (tracking, dashboards, reporting)
- Telegram (notifications, approvals, on-demand commands)
- E-Trade API (coming online: account, positions, orders)

---

## Table of Contents

1. [Summary Table: All 6 Monitoring Workflows](#1-summary-table-all-6-monitoring-workflows)
2. [Workflow 1: Watchlist Alert System](#2-workflow-1-watchlist-alert-system)
3. [Workflow 2: Options Flow & IV Monitor](#3-workflow-2-options-flow--iv-monitor)
4. [Workflow 3: Sector Rotation Monitor](#4-workflow-3-sector-rotation-monitor)
5. [Workflow 4: Portfolio Risk Dashboard](#5-workflow-4-portfolio-risk-dashboard)
6. [Workflow 5: Volatility Regime & Hedging Trigger](#6-workflow-5-volatility-regime--hedging-trigger)
7. [Combined Daily Schedule](#7-combined-daily-schedule)
8. [Total API Call Budget](#8-total-api-call-budget)
9. [Implementation Roadmap](#9-implementation-roadmap)
10. [Maintenance Plan](#10-maintenance-plan)
11. [Appendix: Telegram Message Templates](#11-appendix-telegram-message-templates)

---

## 1. Summary Table: All 6 Monitoring Workflows

| # | Workflow | Trigger | Frequency | Data Sources | Output Channels | Priority | Effort |
|---|---------|---------|-----------|-------------|----------------|----------|--------|
| 0 | **Market Commenter v3.1** (existing) | Daily 7:00 AM ET | 1x/day | FMP | Telegram | Deployed | Done |
| 1 | **Watchlist Alert System** | Every 15 min (market hours) | ~26x/day | FMP | Telegram | P0 | 2 days |
| 2 | **Options Flow & IV Monitor** | 10:30 AM + 3:30 PM ET | 2x/day | Massive.com, FMP | Telegram, Google Sheets | P1 | 3 days |
| 3 | **Sector Rotation Monitor** | Daily 4:30 PM ET | 1x/day | FMP | Telegram, Google Sheets | P2 | 1.5 days |
| 4 | **Portfolio Risk Dashboard** | Daily close + on-demand | 1x/day + ad hoc | E-Trade, Massive.com, FMP | Telegram, Google Sheets | P1 | 3 days |
| 5 | **Volatility Regime & Hedging Trigger** | Every 30 min (market hours) | ~13x/day | FMP, Massive.com | Telegram, Google Sheets | P0 | 2 days |

**Total new workflows:** 5
**Total estimated build time:** 11.5 days (spread across 3-4 weeks with testing)

---

## 2. Workflow 1: Watchlist Alert System

### 2.1 Purpose and Value Proposition

**What it does:** Monitors the 11-ticker core universe every 15 minutes during market hours and sends targeted Telegram alerts when prices cross significant technical or fundamental levels.

**Edge it creates:** A solo manager cannot watch 11 tickers continuously. This workflow eliminates the need to stare at screens. It captures the exact moments when a watchlist name hits a level that demands attention -- whether that is a breakout, a breakdown, an unusual volume surge, or an approaching earnings event. Without this, you either miss the move or waste time refreshing quotes.

**Decision it supports:** "Should I look at this ticker right now?" -- answered automatically.

### 2.2 Trigger Schedule

| Parameter | Value |
|-----------|-------|
| Type | Cron schedule |
| Schedule | Every 15 minutes |
| Active window | 9:30 AM - 4:00 PM ET (market hours only) |
| Executions per day | ~26 (first at 9:30, last at 3:45) |
| Days | Monday - Friday |
| Holidays | Skip (use FMP market status endpoint to verify market is open) |

**n8n cron expression:** `*/15 9-15 * * 1-5` (with additional logic for 9:30 start and 4:00 end)

### 2.3 Data Sources and API Endpoints

| Source | Endpoint | Data Retrieved | Calls/Execution |
|--------|----------|---------------|-----------------|
| FMP API | `GET /api/v3/quote/{symbols}` | Real-time price, volume, change, dayHigh, dayLow, yearHigh, yearLow, avgVolume, priceAvg50, priceAvg200 | 1 (batch all 11 tickers) |
| FMP API | `GET /api/v3/earning_calendar` | Upcoming earnings dates for universe names | 1 (cached daily, not every 15 min) |
| FMP API | `GET /api/v3/market-hours` | Market open/closed status | 1 (first execution only, cached) |

**Total FMP calls per execution:** 1 (batch quote)
**Total FMP calls per day:** ~26 (quotes) + 1 (earnings calendar, cached at 9:30 AM) = **~27 calls/day**

### 2.4 Processing Logic

```
WATCHLIST_ALERT_SYSTEM:

  ON_SCHEDULE (every 15 min, market hours):

    # Step 1: Market check
    IF market_is_closed():
      EXIT (no execution on holidays, pre/post-market)

    # Step 2: Fetch batch quote
    quotes = FMP_GET("/api/v3/quote/AAPL,MSFT,GOOGL,AMZN,AVGO,COST,V,MA,META,NVDA,SPY")

    # Step 3: Load previous state from n8n static data (persists between executions)
    prev_state = load_static_data("watchlist_state")

    # Step 4: Process each ticker
    alerts = []

    FOR each ticker in quotes:

      # --- 52-Week High/Low Alerts ---
      IF ticker.price >= ticker.yearHigh * 0.99:
        alerts.push({
          type: "52W_HIGH",
          ticker: ticker.symbol,
          price: ticker.price,
          level: ticker.yearHigh,
          context: "Within 1% of 52-week high ({yearHigh})"
        })

      IF ticker.price <= ticker.yearLow * 1.01:
        alerts.push({
          type: "52W_LOW",
          ticker: ticker.symbol,
          price: ticker.price,
          level: ticker.yearLow,
          context: "Within 1% of 52-week low ({yearLow})"
        })

      # --- Round Number Alerts ---
      round_levels = get_round_levels(ticker.price)
      FOR each level in round_levels:
        IF prev_state[ticker].price was below level AND ticker.price >= level:
          alerts.push({ type: "ROUND_CROSS_UP", ticker, price, level })
        IF prev_state[ticker].price was above level AND ticker.price <= level:
          alerts.push({ type: "ROUND_CROSS_DOWN", ticker, price, level })

      # --- Moving Average Alerts ---
      IF crossed_above(prev_state[ticker].price, ticker.price, ticker.priceAvg50):
        alerts.push({
          type: "MA50_CROSS_UP",
          ticker: ticker.symbol,
          price: ticker.price,
          level: ticker.priceAvg50,
          context: "Price crossed ABOVE 50-day MA"
        })

      IF crossed_below(prev_state[ticker].price, ticker.price, ticker.priceAvg50):
        alerts.push({
          type: "MA50_CROSS_DOWN",
          ticker: ticker.symbol,
          price: ticker.price,
          level: ticker.priceAvg50,
          context: "Price crossed BELOW 50-day MA"
        })

      IF crossed_above(prev_state[ticker].price, ticker.price, ticker.priceAvg200):
        alerts.push({
          type: "MA200_CROSS_UP",
          ticker: ticker.symbol,
          price: ticker.price,
          level: ticker.priceAvg200,
          context: "Price crossed ABOVE 200-day MA"
        })

      IF crossed_below(prev_state[ticker].price, ticker.price, ticker.priceAvg200):
        alerts.push({
          type: "MA200_CROSS_DOWN",
          ticker: ticker.symbol,
          price: ticker.price,
          level: ticker.priceAvg200,
          context: "Price crossed BELOW 200-day MA"
        })

      # --- Volume Alerts ---
      IF ticker.volume > (ticker.avgVolume * 2):
        volume_ratio = ticker.volume / ticker.avgVolume
        alerts.push({
          type: "UNUSUAL_VOLUME",
          ticker: ticker.symbol,
          price: ticker.price,
          volume: ticker.volume,
          avg_volume: ticker.avgVolume,
          context: "{volume_ratio}x average volume"
        })

    # Step 5: Earnings proximity check (uses cached earnings calendar)
    earnings_calendar = load_static_data("earnings_calendar")
    FOR each ticker in UNIVERSE:
      days_to_earnings = earnings_calendar[ticker].date - today
      IF days_to_earnings <= 5 AND days_to_earnings > 0:
        IF NOT already_notified_today(ticker, "EARNINGS_PROXIMITY"):
          alerts.push({
            type: "EARNINGS_PROXIMITY",
            ticker: ticker,
            earnings_date: earnings_calendar[ticker].date,
            days_away: days_to_earnings,
            context: "Earnings in {days_to_earnings} days — review options positions"
          })

    # Step 6: Deduplicate (don't send same alert type for same ticker within 2 hours)
    alerts = deduplicate(alerts, cooldown_hours=2)

    # Step 7: Send alerts
    IF alerts.length > 0:
      FOR each alert in alerts:
        send_telegram(format_alert(alert))

    # Step 8: Save current state for next execution
    save_static_data("watchlist_state", current_quotes)

HELPER: crossed_above(prev_price, curr_price, level):
  RETURN prev_price < level AND curr_price >= level

HELPER: crossed_below(prev_price, curr_price, level):
  RETURN prev_price > level AND curr_price <= level

HELPER: get_round_levels(price):
  # For prices <$50: check $5 intervals
  # For prices $50-$200: check $10 intervals
  # For prices $200-$500: check $25 intervals
  # For prices $500-$1000: check $50 intervals
  # For prices >$1000: check $100 intervals
  RETURN levels within 1% of current price
```

### 2.5 Output Format

**Telegram message template (single alert):**

```
WATCHLIST ALERT

Ticker: $AAPL
Alert: Price crossed ABOVE 50-day MA
Price: $265.40
Level: $265.12 (50-day MA)
Volume: 48.2M (1.3x avg)
Daily Change: +3.17%

Action: Bullish signal — consider for CSP entry
```

**Telegram message template (earnings proximity):**

```
EARNINGS WATCH

Ticker: $NVDA
Earnings: Feb 25, 2026 (3 days away)
Price: $184.97
IV Rank: Check options flow monitor

Action: Review/close any NVDA options positions.
Do NOT sell new options expiring after Feb 25
unless planned earnings trade.
```

### 2.6 n8n Node Diagram

```
[Schedule Trigger]
  |  (every 15 min, Mon-Fri)
  v
[Code Node: Market Hours Check]
  |  (verify 9:30 AM - 4:00 PM ET, skip holidays)
  |
  |-- IF market closed --> [Stop/No-Op]
  |
  v (market open)
[HTTP Request: FMP Batch Quote]
  |  GET /api/v3/quote/AAPL,MSFT,...,SPY
  v
[Code Node: Load Previous State]
  |  (from n8n static data)
  v
[Code Node: Alert Engine]
  |  - 52-week high/low detection
  |  - Round number crosses
  |  - 50-day / 200-day MA crosses
  |  - Volume anomaly (>2x avg)
  |  - Earnings proximity (from cached calendar)
  |  - Deduplication (2-hour cooldown)
  |
  |-- IF no alerts --> [Code Node: Save State] --> [Stop]
  |
  v (alerts exist)
[Split In Batches]
  |  (one alert at a time)
  v
[Telegram Node: Send Alert]
  |  (formatted message per template)
  v
[Code Node: Save State]
  |  (update static data with current prices + sent alerts log)
  v
[Stop]

--- SEPARATE SUBWORKFLOW (runs once daily at 9:25 AM) ---

[Schedule Trigger: 9:25 AM ET daily]
  v
[HTTP Request: FMP Earnings Calendar]
  |  GET /api/v3/earning_calendar?from=YYYY-MM-DD&to=YYYY-MM-DD
  v
[Code Node: Filter Universe + Cache]
  |  (save to static data for main workflow)
  v
[Stop]
```

### 2.7 Error Handling

| Error | Detection | Response |
|-------|-----------|----------|
| FMP API timeout | HTTP request node timeout (10s) | Retry 1x after 30s. If still failing, skip this execution. Log failure count. |
| FMP API rate limit (429) | HTTP status code | Back off. Skip this execution. Send Telegram alert if 3+ consecutive failures. |
| FMP returns partial data | Missing fields in response | Skip affected tickers. Process remaining normally. |
| n8n static data corruption | Try/catch in Code node | Reset state to empty (will miss cross alerts for one cycle but recovers automatically). |
| Telegram send failure | Telegram node error | Retry 1x. Queue alert for next execution if still failing. |
| Holiday/market closed | FMP market status endpoint | Skip execution cleanly. No error logged. |

### 2.8 API Calls Per Day

| Endpoint | Calls/Execution | Executions/Day | Daily Total |
|----------|----------------|----------------|-------------|
| FMP batch quote | 1 | 26 | 26 |
| FMP earnings calendar | 1 | 1 (cached) | 1 |
| FMP market status | 1 | 1 (cached) | 1 |
| **Workflow 1 Total** | | | **28** |

### 2.9 Implementation Priority and Effort

| Attribute | Value |
|-----------|-------|
| Priority | **P0** (build first) |
| Estimated effort | 2 days |
| Dependencies | None (FMP API already active) |
| Complexity | Medium (state management across executions requires careful testing) |
| Risk | Low (read-only, no trading actions) |

---

## 3. Workflow 2: Options Flow & IV Monitor

### 3.1 Purpose and Value Proposition

**What it does:** Scans implied volatility, put/call ratios, term structure, and large-flow positioning across the core universe twice daily, and surfaces premium-selling opportunities and risk signals.

**Edge it creates:** Options are Altamira's primary alpha source (CSP strategy backtested at 83% win rate, 1.34 Sharpe). The edge in premium selling comes from selling when IV is high relative to realized vol. This workflow systematically identifies those windows across all 11 tickers so no opportunity is missed.

**Decision it supports:** "Which tickers should I sell premium on today?" and "Are any positions at risk from IV changes?"

### 3.2 Trigger Schedule

| Parameter | Value |
|-----------|-------|
| Type | Cron schedule (two fixed times) |
| Schedule | 10:30 AM ET, 3:30 PM ET |
| Rationale | 10:30 AM: Post-open stabilization. 3:30 PM: Pre-close snapshot for next-day planning. |
| Executions per day | 2 |
| Days | Monday - Friday |

### 3.3 Data Sources and API Endpoints

| Source | Endpoint | Data Retrieved | Calls/Execution |
|--------|----------|---------------|-----------------|
| Massive.com | Options chain endpoint | IV by strike/expiry, greeks, volume, open interest | 10 (one per ticker, excl. SPY) |
| Massive.com | Historical IV endpoint | 1-year IV history for rank calculation | 10 (cached daily) |
| FMP API | `GET /api/v3/quote/{symbols}` | Current underlying prices | 1 (batch) |
| FMP API | `GET /api/v3/stock_market/actives` | Market-wide unusual activity | 1 |

### 3.4 Processing Logic

```
OPTIONS_FLOW_IV_MONITOR:

  ON_SCHEDULE (10:30 AM and 3:30 PM ET):

    # Step 1: Fetch underlying prices
    quotes = FMP_GET("/api/v3/quote/AAPL,MSFT,...,SPY")

    # Step 2: Fetch options chain data for each ticker
    FOR each ticker in UNIVERSE (excluding SPY):
      chain[ticker] = MASSIVE_GET("/options/chain/{ticker}")

    # Step 3: Load historical IV data (cached daily at 9:20 AM)
    iv_history = load_static_data("iv_history")

    # Step 4: Calculate IV Rank for each ticker
    results = []
    FOR each ticker in UNIVERSE:
      current_iv = chain[ticker].atm_iv
      iv_52w_high = iv_history[ticker].high_52w
      iv_52w_low = iv_history[ticker].low_52w
      iv_rank = (current_iv - iv_52w_low) / (iv_52w_high - iv_52w_low) * 100

      # IV Change Detection
      prev_iv = load_static_data("prev_session_iv")[ticker]
      iv_change_pct = (current_iv - prev_iv) / prev_iv * 100

      # Put/Call Ratio
      total_put_volume = SUM(chain[ticker].puts.volume)
      total_call_volume = SUM(chain[ticker].calls.volume)
      put_call_ratio = total_put_volume / total_call_volume

      # Term Structure Analysis
      near_iv = get_atm_iv(chain[ticker], target_dte=30)
      far_iv = get_atm_iv(chain[ticker], target_dte=90)
      term_structure = "CONTANGO" if far_iv > near_iv else "BACKWARDATION"
      term_spread = near_iv - far_iv

      # Delta-Weighted Volume
      call_delta_volume = SUM(strike.volume * abs(strike.delta)
        for strike in chain[ticker].calls WHERE strike.volume > 100)
      put_delta_volume = SUM(strike.volume * abs(strike.delta)
        for strike in chain[ticker].puts WHERE strike.volume > 100)
      net_delta_flow = call_delta_volume - put_delta_volume

      # Notable Strikes (volume > 5x open interest)
      notable_strikes = []
      FOR each strike in chain[ticker].all_strikes:
        IF strike.volume > (strike.open_interest * 5) AND strike.volume > 500:
          notable_strikes.push(strike)

      results.push({
        ticker, current_iv, iv_rank, iv_change_pct,
        put_call_ratio, term_structure, term_spread,
        net_delta_flow, notable_strikes
      })

    # Step 5: Flag conditions
    flags = []
    FOR each r in results:
      IF r.iv_rank > 50:
        flags.push({ type: "IV_RANK_HIGH", ticker: r.ticker, iv_rank: r.iv_rank })
      IF r.iv_change_pct < -20:
        flags.push({ type: "IV_CRUSH", ticker: r.ticker, iv_change: r.iv_change_pct })
      IF r.put_call_ratio > 1.5:
        flags.push({ type: "HIGH_PUT_CALL", ticker: r.ticker, ratio: r.put_call_ratio })
      IF r.put_call_ratio < 0.5:
        flags.push({ type: "LOW_PUT_CALL", ticker: r.ticker, ratio: r.put_call_ratio })
      IF r.term_structure == "BACKWARDATION" AND r.term_spread > 3:
        flags.push({ type: "INVERTED_TERM", ticker: r.ticker, spread: r.term_spread })

    # Step 6: Output
    results.sort_by(iv_rank, descending)
    send_telegram(format_iv_summary(results, flags))
    update_google_sheets("Options_IV_Log", results)
    save_static_data("prev_session_iv", current_iv_values)
```

### 3.5 Output Format

**Telegram message template:**

```
OPTIONS IV MONITOR — 10:30 AM Scan

Premium Selling Opportunities (IV Rank > 50):
  NVDA   IV Rank: 72  |  IV: 48.3%  |  +5.2% vs yesterday
  AVGO   IV Rank: 65  |  IV: 42.1%  |  +2.8% vs yesterday
  MSFT   IV Rank: 58  |  IV: 28.7%  |  -0.4% vs yesterday

Flags:
  NVDA: Inverted term structure (near 48.3% vs far 39.1%)
        Earnings Feb 25 — event risk priced in
  AMZN: Put/call ratio 1.62 — elevated put buying

Big Money Positioning:
  AAPL: Net bullish delta flow (+12,400 contracts)
  GOOGL: Net bearish delta flow (-8,200 contracts)

Notable Strikes:
  NVDA Mar 180 Put: 15,200 vol vs 2,100 OI (7.2x)

Full data logged to Google Sheets.
```

**Google Sheets columns (`Options_IV_Log` tab):**

| Column | Description |
|--------|-------------|
| Date | YYYY-MM-DD |
| Time | HH:MM (10:30 or 15:30) |
| Ticker | Symbol |
| Underlying Price | Current stock price |
| ATM IV | At-the-money implied volatility |
| IV Rank | 0-100 percentile vs 52-week range |
| IV Change (%) | vs previous session |
| Put/Call Ratio | Total put volume / total call volume |
| Term Structure | CONTANGO or BACKWARDATION |
| Term Spread | Near IV minus far IV |
| Net Delta Flow | Call delta vol minus put delta vol |
| Notable Strikes | Unusual activity |
| Flags | Alert types triggered |

### 3.6 n8n Node Diagram

```
[Schedule Trigger]
  |  (10:30 AM and 3:30 PM ET, Mon-Fri)
  v
[HTTP Request: FMP Batch Quote]
  v
[Split In Batches: 10 tickers]
  v
[HTTP Request: Massive.com Options Chain]
  |  (per ticker)
  v
[Code Node: Merge All Chain Data]
  v
[Code Node: Load Historical IV + Previous Session IV]
  v
[Code Node: IV Calculations Engine]
  v
[Code Node: Format Telegram Message]
  v
[Telegram Node: Send Summary]
  v
[Google Sheets Node: Append Row]
  v
[Code Node: Save State]
  v
[Stop]
```

### 3.7 Error Handling

| Error | Detection | Response |
|-------|-----------|----------|
| Massive.com API timeout | HTTP timeout (15s) | Retry 1x. Skip ticker and note "DATA MISSING" in output. |
| Massive.com rate limit | HTTP status code | Increase delay between calls (add 1s Wait node). |
| Partial chain data | Missing expirations | Use available data. Flag in output. |
| FMP quote failure | HTTP error | Fall back to previous quote. Flag staleness. |
| IV history cache empty | Missing static data | Trigger daily IV cache subworkflow. Skip IV Rank for this execution. |

### 3.8 API Calls Per Day

| Endpoint | Calls/Execution | Executions/Day | Daily Total |
|----------|----------------|----------------|-------------|
| FMP batch quote | 1 | 2 | 2 |
| FMP actives | 1 | 2 | 2 |
| Massive.com chain (per ticker) | 10 | 2 | 20 |
| Massive.com historical IV | 10 | 1 (cached) | 10 |
| Google Sheets write | 10 | 2 | 20 |
| **Workflow 2 Total** | | | **FMP: 4, Massive: 30, Sheets: 20** |

### 3.9 Implementation Priority and Effort

| Attribute | Value |
|-----------|-------|
| Priority | **P1** (build second) |
| Estimated effort | 3 days |
| Dependencies | Massive.com API endpoint documentation |
| Complexity | High (multiple calculations, multi-source data merge) |

---

## 4. Workflow 3: Sector Rotation Monitor

### 4.1 Purpose and Value Proposition

**What it does:** Tracks relative performance of all 11 GICS sectors versus SPY across four time horizons (1-day, 5-day, 20-day, 60-day), identifies rotation trends, and flags portfolio sector mismatches.

**Edge it creates:** Altamira's universe is tech-heavy. Sector rotation can turn a winning portfolio into a losing one before individual stock signals fire. This workflow detects macro rotation early and gives 5-20 trading days of warning.

**Decision it supports:** "Is the market environment favoring or punishing my sector exposure?"

### 4.2 Trigger Schedule

| Parameter | Value |
|-----------|-------|
| Type | Cron schedule |
| Schedule | 4:30 PM ET daily |
| Executions per day | 1 |
| Days | Monday - Friday |

### 4.3 Data Sources and API Endpoints

| Source | Endpoint | Data Retrieved | Calls/Execution |
|--------|----------|---------------|-----------------|
| FMP API | `GET /api/v3/quote/{symbols}` | Sector ETF prices + changes | 1 (batch) |
| FMP API | `GET /api/v3/historical-price-full/{symbol}` | 60-day price history per ETF | 12 (one per ETF + SPY) |

**Sector ETF Universe:** XLK, XLF, XLV, XLE, XLY, XLP, XLI, XLB, XLRE, XLU, XLC, SPY

### 4.4 Processing Logic

```
SECTOR_ROTATION_MONITOR:

  ON_SCHEDULE (4:30 PM ET daily):

    # Step 1: Fetch sector ETF quotes
    quotes = FMP_GET("/api/v3/quote/XLK,XLF,XLV,XLE,XLY,XLP,XLI,XLB,XLRE,XLU,XLC,SPY")

    # Step 2: Fetch 60-day historical prices
    history = {}
    FOR each etf in SECTOR_ETFS + [SPY]:
      history[etf] = FMP_GET("/api/v3/historical-price-full/{etf}?timeseries=60")

    # Step 3: Calculate relative strength vs SPY
    spy_returns = calculate_returns(history["SPY"])  # 1d, 5d, 20d, 60d
    results = []

    FOR each sector_etf in SECTOR_ETFS:
      etf_returns = calculate_returns(history[sector_etf])
      relative_strength = {
        "1d":  etf_returns["1d"]  - spy_returns["1d"],
        "5d":  etf_returns["5d"]  - spy_returns["5d"],
        "20d": etf_returns["20d"] - spy_returns["20d"],
        "60d": etf_returns["60d"] - spy_returns["60d"]
      }

      # Momentum direction
      IF relative_strength["5d"] > relative_strength["20d"] + 0.5:
        momentum = "GAINING"
      ELIF relative_strength["5d"] < relative_strength["20d"] - 0.5:
        momentum = "LOSING"
      ELSE:
        momentum = "NEUTRAL"

      results.push({ sector, etf, returns, relative_strength, momentum })

    # Step 4: Portfolio sector mismatch detection
    portfolio_sector_map = {
      "Technology": ["AAPL", "MSFT", "NVDA", "AVGO"],
      "Communication": ["GOOGL", "META"],
      "Consumer Discretionary": ["AMZN", "COST"],
      "Financials": ["V", "MA"]
    }

    mismatches = []
    FOR each sector, tickers in portfolio_sector_map:
      sector_result = results.find(r => r.sector == sector)
      IF sector_result.momentum == "LOSING" AND tickers.length >= 2:
        mismatches.push({ sector, tickers, signal: "Portfolio concentrated in weakening sector" })

    # Step 5: Market breadth classification
    strong_sectors = results.filter(r => r.relative_strength["20d"] > 1.0).length
    weak_sectors = results.filter(r => r.relative_strength["20d"] < -1.0).length

    IF strong_sectors >= 7: breadth = "BROAD_RALLY"
    ELIF weak_sectors >= 7: breadth = "BROAD_DECLINE"
    ELSE: breadth = "ROTATIONAL"

    # Step 6: Output
    results.sort_by(relative_strength["5d"], descending)
    send_telegram(format_sector_summary(results, mismatches, breadth))
    update_google_sheets("Sector_Rotation", results)
```

### 4.5 Output Format

**Telegram message template:**

```
SECTOR ROTATION MONITOR — Feb 18, 2026

Market Breadth: ROTATIONAL
(5 sectors gaining, 4 neutral, 2 losing vs SPY)

Leaders (5d relative strength vs SPY):
  XLF  Financials      +1.8%  Gaining
  XLRE Real Estate      +1.4%  Gaining
  XLI  Industrials      +0.9%  Gaining

Laggards:
  XLE  Energy          -1.5%  Losing
  XLP  Staples         -1.2%  Losing
  XLB  Materials       -0.8%  Losing

PORTFOLIO MISMATCH ALERT:
  Technology (XLK) — LOSING momentum
  You hold 4 names: AAPL, MSFT, NVDA, AVGO
  5-day relative strength: -0.7% vs SPY
  Action: Monitor closely. Consider reducing
  exposure if trend continues.

Full heatmap in Google Sheets.
```

### 4.6 n8n Node Diagram

```
[Schedule Trigger]
  |  (4:30 PM ET, Mon-Fri)
  v
[HTTP Request: FMP Batch Quote]
  v
[Split In Batches: 12 ETFs]
  v
[HTTP Request: FMP Historical Prices]
  |  (per ETF, 60 days)
  v
[Code Node: Merge Historical Data]
  v
[Code Node: Calculate Returns & Relative Strength]
  v
[Code Node: Portfolio Sector Mapping + Mismatch Detection]
  v
[IF Node: Mismatch Detected?]
  |-- YES --> [Telegram Node: Send with ALERT header]
  |-- NO  --> [Telegram Node: Send standard summary]
  v
[Google Sheets Node: Update Sector Rotation Tab]
  v
[Stop]
```

### 4.7 API Calls Per Day

| Endpoint | Calls/Execution | Executions/Day | Daily Total |
|----------|----------------|----------------|-------------|
| FMP batch quote | 1 | 1 | 1 |
| FMP historical prices | 12 | 1 | 12 |
| Google Sheets write | 11 | 1 | 11 |
| **Workflow 3 Total** | | | **FMP: 13, Sheets: 11** |

### 4.8 Implementation Priority and Effort

| Attribute | Value |
|-----------|-------|
| Priority | **P2** (build third) |
| Estimated effort | 1.5 days |
| Dependencies | None (FMP API already active) |
| Complexity | Medium |

---

## 5. Workflow 4: Portfolio Risk Dashboard

### 5.1 Purpose and Value Proposition

**What it does:** Pulls live position data from E-Trade, combines with options greeks from Massive.com and prices from FMP, produces a comprehensive portfolio risk snapshot with limit-breach detection. Runs at market close and on-demand via Telegram `/risk` command.

**Edge it creates:** Risk management is the foundation of Altamira's strategy. Without automated limit monitoring, every risk rule is just a suggestion. This workflow makes risk limits enforceable.

**Decision it supports:** "Is my portfolio within risk limits right now?"

### 5.2 Trigger Schedule

| Parameter | Value |
|-----------|-------|
| Type | Dual trigger: Cron + Telegram command |
| Scheduled | Daily at 4:05 PM ET |
| On-demand | Telegram "/risk" command |
| Executions per day | 1 (scheduled) + 0-3 (on-demand) |

### 5.3 Data Sources and API Endpoints

| Source | Endpoint | Data Retrieved | Calls/Execution |
|--------|----------|---------------|-----------------|
| E-Trade API | `GET /v1/accounts/{id}/portfolio` | Positions, quantities, cost basis, market value | 1 |
| E-Trade API | `GET /v1/accounts/{id}/balance` | Balance, buying power, cash, margin | 1 |
| Massive.com | Options greeks endpoint | Current greeks for open options positions | ~5 (per underlying with options) |
| FMP API | `GET /api/v3/quote/{symbols}` | Current prices + VIX | 1 (batch) |

### 5.4 Processing Logic

```
PORTFOLIO_RISK_DASHBOARD:

  ON_TRIGGER (schedule at 4:05 PM OR Telegram "/risk"):

    # Step 1: Authenticate E-Trade
    IF etrade_token_expired():
      send_telegram("E-Trade token expired. Using cached positions.")
      positions = load_static_data("last_known_positions")
      balances = load_static_data("last_known_balances")
      data_source = "CACHED"
    ELSE:
      positions = ETRADE_GET("/v1/accounts/{id}/portfolio")
      balances = ETRADE_GET("/v1/accounts/{id}/balance")
      data_source = "LIVE"
      save_static_data("last_known_positions", positions)
      save_static_data("last_known_balances", balances)

    # Step 2: Fetch prices + VIX
    quotes = FMP_GET("/api/v3/quote/{underlying_symbols},%5EVIX")

    # Step 3: Fetch options greeks
    FOR each options_position in positions:
      greeks[position] = MASSIVE_GET("/options/quote/{details}")

    # Step 4: Calculate Portfolio Greeks
    portfolio_greeks = { net_delta: 0, net_theta: 0, net_gamma: 0, net_vega: 0 }
    FOR each position in options_positions:
      multiplier = position.quantity * 100 * (position.direction == "SHORT" ? -1 : 1)
      portfolio_greeks.net_delta += greeks[position].delta * multiplier
      portfolio_greeks.net_theta += greeks[position].theta * multiplier
      portfolio_greeks.net_gamma += greeks[position].gamma * multiplier
      portfolio_greeks.net_vega  += greeks[position].vega  * multiplier
    FOR each equity_position:
      portfolio_greeks.net_delta += position.quantity

    # Step 5: Allocation Checks
    total_value = balances.total_value
    allocations = calculate_per_ticker_and_sector_allocations(positions, total_value)

    # Step 6: Breach Detection
    breaches = []
    IF allocations.options_pct > 30: breaches.push("OPTIONS: {pct}% > 30%")
    FOR each ticker: IF pct > 5: breaches.push("SINGLE NAME: {ticker} {pct}% > 5%")
    FOR each sector: IF pct > 25: breaches.push("SECTOR: {sector} {pct}% > 25%")
    IF allocations.cash_pct < 15: breaches.push("CASH: {pct}% < 15%")

    # Step 7: Drawdown
    portfolio_peak = load_or_update_peak(total_value)
    drawdown_pct = (total_value - portfolio_peak) / portfolio_peak * 100
    drawdown_tier = classify_drawdown(drawdown_pct)

    # Step 8: VIX Regime
    vix_regime = classify_vix(vix.price)

    # Step 9: Output
    send_telegram(format_risk_dashboard(...))
    IF breaches.length > 0:
      send_telegram(format_breach_alert(breaches), priority="HIGH")
    update_google_sheets("Risk_Dashboard", dashboard_data)
```

### 5.5 Output Format

**Telegram message template (dashboard):**

```
PORTFOLIO RISK DASHBOARD — Feb 18, 2026
Data: LIVE (E-Trade API)

Account Summary:
  Total Value:    $142,350
  Cash:           $28,470 (20.0%)
  Buying Power:   $56,940
  Day P&L:        +$1,245 (+0.88%)

Portfolio Greeks:
  Net Delta:    +245 (equivalent to 245 shares SPY)
  Net Theta:    +$87/day (daily income)
  Net Gamma:    -12
  Net Vega:     -$340

Allocation Check:
  Options:      22.4% / 30% limit     OK
  Cash:         20.0% / 15% minimum   OK
  Max Single:   MSFT 4.2% / 5% limit  OK
  Max Sector:   Tech 18.1% / 25%      OK

Drawdown: -1.3% from peak ($144,225)
  Tier: NORMAL

VIX Regime: NORMAL (20.29)

No breaches detected.
```

**Breach alert (sent separately):**

```
RISK LIMIT BREACH

SINGLE NAME: NVDA at 6.2% > 5% limit
  Action: Reduce NVDA exposure by ~$1,700

SECTOR: Technology at 26.8% > 25% limit
  Action: Trim tech positions or add non-tech exposure

Respond /risk for updated dashboard after adjustment.
```

### 5.6 n8n Node Diagram

```
[Schedule Trigger: 4:05 PM]     [Telegram Trigger: "/risk"]
         |                                |
         +--------------------------------+
         v
[Code Node: Check E-Trade Token]
  |-- Valid --> [E-Trade Portfolio + Balance]
  |-- Expired --> [Load Cached + Send Warning]
  v
[HTTP Request: FMP Batch Quote + VIX]
  v
[Massive.com Greeks (per options position)]
  v
[Code Node: Risk Calculations Engine]
  v
[Telegram Node: Send Dashboard]
  v
[IF Node: Breaches?]
  |-- YES --> [Telegram: Breach Alert]
  v
[Google Sheets: Update Risk Dashboard]
  v
[Stop]
```

### 5.7 API Calls Per Day

| Endpoint | Calls/Execution | Executions/Day | Daily Total |
|----------|----------------|----------------|-------------|
| E-Trade portfolio | 1 | 1-4 | 1-4 |
| E-Trade balance | 1 | 1-4 | 1-4 |
| FMP batch quote | 1 | 1-4 | 1-4 |
| Massive.com greeks | ~5 | 1-4 | 5-20 |
| Google Sheets write | 1 | 1-4 | 1-4 |
| **Workflow 4 Total (typical)** | | | **E-Trade: 2, FMP: 2, Massive: 5, Sheets: 1** |

### 5.8 Implementation Priority and Effort

| Attribute | Value |
|-----------|-------|
| Priority | **P1** (build when E-Trade API is online) |
| Estimated effort | 3 days |
| Dependencies | **E-Trade API must be online** |
| Complexity | High (three data sources, token management, on-demand trigger) |

**Phased approach:**
- **Phase A (immediate):** Build with manual Google Sheets positions input (no E-Trade).
- **Phase B (when E-Trade API live):** Swap to E-Trade API. Add Telegram trigger.

---

## 6. Workflow 5: Volatility Regime & Hedging Trigger

### 6.1 Purpose and Value Proposition

**What it does:** Monitors VIX, VVIX, and VIX term structure every 30 minutes during market hours. Classifies the current volatility regime and sends actionable hedging/sizing alerts when thresholds are crossed.

**Edge it creates:** Volatility regime changes are the single most important macro signal for an options-selling strategy. This workflow converts VIX-based sizing rules into automated triggers, catching regime changes intraday.

**Decision it supports:** "What is the current vol regime, and should I change my positioning?"

### 6.2 Trigger Schedule

| Parameter | Value |
|-----------|-------|
| Type | Cron schedule + daily summary |
| Intraday | Every 30 minutes (9:30 AM - 4:00 PM ET) |
| Daily summary | 4:00 PM ET |
| Executions per day | ~14 |
| Days | Monday - Friday |

### 6.3 Data Sources and API Endpoints

| Source | Endpoint | Data Retrieved | Calls/Execution |
|--------|----------|---------------|-----------------|
| FMP API | `GET /api/v3/quote/%5EVIX` | VIX level, change | 1 |
| FMP API | `GET /api/v3/quote/%5EVVIX` | VVIX | 1 |
| FMP API | `GET /api/v3/historical-price-full/%5EVIX?timeseries=5` | 5-day VIX history | 1 (cached daily) |
| Massive.com | SPY options chain (near + far term) | Term structure proxy | 2 |

### 6.4 Processing Logic

```
VOLATILITY_REGIME_MONITOR:

  ON_SCHEDULE (every 30 min, market hours):

    # Step 1: Fetch VIX + VVIX
    vix = FMP_GET("/api/v3/quote/%5EVIX")
    vvix = FMP_GET("/api/v3/quote/%5EVVIX")

    # Step 2: Load previous state
    prev_state = load_static_data("vol_regime_state")

    # Step 3: VIX Level Classification
    IF vix.price < 15: regime = "LOW_COMPLACENT"
    ELIF vix.price <= 25: regime = "NORMAL"
    ELIF vix.price <= 35: regime = "ELEVATED"
    ELSE: regime = "CRISIS"

    # Step 4: Rate of Change
    prev_close = load_static_data("vix_5d_history")[0].close
    vix_daily_change_pct = ((vix.price - prev_close) / prev_close) * 100

    # Step 5: Term Structure
    spy_near = MASSIVE_GET("/options/chain/SPY?expiry=near_month")
    spy_far = MASSIVE_GET("/options/chain/SPY?expiry=second_month")
    near_atm_iv = get_atm_iv(spy_near)
    far_atm_iv = get_atm_iv(spy_far)
    term_structure = "BACKWARDATION" if near_atm_iv > far_atm_iv else "CONTANGO"

    # Step 6: VVIX Analysis
    vvix_elevated = vvix.price > 120
    vvix_spike = vvix.changesPercentage > 15

    # Step 7: Trigger Detection
    triggers = []

    IF regime != prev_state.regime:
      triggers.push({ type: "REGIME_CHANGE", from: prev_state.regime, to: regime, priority: "HIGH" })

    IF prev_state.vix <= 25 AND vix.price > 25:
      triggers.push({ type: "VIX_ABOVE_25", priority: "HIGH" })

    IF prev_state.vix <= 35 AND vix.price > 35:
      triggers.push({ type: "VIX_ABOVE_35", priority: "CRITICAL" })

    IF prev_state.vix >= 15 AND vix.price < 15:
      triggers.push({ type: "VIX_BELOW_15", priority: "MEDIUM" })

    IF abs(vix_daily_change_pct) > 20:
      triggers.push({ type: "VIX_ROC_20", change: vix_daily_change_pct, priority: "HIGH" })

    IF abs(vix_daily_change_pct) > 30:
      triggers.push({ type: "VIX_ROC_30", change: vix_daily_change_pct, priority: "CRITICAL" })

    IF term_structure == "BACKWARDATION" AND prev_state.term_structure == "CONTANGO":
      triggers.push({ type: "TERM_INVERSION", priority: "HIGH" })

    IF vvix_spike AND NOT prev_state.vvix_spike_notified:
      triggers.push({ type: "VVIX_SPIKE", level: vvix.price, priority: "MEDIUM" })

    # Step 8: Send alerts
    IF triggers.length > 0:
      FOR each trigger in triggers:
        send_telegram(format_vol_trigger(trigger, vix, vvix, term_structure))

    # Step 9: Daily summary (4:00 PM only)
    IF is_market_close_execution():
      send_telegram(format_daily_vol_summary(vix, vvix, regime, term_structure))
      update_google_sheets("Vol_Regime_Log", summary)

    # Step 10: Save state
    save_static_data("vol_regime_state", { vix_level: vix.price, regime, term_structure, ... })
```

### 6.5 Output Format

**Telegram trigger alert:**

```
VOL REGIME ALERT — HIGH PRIORITY

Trigger: VIX crossed ABOVE 25
VIX: 25.34 (+18.2% today)
Previous Regime: NORMAL
New Regime: ELEVATED

Term Structure: CONTANGO (normal)
VVIX: 108.5 (normal)

Sizing Guidance:
Reduce new positions to 75% of standard size.
Review all open short premium positions.
```

**Daily summary (4:00 PM):**

```
VOL REGIME DAILY SUMMARY — Feb 18, 2026

VIX Close:        20.29  (+2.1% today)
VIX Regime:       NORMAL
Term Structure:   CONTANGO (far 18.2% > near 17.8%)
VVIX:             105.3 (normal)

Today's Triggers:  0 (quiet session)

Sizing Guidance:   Standard sizing applies.
Hedging Posture:   Normal — no action needed.

5-Day VIX Trend:
  Feb 14: 19.12
  Feb 15: 19.45
  Feb 17: 19.87
  Feb 18: 20.29   <-- trending higher, watch for 25 threshold
```

**Critical alert:**

```
VOL REGIME ALERT — CRITICAL

EMERGENCY: VIX +32.4% TODAY (now 26.87)
Regime: CRISIS APPROACHING

IMMEDIATE ACTIONS REQUIRED:
1. Review ALL open options positions
2. No new trades until further notice
3. Consider closing short premium at a loss
   rather than risking assignment
4. Check portfolio delta — reduce if net long

Respond /risk for current portfolio exposure.
```

### 6.6 n8n Node Diagram

```
[Schedule Trigger]
  |  (every 30 min, Mon-Fri, market hours)
  v
[Code Node: Market Hours Check]
  |-- Outside hours --> [Stop]
  v
[HTTP Request: FMP VIX]     [HTTP Request: FMP VVIX]
  v                          v
[Code Node: Merge VIX + VVIX]
  v
[HTTP Request: Massive.com SPY Near-Month]
[HTTP Request: Massive.com SPY Far-Month]
  v
[Code Node: Load Previous State + History]
  v
[Code Node: Volatility Regime Engine]
  |  - Classification, ROC, term structure, triggers
  v
[IF Node: Triggers?]
  |-- YES --> [Telegram: Send Trigger Alerts]
  v
[IF Node: 4:00 PM?]
  |-- YES --> [Telegram: Daily Summary] + [Google Sheets: Log]
  v
[Code Node: Save State]
  v
[Stop]
```

### 6.7 API Calls Per Day

| Endpoint | Calls/Execution | Executions/Day | Daily Total |
|----------|----------------|----------------|-------------|
| FMP VIX quote | 1 | 14 | 14 |
| FMP VVIX quote | 1 | 14 | 14 |
| FMP VIX history | 1 | 1 (cached) | 1 |
| Massive.com SPY near-month | 1 | 14 | 14 |
| Massive.com SPY far-month | 1 | 14 | 14 |
| Google Sheets write | 1 | 1 | 1 |
| **Workflow 5 Total** | | | **FMP: 29, Massive: 28, Sheets: 1** |

### 6.8 Implementation Priority and Effort

| Attribute | Value |
|-----------|-------|
| Priority | **P0** (build alongside Workflow 1) |
| Estimated effort | 2 days |
| Dependencies | FMP API, Massive.com |
| Complexity | Medium |

---

## 7. Combined Daily Schedule

```
TIME        WORKFLOW                                    TYPE
------------------------------------------------------------------------
07:00 AM    Market Commenter v3.1 (existing)            Daily report
09:20 AM    [WF2] IV History Cache (subworkflow)        Daily cache
09:25 AM    [WF1] Earnings Calendar Cache               Daily cache
09:25 AM    [WF5] VIX 5-Day History Cache               Daily cache
09:30 AM    [WF1] Watchlist Alert System                Every 15 min
09:30 AM    [WF5] Vol Regime Monitor                    Every 30 min
09:45 AM    [WF1] Watchlist Alert System                |
10:00 AM    [WF1] + [WF5]                              |
10:15 AM    [WF1] Watchlist Alert System                |
10:30 AM    [WF1] + [WF5]                              |
10:32 AM    [WF2] Options Flow & IV Monitor             AM scan
  ...       (pattern continues every 15/30 min)         |
03:30 PM    [WF1] + [WF5]                              |
03:32 PM    [WF2] Options Flow & IV Monitor             PM scan
03:45 PM    [WF1] Watchlist Alert System (last)         |
04:00 PM    [WF5] Vol Regime Daily Summary              End-of-day
04:05 PM    [WF4] Portfolio Risk Dashboard              Daily close
04:30 PM    [WF3] Sector Rotation Monitor               Post-market

ON-DEMAND:
  /risk     [WF4] Portfolio Risk Dashboard              Via Telegram
------------------------------------------------------------------------

DAILY EXECUTION COUNTS:
  Market Commenter:   1 execution
  Watchlist Alerts:   ~26 executions
  Options IV:         2 executions
  Sector Rotation:    1 execution
  Portfolio Risk:     1 + ad hoc executions
  Vol Regime:         ~14 executions
  ----------------------------------------
  TOTAL:              ~45 executions per day
```

---

## 8. Total API Call Budget

### Daily API Calls by Source

| Workflow | FMP Calls | Massive.com Calls | E-Trade Calls | Sheets Writes |
|----------|-----------|-------------------|---------------|---------------|
| Market Commenter (existing) | ~10 | 0 | 0 | 0 |
| WF1: Watchlist Alerts | 28 | 0 | 0 | 0 |
| WF2: Options IV Monitor | 4 | 30 | 0 | 20 |
| WF3: Sector Rotation | 13 | 0 | 0 | 11 |
| WF4: Portfolio Risk | 2-8 | 5-20 | 2-8 | 1-4 |
| WF5: Vol Regime | 29 | 28 | 0 | 1 |
| **DAILY TOTAL** | **86-92** | **63-78** | **2-8** | **33-36** |

### API Rate Limit Analysis

| API | Daily Budget | Known Rate Limit | Utilization | Status |
|-----|-------------|-----------------|-------------|--------|
| FMP API | ~92/day | 300/min (standard) | <1% | Safe |
| Massive.com | ~78/day | TBD | TBD | Verify |
| E-Trade API | ~8/day | 2 req/sec | <1% | Safe |
| Google Sheets | ~36/day | 300/min | <1% | Safe |
| Telegram | ~50-80 msg/day | 30 msg/sec | <1% | Safe |

---

## 9. Implementation Roadmap

### Phase 1: Foundation (Week of Feb 24)

**Build Workflow 1 (Watchlist Alerts) + Workflow 5 (Vol Regime)**

| Day | Task | Output |
|-----|------|--------|
| Day 1 | WF1: Build schedule trigger + FMP batch quote + market hours check | Core data pipeline |
| Day 2 | WF1: Build alert engine + Telegram output + testing | WF1 live |
| Day 3 | WF5: Build VIX/VVIX fetch + regime classification + triggers | Core vol monitoring |
| Day 4 | WF5: Build term structure + daily summary + testing | WF5 live |

### Phase 2: Options Intelligence (Week of Mar 3)

**Build Workflow 2 (Options IV Monitor)**

| Day | Task | Output |
|-----|------|--------|
| Day 5 | WF2: Massive.com chain fetching + IV Rank + cache | Options data pipeline |
| Day 6 | WF2: Put/call ratio + term structure + delta flow | Full IV engine |
| Day 7 | WF2: Telegram + Google Sheets + testing | WF2 live |

### Phase 3: Portfolio Awareness (Week of Mar 10)

**Build Workflow 4 (Portfolio Risk Dashboard)**

| Day | Task | Output |
|-----|------|--------|
| Day 8 | WF4 Phase A: Google Sheets input + FMP + risk calcs | Manual-input dashboard |
| Day 9 | WF4 Phase A: Breach detection + Telegram + alerts | WF4 Phase A live |
| Day 10 | WF4 Phase B: E-Trade API swap + Telegram trigger | WF4 fully live |

### Phase 4: Macro Overlay (Week of Mar 17)

**Build Workflow 3 (Sector Rotation Monitor)**

| Day | Task | Output |
|-----|------|--------|
| Day 11 | WF3: Sector ETF history + relative strength + mismatch + output | WF3 live |

### Phase 5: Hardening (Week of Mar 24)

- Monitor all workflows for 1 week
- Tune alert thresholds
- Build health monitoring workflow

### Visual Roadmap

```
Week 1 (Feb 24):  [===WF1 (Watchlist)=====][===WF5 (Vol Regime)===]
Week 2 (Mar 3):   [=======WF2 (Options IV Monitor)================]
Week 3 (Mar 10):  [=======WF4 (Portfolio Risk Dashboard)===========]
Week 4 (Mar 17):  [==WF3 (Sector)==][====Hardening & Tuning========]
Week 5 (Mar 24):  [=========Monitoring + Health Dashboard==========]
```

---

## 10. Maintenance Plan

### 10.1 Workflow Health Monitoring

Create a meta-workflow that monitors health of all other workflows daily at 5:00 PM ET. Query n8n API for execution counts, failures, and timing. Send Telegram health report.

### 10.2 Weekly Review Protocol

Every Monday morning, 15 minutes:

| Check | Action |
|-------|--------|
| Alert volume | Target 5-15 actionable alerts/day. Tighten or loosen thresholds. |
| False positives | Adjust logic for alerts that didn't lead to action. |
| Missed events | Add detection for significant moves that weren't alerted. |
| API errors | Check recurring failures, rate limits, credential expiration. |
| Google Sheets data | Spot-check integrity, gaps, duplicates. |
| Telegram formatting | Ensure readability on mobile. |

### 10.3 Monthly Maintenance Tasks

| Task | Frequency |
|------|-----------|
| Review and update watchlist universe | Monthly |
| Verify API rate limit usage | Monthly |
| Prune Google Sheets data (archive old rows) | Monthly |
| Test on-demand Telegram triggers | Monthly |
| Review n8n execution logs | Monthly |
| Update sector ETF list | Annually |

### 10.4 Credential Rotation Schedule

| Credential | Rotation | Notes |
|------------|----------|-------|
| FMP API key | Annually | Stored in n8n credentials |
| Massive.com API key | Per provider policy | Stored in n8n credentials |
| E-Trade OAuth tokens | **Daily** (auto-expire midnight ET) | Handle in workflow logic |
| Telegram bot token | Annually | Stored in n8n credentials |
| Google Sheets OAuth | Auto-refreshes | n8n handles automatically |

### 10.5 Scaling Considerations

| Current (11 tickers) | Future (25+ tickers) | Action Needed |
|-----------------------|---------------------|---------------|
| FMP batch quote: 1 call | Still 1 call | No change |
| Massive.com: 10 calls | 25+ calls | Check rate limits; stagger |
| Alert volume: ~5-15/day | 15-40/day | Implement summary batching |
| Google Sheets: 33 rows/day | 80+ rows/day | Split tabs or move to database |

---

## 11. Appendix: Telegram Message Templates

### Formatting Standards

- **Headers in CAPS** for quick scanning on mobile
- **Monospace** for numbers and data tables
- **Bold** for tickers and key values
- Messages under 4096 characters (Telegram limit)
- Liberal line breaks for mobile readability
- Workflow name in every message header

### Alert Priority Levels

| Priority | Behavior | Notification |
|----------|----------|--------------|
| CRITICAL | Send immediately, retry 3x | Sound |
| HIGH | Send immediately, retry 1x | Sound |
| MEDIUM | Send immediately, standard retry | Silent |
| LOW / INFO | Batch into daily summaries | Silent |

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-18 | Initial design document — 5 workflows, full specifications |

---

*This document is the blueprint for Altamira Capital's automated market monitoring infrastructure. Each workflow is designed to be built independently and incrementally. Start with the P0 workflows (Watchlist Alerts + Vol Regime) and layer on additional intelligence over 4 weeks.*
