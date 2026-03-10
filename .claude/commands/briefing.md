# /briefing — Daily Market Briefing (Market Commenter style)

Produce a full daily market briefing: indices, hot stock/biggest loser, best/worst sector, SPY/QQQ/VIX, earnings calendar, index vs 5D/20D averages, support/resistance, trend, commentary, and an index performance chart.

## Instructions

You are generating a Market Commenter-style daily briefing for Altamira Capital. Follow these steps exactly.

**Data sources:** FMP uses two base URLs with the same API key. Use the key: `FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz`.

- **FMP v3** (base `https://financialmodelingprep.com/api/v3`) — quotes, earnings calendar.
- **FMP stable** (base `https://financialmodelingprep.com/stable`) — gainers, losers, sector snapshot, historical EOD. Append `?apikey={KEY}` or `&apikey={KEY}` to all requests.

---

### Step 1: Resolve date and output paths

- Use **today's date** in YYYY-MM-DD format (or user override from $ARGUMENTS if provided later).
- Output paths: `outputs/briefing-{DATE}.md`, `outputs/briefing-chart-{DATE}.png`.
- Ensure `outputs/` exists (create if needed).

---

### Step 2: Fetch data (parallel where possible)

**FMP v3** (base: `https://financialmodelingprep.com/api/v3`):

1. **Quote** — indices, VIX, SPY, QQQ (level, change %):
   ```
   GET /quote/^GSPC,^DJI,^IXIC,^VIX,SPY,QQQ?apikey={KEY}
   ```
   Map symbols: ^GSPC = S&P 500, ^DJI = Dow Jones, ^IXIC = Nasdaq Composite. Extract: price, changesPercentage (or equivalent).

2. **Earnings calendar** — companies reporting earnings (today through next 7 days):
   ```
   GET /earning_calendar?from={TODAY}&to={TODAY+7}&apikey={KEY}
   ```
   Use from = today, to = 7 days ahead. Parse: date, symbol, epsEstimated, revenueEstimated if present.

**FMP stable** (base: `https://financialmodelingprep.com/stable`):

3. **Biggest gainers** — hot stock:
   ```
   GET /biggest-gainers?apikey={KEY}
   ```
   Take the top (first) entry: symbol, changesPercentage (or equivalent).

4. **Biggest losers** — biggest loser:
   ```
   GET /biggest-losers?apikey={KEY}
   ```
   Take the top (first) entry: symbol, changesPercentage.

5. **Sector performance snapshot** — best and worst sector:
   ```
   GET /sector-performance-snapshot?date={TODAY}&apikey={KEY}
   ```
   If the API returns an array or object with sector names and performance %, identify the best and worst by performance. If date=today has no data (e.g. market closed), try the most recent trading day. Document the sector name and % change.

6. **Historical index EOD** — for 5D/20D averages and support/resistance (last ~30 trading days):
   ```
   GET /historical-price-eod/light?symbol=^GSPC&from={FROM}&to={TO}&apikey={KEY}
   ```
   Set FROM to 30 calendar days ago and TO to today (YYYY-MM-DD). Response typically has date and close (and possibly open/high/low). If the endpoint uses different parameter names (e.g. `startDate`/`endDate`), use the FMP stable docs. Repeat for ^DJI and ^IXIC if you want multi-index 5D/20D; minimum is ^GSPC for the main briefing.

---

### Step 3: Compute derived metrics

- **5D and 20D averages:** From the historical close series for ^GSPC (and optionally ^DJI, ^IXIC), compute the simple moving average of the last 5 and 20 closing prices. Compare the current index level (from quote) to 5D avg and 20D avg; show in the report as "vs 5D Avg" and "vs 20D Avg" (e.g. "above 5D" / "below 20D" or numeric).
- **Support / Resistance:** From the same historical series (e.g. last 20 trading days), take the 20-day high as **Resistance** and the 20-day low as **Support**. State in the report that these are derived from recent N-day high/low (N=20).
- **Trend:** Apply to the primary index (S&P 500 / ^GSPC): **Bullish** if current price above both 5D and 20D average; **Bearish** if below both; **Mixed** otherwise.
- **VIX context:** Map VIX level to a short label: e.g. **Elevated** if > 20, **Low** if < 15, **Normal** (or "Moderate") if 15–20. Include one sentence in the report (e.g. "VIX is elevated at 22.")

