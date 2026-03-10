# Trading Infrastructure Setup — Altamira Capital

**Version:** 1.1
**Date:** 2026-02-18 (updated)
**Target Completion:** 2026-02-28
**Status:** In Progress — significant deliverables complete, E-Trade API setup is critical path

---

## Next actions (priority order)

1. **E-Trade API (critical path)** — Complete Phase 2: Developer Registration, OAuth 1.0a flow, and test API calls (list accounts, portfolio). See `outputs/etrade-api-setup-guide.md`.
2. **Account configuration** — Complete Phase 1 checkboxes: Options Level 3, margin, E-Trade Pro watchlists (AAPL, MSFT, GOOGL, AMZN, AVGO, COST, V, MA, META, NVDA, SPY), 2FA.
3. **n8n + E-Trade** — Once API keys and OAuth work: connect Daily Portfolio Snapshot workflow (`n8n-workflow-1-daily-portfolio-snapshot.json`) to E-Trade sandbox/production per Phase 4.
4. **Paper trading go-live** — After pre-launch check passes: run `scripts/pre-launch-check.py`, then start paper trading per `outputs/paper-trading-plan.md` (Mar 1 target).

**Single next step:** Register for E-Trade Developer account and obtain API credentials (consumer key + secret); document in password manager. Then test OAuth 1.0a flow per etrade-api-setup-guide.

---

## Overview

This checklist covers everything needed to go from current state (automation tools built, no brokerage integration) to paper trading with full position tracking and risk management. Organized by phase with a two-week timeline.

**Prerequisites:** E-Trade account exists. Automation stack (OCA, Market Commenter, Earnings Alpha, Fiscal Platform) operational. n8n cloud instance running. FMP and Massive.com API keys active.

---

## Phase 1: E-Trade Account Configuration

**Target:** Week 1 (Feb 17-21)

### Account Setup

- [ ] Confirm account type: Individual margin account
- [ ] Apply for Options Level 3 approval (spreads, multi-leg strategies)
  - Level 1: Covered calls, protective puts
  - Level 2: Long calls/puts
  - **Level 3: Spreads (bull put, bear call, jade lizard, iron condor)**
  - Requires: Options trading experience, financial suitability questionnaire
- [ ] Enable margin trading
- [ ] Evaluate portfolio margin eligibility ($100K+ equity requirement)
  - Portfolio margin significantly reduces capital requirements for defined-risk spreads
  - If not immediately eligible, apply once account reaches threshold
- [ ] Review and document commission structure
  - Base: $0.65/contract for options
  - Confirm no ticket charges on equity trades
  - Note any volume discounts available
- [ ] Set up E-Trade Pro desktop platform
  - Configure watchlists matching core universe: AAPL, AMZN, AVGO, COST, GOOGL, MA, META, MSFT, NVDA, SPY, V
  - Set up options chain views with Greeks display (delta, theta, IV)
  - Configure alerts for target delta/DTE ranges
- [ ] Set up Power E-Trade (web/mobile)
  - Mirror watchlists from E-Trade Pro
  - Enable push notifications for price alerts and order fills

### Account Security

- [ ] Enable two-factor authentication (2FA)
- [ ] Set up security questions
- [ ] Configure login notifications
- [ ] Review and set IP allowlisting if available

---

## Phase 2: E-Trade API Setup

**Target:** Week 1 (Feb 17-21)

### Developer Registration

- [ ] Register for E-Trade Developer account at developer.etrade.com
- [ ] Apply for API access (consumer key + consumer secret)
  - Sandbox access is typically immediate
  - Production access may require additional approval (allow 3-5 business days)
- [ ] Document API credentials securely (use password manager, never in code/repos)

### API Authentication: OAuth 1.0a

E-Trade uses **OAuth 1.0a** (not OAuth 2.0). This is a common pain point — document carefully.

