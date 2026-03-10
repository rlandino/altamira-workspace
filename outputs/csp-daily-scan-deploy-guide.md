# CSP Daily Scan — Deploy Guide

Deploy the **Altamira - CSP Daily Scan (P0)** workflow to your n8n instance (e.g. n8n cloud) so it runs at **10:30 AM ET** on weekdays and sends scored CSP opportunities to Telegram and logs to Google Sheets.

---

## 1. Import the workflow

1. Open your n8n instance (e.g. **https://rlandino.app.n8n.cloud**).
2. Go to **Workflows** → **Add workflow** (or **Import from File**).
3. **Import from file:**  
   - Click the **⋮** menu (top right) → **Import from File** (or **Import**).  
   - Select: **`outputs/n8n-workflow-csp-daily-scan.json`** from this workspace.  
   - Or copy the entire contents of that file and use **Import from URL/Clipboard** if your n8n supports it.
4. The workflow opens with 17 nodes (trigger, Code, HTTP Request, Telegram, Google Sheets, sticky notes). Save it (e.g. name: **Altamira - CSP Daily Scan (P0)**).

---

## 2. Configure credentials (after import or API deploy)

Attach credentials to these nodes (red “missing credential” will disappear once set):

| Node(s) | Credential type | What to use |
|--------|------------------|-------------|
| **FMP: VIX & SPY Quote**, **FMP: Universe Quotes (11 Tickers)**, **FMP: Earnings Calendar (Next 45 Days)** | **HTTP Query Auth** (or Header Auth) | FMP API key: `FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz`. Create a credential named e.g. “FMP API Key” with the key as the query parameter `apikey` (or in header). |
| **Send Telegram Alert** | **Telegram API** | Your Telegram Bot token. Create or select a credential (e.g. “Altamira Telegram Bot”). |
| **Log to Google Sheets** | **Google Sheets OAuth2** | Your Google account with access to the paper-trading workbook. Create or select (e.g. “Google Sheets (Altamira)”). |

- Open each node listed above → **Credential** → create new or select existing.
- The **Fetch Options Chains** Code node has FMP and Massive API keys **hardcoded** in the script. That’s intentional so the workflow runs without extra credentials; you can later move them to n8n credentials or env vars if you prefer.

---

## 3. Set environment variables

The workflow expects these **n8n environment variables** (Settings → Variables, or your hosting’s env config):

| Variable | Description | Example |
|----------|-------------|---------|
| **TELEGRAM_CHAT_ID** | Telegram chat or group where the daily alert is sent | Your numeric chat ID (e.g. from @userinfobot or your bot’s updates). |
| **GOOGLE_SHEET_ID** | ID of the Google Sheet used for “CSP Scans” (from the sheet URL) | From `https://docs.google.com/spreadsheets/d/<GOOGLE_SHEET_ID>/edit`. |

- If you don’t set these, **Send Telegram Alert** and **Log to Google Sheets** will fail at runtime until you add them.
- For testing you can temporarily set **Send Telegram Alert** to a fixed `chatId` and **Log to Google Sheets** to a fixed `documentId` in the node parameters instead of `$env.*`.

---

## 4. Google Sheet “CSP Scans”

- In the same workbook you use for paper trading (or a dedicated one), ensure a sheet named **CSP Scans** exists.
- Recommended columns (order can vary if you use “autoMapInputData”):  
  **Date**, **VIX**, **Regime**, **Sizing%**, **Ticker1**, **Strike1**, **Expiry1**, **Premium1**, **Delta1**, **AnnReturn1**, **Score1**, **Ticker2**, **Strike2**, **Expiry2**, **Premium2**, **Delta2**, **AnnReturn2**, **Score2**, **Ticker3**, **Strike3**, **Expiry3**, **Premium3**, **Delta3**, **AnnReturn3**, **Score3**, **TotalCollateral**, **Cash%**, **ContractsScanned**, **Notes**.
- In the **Log to Google Sheets** node, set **Document** to the workbook and **Sheet** to **CSP Scans** (or reference `$env.GOOGLE_SHEET_ID` and sheet name **CSP Scans**).

---

## 5. Activate and test

1. **Save** the workflow.
2. Turn the workflow **Active** (toggle in the top right).
3. **Test run:** Use **Execute Workflow** (or “Test workflow”) to run once.  
   - If market is open and the schedule logic passes, you should see Telegram message and a new row in **CSP Scans**.  
   - If market is closed or it’s a weekend, the **Market Hours Check** node may return no items and the run will stop without sending (that’s expected).
4. Confirm the **Schedule Trigger** is **10:30 AM ET**, **Monday–Friday** (already set in the imported JSON).

---

## 6. Summary checklist

- [ ] Workflow imported from `outputs/n8n-workflow-csp-daily-scan.json`
- [ ] FMP credential set on all three FMP HTTP Request nodes
- [ ] Telegram credential set on **Send Telegram Alert**
- [ ] Google Sheets OAuth2 credential set on **Log to Google Sheets**
- [ ] `TELEGRAM_CHAT_ID` and `GOOGLE_SHEET_ID` set in n8n (or overridden in nodes for testing)
- [ ] Sheet **CSP Scans** exists with correct columns
- [ ] Workflow saved and **Active**
- [ ] One manual test run executed

After this, the CSP Daily Scan will run automatically at 10:30 AM ET on weekdays (when the market is open and not a 2026 NYSE holiday).