---

### Step 4: Economic calendar section

"Companies reporting earnings" = table from the earning_calendar response for the chosen from/to. Columns: **Date** | **Symbol** | **EPS estimate** (if available). Sort by date. If no results, state "No earnings in the next 7 days" or similar.

---

### Step 5: Write the report

Write a single markdown file to `outputs/briefing-{DATE}.md` with the following sections in this order:

1. **Market indices** — S&P 500, Nasdaq Composite, Dow Jones: level and day change %.
2. **Hot stock** — Ticker (change %).
3. **Biggest loser** — Ticker (change %).
4. **Best sector** — Name (change %).
5. **Worst sector** — Name (change %).
6. **SPY** — Level (change %).
7. **QQQ** — Level (change %).
8. **VIX** — Level and relative description (e.g. elevated / normal / low).
9. **Economic calendar** — Companies reporting earnings (table: Date | Symbol | EPS estimate).
10. **Current index levels vs averages** — For S&P 500 (and optionally others): current level vs 5D avg and vs 20D avg (e.g. "Above 5D, below 20D" or numeric).
11. **Resistance / Support** — Resistance level, Support level (from 20-day high/low); note that these are derived from recent price range.
12. **Trend** — Bullish / Bearish / Mixed (for S&P 500).
13. **Commentary** — Two to four sentences on indices (higher/lower/mixed) and sector rotation (e.g. which sectors leading/lagging). Do not invent news; stick to price/level and sector data.
14. **Index performance chart** — If the chart was generated (Step 6), embed: `![Index performance](outputs/briefing-chart-{DATE}.png)`. Otherwise write "Chart not generated" or omit.

Use clear headings (## or ###) and short bullets or tables so the briefing is scannable.

---

### Step 6: Generate index performance chart (recommended)

Run the chart script so the briefing includes a visual:

```bash
python scripts/briefing_chart.py --date {DATE}
```

(Omit `--date` to use today.) The script writes `outputs/briefing-chart-{DATE}.png`. After the report is written, ensure section 14 references this image. If the script fails (e.g. missing dependencies), note in the report that the chart could not be generated and continue.

---

### Step 7: Summarize in chat

After writing the file (and optionally the chart), give a 2–3 sentence recap in chat:

- Main index move and trend (e.g. "S&P 500 up 0.5%, trend Bullish; VIX low at 14.")
- Best/worst sector and hot stock/loser in one line.
- Report path: `outputs/briefing-{DATE}.md` (and chart path if generated).

Also output a **Voice script** (2–4 sentences), phrased for listening, with the same content as the recap (e.g. "Your daily briefing. S&P 500 is up 0.5 percent, trend Bullish. VIX is low at 14. Best sector today is Technology; worst is Energy. Report saved to outputs/briefing-{DATE}.md."). Label it clearly so it can be used for TTS.

---

### Step 8: Optional — play summary aloud (voice)

If the user wants to hear the summary, run the speak script on the voice script from Step 7:

```bash
python scripts/speak_text.py --text "&lt;Voice script text from Step 7&gt;"
```

To save audio to a file (uses edge-tts; does not speak aloud unless you omit --no-speak):

```bash
python scripts/speak_text.py --text "&lt;Voice script&gt;" --out outputs/briefing-{DATE}-audio.mp3 --no-speak
```

To speak aloud and also save: omit `--no-speak` when using `--out`. If the voice script was written to a file (e.g. `outputs/briefing-voice-{DATE}.txt`), use:

```bash
python scripts/speak_text.py --file outputs/briefing-voice-{DATE}.txt
```

**Dependencies:** Speaking aloud uses `pyttsx3` (offline; `pip install pyttsx3`). Saving to MP3 uses `edge-tts` (`pip install edge-tts`). If the script fails (e.g. missing library), note in chat and continue.

**Cross-command:** After any briefing, the user can run `/speak briefing` to hear the Voice script without re-running the briefing.

---

## Context

- **Altamira Capital** is a multi-strategy investment firm focused on US large/mega-cap equities and options.
- **Market Commenter** (n8n): a full daily report may also be produced by the n8n workflow. This command is the in-session alternative when that workflow has not run or when a quick briefing is needed.
- **Investment thesis:** `outputs/altamira-investment-thesis.md` (for strategy alignment if needed).