- [ ] Understand the OAuth 1.0a flow:
  1. Request token → `https://api.etrade.com/oauth/request_token`
  2. Authorize token → User redirected to E-Trade login page
  3. Exchange for access token → `https://api.etrade.com/oauth/access_token`
  - Access tokens expire at midnight ET daily — must re-authenticate each session
- [ ] Test OAuth flow manually using Postman or curl
  - Verify request token retrieval
  - Complete authorization redirect
  - Obtain access token
  - Make test API call (e.g., list accounts)
- [ ] Document the token refresh process (daily re-auth requirement)

### API Endpoints (Key)

| Endpoint | Purpose | Priority |
|----------|---------|----------|
| `/v1/accounts/list` | List accounts and balances | P0 |
| `/v1/accounts/{id}/balance` | Buying power, margin, cash | P0 |
| `/v1/accounts/{id}/portfolio` | Current positions and Greeks | P0 |
| `/v1/market/quote/{symbols}` | Real-time quotes | P1 |
| `/v1/market/optionchains` | Options chain data | P1 |
| `/v1/accounts/{id}/orders` | Order management | P1 |
| `/v1/accounts/{id}/orders/place` | Place orders (Phase 2+) | P2 |

### Rate Limits and Constraints

- [ ] Document rate limits:
  - 2 requests/second for market data
  - 4 requests/second for account data
  - Throttle n8n workflows accordingly
- [ ] Plan for daily token expiration in automation workflows
  - Option A: Manual re-auth each morning (simplest, Phase 1)
  - Option B: Semi-automated re-auth via n8n with Telegram notification (Phase 2)

### Sandbox Testing

- [ ] Configure sandbox endpoints:
  - Sandbox base: `https://apisb.etrade.com`
  - Production base: `https://api.etrade.com`
- [ ] Test all P0 endpoints in sandbox
- [ ] Verify response parsing for positions, balances, and orders
- [ ] Document any sandbox limitations (delayed data, missing endpoints)

### n8n Credential Setup

- [ ] Create custom OAuth 1.0a credential in n8n
  - n8n's built-in OAuth is typically 2.0 — E-Trade requires custom HTTP node with OAuth 1.0a signing
  - Option: Use n8n Code node with `oauth-1.0a` npm package for request signing
  - Alternative: Create a lightweight proxy service that handles OAuth 1.0a and exposes REST endpoints to n8n
- [ ] Test n8n → E-Trade API connection with account list endpoint
- [ ] Verify credential storage security in n8n cloud

---

## Phase 3: Data Feed Integration

**Target:** Week 2 (Feb 24-28)

### Data Source Mapping

| Source | Data Type | Current Status | Integration Target |
|--------|-----------|----------------|-------------------|
| FMP API | Fundamentals, earnings, ratios, SEC filings | Active | Continue as-is; feed into Earnings Alpha |
| Massive.com | OPRA options feed, greeks, IV, historical tick data | Active | Primary options data for OCA |
| E-Trade API | Account balances, positions, buying power | New | Connect to portfolio monitoring workflows |
| Google Sheets | Idea tracking, reporting outputs | Active | Continue as trade journal and reporting layer |
| Telegram | Notifications, approval workflows | Active | Continue as alerting and manual approval channel |

### Integration Tasks

- [ ] Map FMP API data flow → existing n8n workflows → OCA input
  - Verify ticker coverage matches core universe
  - Confirm earnings calendar data is current
- [ ] Map Massive.com OPRA feed → OCA options chain analysis
  - Verify Greeks accuracy against E-Trade chain data
  - Document any data latency between sources
- [ ] Create n8n workflow: E-Trade API → Portfolio positions snapshot
  - Trigger: Daily at market close (4:00 PM ET)
  - Output: Current positions, P&L, Greeks exposure to Google Sheets
- [ ] Create n8n workflow: E-Trade API → Buying power check
  - Trigger: On-demand (called by OCA before trade recommendations)
  - Output: Available buying power, margin used, cash balance
- [ ] Verify data consistency across sources
  - Cross-check: Massive.com IV vs. E-Trade IV for same contract
  - Cross-check: FMP earnings date vs. E-Trade earnings date

---

## Phase 4: Execution Workflow

**Target:** Week 2 (Feb 24-28)

### Signal → Analysis → Execution Pipeline

The execution pipeline has three phases. Start with Phase 1 (fully manual) and progress to Phase 3 only after live trading validation.

#### Phase 1: Manual Execution (Current Target)

```
OCA screens options → Structured recommendation →
Ricardo reviews in Google Sheets → Manual order entry in E-Trade Pro
```

- [ ] Configure OCA output to include:
  - Specific contract (underlying, strike, expiration)
  - Entry price range (credit for sells, debit for buys)
  - Position size (contracts) based on 5% max position rule
  - Defined exit: profit target (50% of max) and stop-loss (200% of credit)
  - Portfolio impact: new total delta, sector exposure, options allocation %
- [ ] Create trade execution checklist template (pre-trade):
  - [ ] Thesis documented?
  - [ ] Edge identified?
  - [ ] Max loss calculated?
  - [ ] Exit plan defined?
  - [ ] Portfolio fit verified (sector, correlation, total exposure)?
  - [ ] Buying power sufficient?
- [ ] Set up post-trade logging workflow:
  - Trade entered in Google Sheets journal
  - Telegram notification sent with trade summary
  - Position added to daily monitoring workflow

#### Phase 2: Semi-Automated (Q2 2026)

```
OCA screens → Recommendation with auto-filled order →
Telegram approval request → Ricardo approves → Order placed via API
```

- [ ] Build n8n workflow: OCA recommendation → E-Trade order preview
- [ ] Build Telegram approval bot: Show trade details, approve/reject buttons
- [ ] On approval: Place order via E-Trade API
- [ ] On rejection: Log reason, adjust OCA parameters if systematic

#### Phase 3: Automated (Q3-Q4 2026, Conditional)

```
OCA screens → Pre-trade risk check (automated) →
Order placed → Confirmation sent → Position monitored
```

- [ ] Only activate after 6+ months of validated Phase 2 performance
- [ ] Automated pre-trade risk checks must pass before any order
- [ ] Kill switch: Telegram command to halt all automated trading immediately
- [ ] Daily human review of all automated trades remains mandatory

---

## Phase 5: Risk Management Tooling

**Target:** Week 2 (Feb 24-28)

### Position Monitoring Workflow

- [x] Create n8n workflow: Risk Limit Monitor — `outputs/n8n-workflow-4-risk-limit-monitor.json`
  - ✅ Trigger: Every 30 minutes during market hours
  - ✅ Checks: 7 risk limits (position size, sector, options alloc, cash reserve, delta, theta, drawdown)
  - ✅ Alerts via Telegram with severity levels and recommended actions
  - [ ] **IMPORT INTO N8N** — replace credential IDs and activate
- [x] Create n8n workflow: Watchlist Alert System — `outputs/n8n-workflow-watchlist-alert-system.json`
  - ✅ Trigger: Every 15 minutes during market hours
  - ✅ 6 alert types: SMA cross, price move, volume spike, earnings proximity, 52-week levels, round numbers
  - [ ] **IMPORT INTO N8N** — replace credential IDs and activate

### Exposure Dashboard

- [x] Create Google Sheets dashboard — `outputs/paper-trading-workbook.gs`
  - ✅ Daily Dashboard sheet with: net delta, daily theta, CSP count, equity positions, cash %, VIX, SPY
  - ✅ Conditional formatting: red if cash <15%, yellow 15-20%, drawdown red if <-5%
  - ✅ Running peak and drawdown formulas built in
  - [ ] **PASTE APPS SCRIPT INTO GOOGLE SHEETS** and run `setupPaperTradingWorkbook()`
- [x] Connect dashboard to E-Trade API via n8n — `outputs/n8n-workflow-1-daily-portfolio-snapshot.json`
  - ✅ Daily refresh at 4:15 PM ET
  - [ ] **IMPORT INTO N8N** — requires E-Trade OAuth credential

### Pre-Trade Risk Checks

- [x] Build pre-trade validation checklist (automated in n8n) — `outputs/n8n-workflow-2-trade-entry-logger.json`
  - ✅ 5 automated checks: position ≤5%, sector ≤25%, cash ≥15%, options ≤30%, max loss ≤5%
  - ✅ Blocks trade logging if any check fails, sends Telegram risk alert instead
  - [ ] **IMPORT INTO N8N** — replace credential IDs and activate
- [x] `/paper-trade` Claude command provides manual pre-trade checklist — `.claude/commands/paper-trade.md`

### Trade Journal

- [x] Set up Google Sheets trade journal — `outputs/paper-trading-workbook.gs`
  - ✅ Trade Log sheet with 26 columns (A-Z): Trade ID through Lessons
  - ✅ Formulas: Raw P&L, Commission, Slippage, Adjusted P&L, P&L %, Days Held
  - ✅ Dropdowns: Strategy, Direction, Exit Reason, Rule Compliance
  - ✅ Conditional formatting: green/red P&L, yellow on compliance violations
  - [ ] **PASTE APPS SCRIPT INTO GOOGLE SHEETS** and run `setupPaperTradingWorkbook()`
- [x] Create n8n workflow to auto-populate on trade entry — `outputs/n8n-workflow-2-trade-entry-logger.json`
  - ✅ Webhook trigger, auto-generates Trade ID, calculates DTE and max loss
  - [ ] **IMPORT INTO N8N** — replace credential IDs and activate
- [x] Weekly review template — included in Paper Trading Plan Section 6 + Weekly Summary sheet in workbook

---

## Phase 6: Connecting Existing Tools

**Target:** Week 2 (Feb 24-28)

### OCA → E-Trade Integration

- [ ] Feed E-Trade buying power into OCA position sizing
  - OCA currently recommends trades without knowing available capital
  - Add buying power constraint: never recommend a trade that would breach cash reserve minimum
- [ ] Cross-reference OCA recommendations with existing positions
  - Prevent doubling up: if already short AAPL puts, flag before recommending more
  - Check correlation: if recommending GOOGL puts while already short META puts, flag tech concentration

### Market Commenter → Portfolio Awareness

- [ ] Feed current positions into Market Commenter context
  - Market Commenter should note when market events directly affect open positions
  - Example: "Tech selling off -2%. You have 3 short put positions in tech sector — monitor."
- [ ] Add regime-change alerts
  - If Market Commenter detects shift from low-vol to high-vol regime, trigger position review

### Earnings Alpha → Position Alerts

- [ ] Cross-reference Earnings Alpha calendar with open positions
  - Alert 5 days before earnings on any underlying with an open position
  - Include: Expected move, IV rank, recommended action (hold/close/adjust)
- [ ] Feed earnings signals into OCA for pre-earnings trade recommendations

### Fiscal Platform → Sector Overlay

- [ ] Connect Fiscal Platform sector analysis to portfolio sector exposure
  - Flag if portfolio is concentrated in sectors facing policy headwinds
  - Surface opportunities in sectors benefiting from policy tailwinds

---

## Phase 7: Paper Trading Protocol

**Target:** Begin Mar 1, minimum 4-week duration
**Detailed plan:** `outputs/paper-trading-plan.md` (comprehensive 38-action-item plan)

### Setup

- [x] Paper trading plan documented — `outputs/paper-trading-plan.md`
  - ✅ Phased rollout: CSP-only (Week 1) → add momentum (Week 2) → full multi-strategy (Weeks 3-4)
  - ✅ 15 go-live criteria defined (10 quantitative, 5 qualitative)
  - ✅ Platform comparison: E-Trade primary, ThinkorSwim backup
  - ✅ Fill assumption adjustments (slippage, commissions)
- [x] Google Sheets tracking workbook — `outputs/paper-trading-workbook.gs`
  - ✅ Trade Log, Daily Dashboard, Weekly Summary, Risk Limits sheets
  - ✅ All formulas (Sharpe, drawdown, adjusted P&L) pre-built
- [x] Risk management framework — `outputs/risk-management-framework.md`
  - ✅ Position sizing formulas, drawdown tiers, circuit breakers, stress tests
- [ ] **ACTIVATE E-TRADE PAPER TRADING** — configure $100K starting capital
- [ ] **CREATE GOOGLE SHEET** — paste Apps Script, run setup
- [ ] **IMPORT ALL N8N WORKFLOWS** — 6 workflows ready

### Weekly Review Protocol

- [x] Weekly review template defined — Paper Trading Plan Section 6
  - ✅ 8-section template: Performance, Trades, Thesis Accuracy, Compliance, Strategy Notes, Market Regime, Parameter Adjustments, Next Week Plan
  - ✅ Behavioral scoring (7-point scale)
- [x] n8n workflow auto-calculates weekly metrics — `outputs/n8n-workflow-3-weekly-metrics-calculator.json`
  - ✅ Rolling Sharpe, win rate, drawdown, go-live scorecard
  - [ ] **IMPORT INTO N8N** — replace credential IDs and activate

### Go-Live Criteria — expanded to 15 criteria in `outputs/paper-trading-plan.md`

| Criterion | Target | Measurement |
|-----------|--------|-------------|
| Duration | Minimum 4 weeks | Calendar weeks of paper trading |
| CSP trades closed | ≥20 | Trade log count |
| Momentum rebalances | ≥4 | Rebalance log count |
| Win rate (all) | >60% | Winning / total closed trades |
| CSP win rate | >65% | CSP winners / CSP total |
| Sharpe ratio | >1.0 | Annualized from weekly returns |
| Max drawdown | >-10% | Peak-to-trough during paper period |
| No weekly loss >-3% | 0 violations | Weekly P&L tracking |
| Adjusted P&L positive | >$0 | After commissions + slippage |
| Automation uptime | >95% | n8n workflow success rate |
| Rule compliance | 100% | Zero violations |
| Daily tracking | Zero missed days | Consecutive daily entries |
| Weekly reviews complete | 4+ | Completed templates |
| Pre-trade checklists | 100% | Every trade validated |
| Emotional readiness | Self-assessed | No revenge trading, FOMO, or rule-breaking |

### Transition to Live

- [ ] Start at 50% of target position sizes (Apr 1 target)
- [ ] Run paper + live in parallel for first 30 days
- [ ] Scale to 75% at Week 5, 100% at Week 7 if criteria hold
- [ ] Maintain trade journal discipline throughout

---

## Timeline Summary

| Week | Focus | Key Milestones |
|------|-------|----------------|
| **Week 1 (Feb 17-21)** | Account + API | Options Level 3 applied, API keys obtained, OAuth tested, sandbox verified |
| **Week 2 (Feb 24-28)** | Integration + Risk | Data feeds connected, risk dashboard built, paper trading begins |
| **Weeks 3-6 (Mar 1-28)** | Paper Trading | 4-week paper trading protocol, weekly reviews, parameter refinement |
| **Week 7+ (Mar 31+)** | Go-Live Decision | Evaluate go-live criteria, transition plan if criteria met |

---

## Reference: E-Trade API Quick Reference

### Base URLs

| Environment | Base URL |
|-------------|----------|
| Sandbox | `https://apisb.etrade.com` |
| Production | `https://api.etrade.com` |

### OAuth 1.0a Headers (Required on All Requests)

```
oauth_consumer_key
oauth_timestamp
oauth_nonce
oauth_signature_method (HMAC-SHA1)
oauth_signature
oauth_token (after authorization)
```

### Common Response Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Process response |
| 401 | Unauthorized | Token expired — re-authenticate |
| 403 | Forbidden | Check permissions/account access |
| 429 | Rate limited | Back off; check rate limit headers |
| 500 | Server error | Retry with exponential backoff |

---

*This checklist is a living document. Update status as items are completed. Items may be added as integration reveals new requirements.*
