# E-Trade API Setup & Paper Trading — Action Guide

**Version:** 1.0
**Date:** 2026-02-18
**For:** Ricardo Landino, Altamira Capital
**Status:** Ready for Execution
**Estimated Total Time:** ~3 hours (excluding approval wait times)
**Companion Documents:** Trading Infrastructure Setup v1.0, Paper Trading Launch Plan v1.0

---

## Timeline Checklist

| Date | Tasks | Status |
|------|-------|--------|
| **Feb 19** | 1. E-Trade Account Configuration + 2. Developer Portal & API Keys | [ ] |
| **Feb 20** | 3. OAuth 1.0a Testing with Postman/curl | [ ] |
| **Feb 21** | 4. Test API Endpoints + 5. Paper Trading Activation | [ ] |
| **Feb 25** | 6. n8n Credential Setup | [ ] |

---

## 1. E-Trade Account Configuration (~30 min)

### 1.1 Apply for Options Level 3

You need Level 3 for spreads and multi-leg strategies (bull put spreads, jade lizards, iron condors). Level 2 only covers long calls/puts.

**Where to find it:**

1. Log in to Power E-Trade: https://us.etrade.com/etx/pxy/login
2. Click your account name (top right) > **Account Settings**
3. Under **Trading Features**, click **Options Trading**
4. If your current level is below Level 3, click **Upgrade** or **Apply for Options Trading**

**Suitability Questionnaire — what to answer for Level 3 approval:**

The questionnaire determines risk tolerance and experience. Answer honestly, but be aware that these factors drive approval:

| Question Area | Recommended Response | Why |
|---------------|---------------------|-----|
| Investment objective | "Growth" or "Speculation" | "Income" alone may cap you at Level 1 |
| Trading experience (years) | 3+ years options experience | Critical — less than 2 years often limits to Level 2 |
| Number of options trades/year | 25+ | Shows active engagement |
| Annual income | $100K+ | Higher income = higher tolerance assumed |
| Net worth (liquid) | $200K+ | Demonstrates ability to absorb losses |
| Risk tolerance | "Moderate" or "Aggressive" | "Conservative" will block Level 3 |
| Knowledge level | "Good" or "Extensive" | Must show understanding of spreads, multi-leg |

**Expected approval timeline:**
- If suitability is strong: **Instant to 24 hours** (often approved immediately online)
- If borderline: **1-3 business days** (may require phone follow-up)
- If denied: Call E-Trade options desk at **1-800-387-2331** and explain your strategy. Denials can often be reversed with a conversation.

**Pitfall:** If you currently have no options approval, you may be auto-approved for Level 1 or 2 only. Check the confirmation page carefully — it will state the approved level. If it says Level 2, you need to request an upgrade to Level 3 separately.

### 1.2 Enable Margin Trading

1. Same path: **Account Settings** > **Trading Features** > **Margin Trading**
2. If not already enabled, click **Apply for Margin**
3. Margin requires a minimum $2,000 equity balance
4. Approval is typically instant if the account meets the minimum
5. Portfolio margin ($100K+ equity) is a separate application — defer this until the account reaches threshold

### 1.3 Review Commission Structure

Verify these rates in **Account Settings** > **Commissions & Fees**:

| Trade Type | Commission | Notes |
|------------|-----------|-------|
| Equity trades | $0.00 | No ticket charges |
| Options (per contract) | $0.65 | Both opening and closing |
| Multi-leg options | $0.65/leg | Each leg charged separately |
| Assignment/exercise | $0.00 | No charge |

**Budget impact for paper trading:** At 20+ CSP trades (round-trip), expect ~$26+ in simulated commissions. Track this in the adjusted P&L formula.

### 1.4 Set Up Watchlists

**In Power E-Trade:**

1. Click **Watchlists** in the top navigation
2. Click **+ Create Watchlist** > Name it "Altamira Core"
3. Add all 11 symbols: `AAPL, MSFT, GOOGL, AMZN, AVGO, COST, V, MA, META, NVDA, SPY`
4. Add columns: **Last, Change %, Volume, IV Rank, 50-Day MA, Delta** (customize via the gear icon)
5. Save

**In E-Trade Pro (desktop), if using:**

1. Open E-Trade Pro > **Watchlist** tab
2. Create "Altamira Core" with the same 11 symbols
3. Right-click column headers to add Greeks columns

---

## 2. E-Trade Developer Portal & API Keys (~20 min)

### 2.1 Register for Developer Access

1. Go to: **https://developer.etrade.com**
2. Click **Get Started** or **Sign Up**
3. Log in with your regular E-Trade credentials
4. Complete the developer registration form:
   - **App Name:** "Altamira Trading System" (or similar; this is just a label)
   - **App Description:** "Portfolio monitoring and options analysis"
   - **Callback URL:** `oob` (out-of-band — you will manually copy the verifier code)
   - **App Type:** Select "Individual"

### 2.2 Get Sandbox Keys (Immediate)

After registration:

1. Navigate to **My Apps** or **API Keys** section
2. Your **Sandbox** credentials will be available immediately:
   - `SANDBOX_CONSUMER_KEY` (also called API Key)
   - `SANDBOX_CONSUMER_SECRET` (also called API Secret)
3. Copy both values now

**Where they appear:** On the developer dashboard under your app listing. There will be two sets — "Sandbox" and "Production." Sandbox is active immediately.

### 2.3 Request Production Keys

1. On the same page, click **Request Production Access** (or similar button)
2. Fill out the production application:
   - Describe your use case: "Automated portfolio monitoring, balance checking, and options chain analysis for personal trading account"
   - Expected API call volume: "Low — under 1,000 calls/day"
3. Submit

**Expected timeline:** 3-5 business days for production key approval. You will receive an email at your E-Trade registered email.

**Pitfall:** Production keys are not the same as sandbox keys. Do not use sandbox keys against `api.etrade.com` or vice versa. They are completely separate credential sets.

### 2.4 Store Credentials Securely

**Never store API keys in code repositories, plain text files, or documents synced to the cloud.**

Recommended storage:

| Method | How |
|--------|-----|
| **Password manager** (best) | Create entries: "E-Trade API Sandbox" and "E-Trade API Production" with consumer key + secret |
| **Environment variables** (for scripts) | Set `ETRADE_SANDBOX_KEY`, `ETRADE_SANDBOX_SECRET` in your shell profile (`.bashrc` or `.zshrc`) |
| **n8n credentials** (for workflows) | Store inside n8n's built-in credential manager (encrypted at rest) |

For environment variables, add to your shell profile:
```bash
export ETRADE_SANDBOX_KEY="your_sandbox_consumer_key"
export ETRADE_SANDBOX_SECRET="your_sandbox_consumer_secret"
export ETRADE_PROD_KEY="your_production_consumer_key"
export ETRADE_PROD_SECRET="your_production_consumer_secret"
```

---

## 3. OAuth 1.0a Testing with Postman/curl (~45 min)

E-Trade uses **OAuth 1.0a** (not 2.0). This is the most common stumbling block. Follow this flow exactly.

### 3.1 OAuth 1.0a Flow Overview

```
Step 1: Get Request Token     → You receive oauth_token + oauth_token_secret
Step 2: Authorize (browser)   → User logs in, gets a verifier code
Step 3: Get Access Token      → Exchange request token + verifier for access token
Step 4: Make API calls        → Use access token on all subsequent requests
```

**Critical:** Access tokens expire at **midnight Eastern Time every day.** You must re-authenticate each trading day.

### 3.2 Step 1 — Get Request Token

**Sandbox base URL:** `https://apisb.etrade.com`
**Production base URL:** `https://api.etrade.com`

All examples below use sandbox. Replace `apisb` with `api` for production once you have production keys.

**curl command:**

```bash
curl -X POST "https://apisb.etrade.com/oauth/request_token" \
  --header "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "oauth_consumer_key=YOUR_SANDBOX_KEY" \
  --data-urlencode "oauth_signature_method=HMAC-SHA1" \
  --data-urlencode "oauth_timestamp=$(date +%s)" \
  --data-urlencode "oauth_nonce=$(openssl rand -hex 16)" \
  --data-urlencode "oauth_callback=oob" \
  --data-urlencode "oauth_version=1.0" \
  --data-urlencode "oauth_signature=COMPUTED_SIGNATURE"
```

**The problem with raw curl:** OAuth 1.0a requires computing an HMAC-SHA1 signature over a specific base string. Doing this manually is error-prone. **Use a tool that handles signing for you.**

**Recommended: Use a Python script instead of raw curl.** This handles all the signing automatically:

```python
#!/usr/bin/env python3
"""E-Trade OAuth 1.0a — Request Token"""

import requests
from requests_oauthlib import OAuth1

# Replace with your actual credentials
CONSUMER_KEY = "YOUR_SANDBOX_KEY"
CONSUMER_SECRET = "YOUR_SANDBOX_SECRET"

# Sandbox URLs
REQUEST_TOKEN_URL = "https://apisb.etrade.com/oauth/request_token"
AUTHORIZE_URL = "https://us.etrade.com/e/t/etws/authorize"
ACCESS_TOKEN_URL = "https://apisb.etrade.com/oauth/access_token"

# Step 1: Get request token
oauth = OAuth1(CONSUMER_KEY, client_secret=CONSUMER_SECRET, callback_uri="oob")
response = requests.post(REQUEST_TOKEN_URL, auth=oauth)

print(f"Status: {response.status_code}")
print(f"Response: {response.text}")

# Parse the response
from urllib.parse import parse_qs
tokens = parse_qs(response.text)
request_token = tokens["oauth_token"][0]
request_token_secret = tokens["oauth_token_secret"][0]

print(f"\nRequest Token: {request_token}")
print(f"Request Token Secret: {request_token_secret}")
print(f"\nStep 2: Open this URL in your browser:")
print(f"{AUTHORIZE_URL}?key={CONSUMER_KEY}&token={request_token}")
```

**Install dependencies first:**
```bash
pip install requests requests-oauthlib
```

**Expected response (Step 1):**
```
Status: 200
Response: oauth_token=REQUEST_TOKEN_VALUE&oauth_token_secret=REQUEST_TOKEN_SECRET_VALUE
```

### 3.3 Step 2 — Authorize in Browser

1. Open the URL printed by the script in your browser
2. Log in with your E-Trade credentials
3. Accept the authorization prompt
4. E-Trade displays a **verifier code** (5-6 character alphanumeric string)
5. Copy this verifier code — you need it for Step 3

**URL format:**
```
https://us.etrade.com/e/t/etws/authorize?key=YOUR_SANDBOX_KEY&token=REQUEST_TOKEN_VALUE
```

**Pitfall:** The authorize URL goes to `us.etrade.com` (the main site), not `apisb.etrade.com`. This is correct — authorization always happens on the main site regardless of sandbox vs. production.

### 3.4 Step 3 — Get Access Token

```python
# Step 3: Exchange for access token (continue from script above)
verifier = input("Enter the verifier code from the browser: ")

oauth = OAuth1(
    CONSUMER_KEY,
    client_secret=CONSUMER_SECRET,
    resource_owner_key=request_token,
    resource_owner_secret=request_token_secret,
    verifier=verifier
)

response = requests.post(ACCESS_TOKEN_URL, auth=oauth)

print(f"Status: {response.status_code}")
print(f"Response: {response.text}")

tokens = parse_qs(response.text)
access_token = tokens["oauth_token"][0]
access_token_secret = tokens["oauth_token_secret"][0]

print(f"\nAccess Token: {access_token}")
print(f"Access Token Secret: {access_token_secret}")
print("\nSave these! They're valid until midnight ET.")
```

**Expected response:**
```
Status: 200
Response: oauth_token=ACCESS_TOKEN_VALUE&oauth_token_secret=ACCESS_TOKEN_SECRET_VALUE
```

### 3.5 Step 4 — Test an API Call

```python
# Step 4: Make a test API call
oauth = OAuth1(
    CONSUMER_KEY,
    client_secret=CONSUMER_SECRET,
    resource_owner_key=access_token,
    resource_owner_secret=access_token_secret
)

response = requests.get("https://apisb.etrade.com/v1/accounts/list.json", auth=oauth)
print(f"Status: {response.status_code}")
print(f"Accounts: {response.json()}")
```

### 3.6 Complete Script (All-in-One)

Save this as `etrade_auth.py` for daily use:

```python
#!/usr/bin/env python3
"""
E-Trade OAuth 1.0a — Complete Auth Flow
Run daily before market open to get fresh access tokens.
Tokens expire at midnight ET.
"""

import json
import webbrowser
from urllib.parse import parse_qs

import requests
from requests_oauthlib import OAuth1

# ── Configuration ───────────────────────────────────────────
# Replace with your actual credentials, or set as env vars
import os

CONSUMER_KEY = os.environ.get("ETRADE_SANDBOX_KEY", "YOUR_SANDBOX_KEY")
CONSUMER_SECRET = os.environ.get("ETRADE_SANDBOX_SECRET", "YOUR_SANDBOX_SECRET")

# Toggle sandbox vs production
USE_SANDBOX = True

if USE_SANDBOX:
    BASE_URL = "https://apisb.etrade.com"
else:
    BASE_URL = "https://api.etrade.com"

REQUEST_TOKEN_URL = f"{BASE_URL}/oauth/request_token"
ACCESS_TOKEN_URL = f"{BASE_URL}/oauth/access_token"
AUTHORIZE_URL = "https://us.etrade.com/e/t/etws/authorize"

# ── Step 1: Request Token ──────────────────────────────────
print("Step 1: Requesting token...")
oauth = OAuth1(CONSUMER_KEY, client_secret=CONSUMER_SECRET, callback_uri="oob")
response = requests.post(REQUEST_TOKEN_URL, auth=oauth)

if response.status_code != 200:
    print(f"FAILED: {response.status_code} — {response.text}")
    print("Check: Are your consumer key/secret correct? Is the base URL right?")
    exit(1)

tokens = parse_qs(response.text)
request_token = tokens["oauth_token"][0]
request_token_secret = tokens["oauth_token_secret"][0]
print(f"  Request token obtained.")

# ── Step 2: Authorize ──────────────────────────────────────
auth_url = f"{AUTHORIZE_URL}?key={CONSUMER_KEY}&token={request_token}"
print(f"\nStep 2: Opening browser for authorization...")
print(f"  URL: {auth_url}")
webbrowser.open(auth_url)

verifier = input("\nEnter the verifier code from the browser: ").strip()

# ── Step 3: Access Token ──────────────────────────────────
print("\nStep 3: Exchanging for access token...")
oauth = OAuth1(
    CONSUMER_KEY,
    client_secret=CONSUMER_SECRET,
    resource_owner_key=request_token,
    resource_owner_secret=request_token_secret,
    verifier=verifier,
)
response = requests.post(ACCESS_TOKEN_URL, auth=oauth)

if response.status_code != 200:
    print(f"FAILED: {response.status_code} — {response.text}")
    print("Check: Did you enter the verifier correctly? Is the request token still valid?")
    exit(1)

tokens = parse_qs(response.text)
access_token = tokens["oauth_token"][0]
access_token_secret = tokens["oauth_token_secret"][0]

print(f"  Access token obtained. Valid until midnight ET.")

# ── Step 4: Test Call ──────────────────────────────────────
print("\nStep 4: Testing API — listing accounts...")
oauth = OAuth1(
    CONSUMER_KEY,
    client_secret=CONSUMER_SECRET,
    resource_owner_key=access_token,
    resource_owner_secret=access_token_secret,
)
response = requests.get(f"{BASE_URL}/v1/accounts/list.json", auth=oauth)

if response.status_code == 200:
    data = response.json()
    print(f"  SUCCESS. Accounts found:")
    accounts = data.get("AccountListResponse", {}).get("Accounts", {}).get("Account", [])
    for acct in accounts:
        print(f"    - {acct.get('accountId')} ({acct.get('accountDesc', 'N/A')})")

    # Save tokens for use in other scripts/n8n
    creds = {
        "consumer_key": CONSUMER_KEY,
        "consumer_secret": CONSUMER_SECRET,
        "access_token": access_token,
        "access_token_secret": access_token_secret,
        "base_url": BASE_URL,
    }
    with open("etrade_tokens.json", "w") as f:
        json.dump(creds, f, indent=2)
    print(f"\n  Tokens saved to etrade_tokens.json")
    print(f"  WARNING: Delete this file at end of day. Tokens expire at midnight ET.")
else:
    print(f"  FAILED: {response.status_code} — {response.text}")
```

### 3.7 Postman Setup (Alternative)

If you prefer Postman over Python:

1. **Import a new collection** > Name it "E-Trade API"
2. **Set collection-level auth:**
   - Type: **OAuth 1.0**
   - Consumer Key: your sandbox key
   - Consumer Secret: your sandbox secret
   - Signature Method: **HMAC-SHA1**
   - Disable "Add params to header" (use query string for request token)
3. **Create request: Get Request Token**
   - Method: POST
   - URL: `https://apisb.etrade.com/oauth/request_token`
   - Auth: Inherit from collection
   - Add param: `oauth_callback=oob`
4. **Send** — copy the `oauth_token` from the response
5. **Open browser:** `https://us.etrade.com/e/t/etws/authorize?key=YOUR_KEY&token=OAUTH_TOKEN`
6. **Copy verifier code**
7. **Create request: Get Access Token**
   - Method: POST
   - URL: `https://apisb.etrade.com/oauth/access_token`
   - Auth: Inherit from collection, but add:
     - Token: the `oauth_token` from step 4
     - Token Secret: the `oauth_token_secret` from step 4
     - Verifier: the code from step 6
8. **Send** — you now have your access token
9. **Update collection auth** with the access token and secret for subsequent requests

### 3.8 Common Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| **401 Unauthorized** | Token expired (midnight ET reset) | Re-run the full auth flow. Tokens cannot be refreshed — you must re-authenticate. |
| **401 Unauthorized** (on request token) | Wrong consumer key/secret | Double-check credentials. Sandbox keys only work with `apisb.etrade.com`. |
| **Signature mismatch / Invalid signature** | Timestamp drift, bad nonce, encoding issue | Ensure system clock is accurate (within 5 min of server time). Use a fresh nonce per request. URL-encode all parameters. |
| **SSL/TLS errors** | Outdated SSL library or certificate issue | Update Python/curl. Ensure you are using `https://` (not `http://`). |
| **oauth_problem=token_rejected** | Using an expired or revoked request token | Request tokens are single-use and expire quickly (~5 min). Start over from Step 1. |
| **403 Forbidden** | Account not authorized for API access | Verify your developer app is approved. Check that you accepted the API agreement. |
| **Empty response body** | Missing `.json` extension on endpoint URL | Append `.json` to the endpoint (e.g., `/v1/accounts/list.json`). Without it, E-Trade may return XML. |

---

## 4. Test API Endpoints (~30 min)

With your access token from Task 3, test each key endpoint. Use either the Python script approach or Postman.

### 4.1 List Accounts

```python
# Using the oauth object from the auth script
response = requests.get(f"{BASE_URL}/v1/accounts/list.json", auth=oauth)
print(json.dumps(response.json(), indent=2))
```

**Expected response shape:**
```json
{
  "AccountListResponse": {
    "Accounts": {
      "Account": [
        {
          "accountId": "12345678",
          "accountIdKey": "ENCODED_KEY",
          "accountMode": "MARGIN",
          "accountDesc": "Individual Brokerage",
          "accountName": "Ricardo Landino",
          "accountType": "INDIVIDUAL",
          "institutionType": "BROKERAGE",
          "accountStatus": "ACTIVE"
        }
      ]
    }
  }
}
```

**Save the `accountIdKey`** — you need it for all subsequent account-specific calls. This is NOT the same as the plain `accountId`.

### 4.2 Account Balance

```python
ACCOUNT_ID_KEY = "ENCODED_KEY_FROM_ABOVE"

response = requests.get(
    f"{BASE_URL}/v1/accounts/{ACCOUNT_ID_KEY}/balance.json",
    params={"instType": "BROKERAGE", "realTimeNAV": "true"},
    auth=oauth
)
print(json.dumps(response.json(), indent=2))
```

**Expected response shape:**
```json
{
  "BalanceResponse": {
    "accountId": "12345678",
    "accountType": "MARGIN",
    "Computed": {
      "cashAvailableForInvestment": 100000.00,
      "cashBuyingPower": 200000.00,
      "marginBuyingPower": 200000.00,
      "netCash": 100000.00,
      "RealTimeValues": {
        "totalAccountValue": 100000.00,
        "netMv": 0.00,
        "totalLongValue": 0.00
      }
    }
  }
}
```

**Key fields to capture:** `cashAvailableForInvestment` (buying power for CSPs), `totalAccountValue` (portfolio value).

**Pitfall:** The `instType=BROKERAGE` parameter is required. Without it, you get a 400 error.

### 4.3 Portfolio Positions

```python
response = requests.get(
    f"{BASE_URL}/v1/accounts/{ACCOUNT_ID_KEY}/portfolio.json",
    auth=oauth
)
print(json.dumps(response.json(), indent=2))
```

**Expected response shape (with positions):**
```json
{
  "PortfolioResponse": {
    "AccountPortfolio": [
      {
        "Position": [
          {
            "symbolDescription": "AAPL",
            "quantity": 100,
            "positionType": "LONG",
            "pricePaid": 185.50,
            "marketValue": 18750.00,
            "totalGain": 200.00,
            "totalGainPct": 1.08
          }
        ]
      }
    ]
  }
}
```

**Note:** If the account has no positions (new paper account), the response may return an empty portfolio or a 204 No Content. This is normal.

### 4.4 Market Quote

```python
response = requests.get(
    f"{BASE_URL}/v1/market/quote/AAPL.json",
    auth=oauth
)
print(json.dumps(response.json(), indent=2))
```

**Expected response shape:**
```json
{
  "QuoteResponse": {
    "QuoteData": [
      {
        "Product": {
          "symbol": "AAPL",
          "securityType": "EQ"
        },
        "All": {
          "lastTrade": 236.87,
          "bid": 236.85,
          "ask": 236.89,
          "bidSize": 200,
          "askSize": 300,
          "volume": 45678901,
          "high": 238.50,
          "low": 235.20,
          "open": 236.00,
          "previousClose": 235.46,
          "changeClose": 1.41,
          "changePct": 0.60,
          "high52": 260.10,
          "low52": 164.08
        }
      }
    ]
  }
}
```

**Tip:** You can request multiple symbols: `/v1/market/quote/AAPL,MSFT,GOOGL.json`

### 4.5 Options Chain

```python
response = requests.get(
    f"{BASE_URL}/v1/market/optionchains.json",
    params={
        "symbol": "AAPL",
        "expiryYear": "2026",
        "expiryMonth": "3",
        "expiryDay": "20",
        "strikePriceNear": "235",
        "noOfStrikes": "10",
        "optionCategory": "STANDARD",
        "chainType": "PUT",
        "priceType": "ATNM"
    },
    auth=oauth
)
print(json.dumps(response.json(), indent=2))
```

**Expected response shape:**
```json
{
  "OptionChainResponse": {
    "OptionPair": [
      {
        "Put": {
          "symbol": "AAPL:2026:3:20:P:230",
          "strikePrice": 230.00,
          "bid": 2.15,
          "ask": 2.25,
          "lastPrice": 2.20,
          "volume": 1250,
          "openInterest": 8500,
          "OptionGreeks": {
            "delta": -0.22,
            "gamma": 0.015,
            "theta": -0.08,
            "vega": 0.35,
            "iv": 0.28
          }
        }
      }
    ]
  }
}
```

**Key parameters for your strategies:**

| Parameter | Purpose | CSP Typical Values |
|-----------|---------|-------------------|
| `chainType` | PUT or CALL or CALLPUT | PUT (for CSPs) |
| `strikePriceNear` | Center the chain around this price | Current stock price |
| `noOfStrikes` | How many strikes to return | 10-20 |
| `expiryYear/Month/Day` | Specific expiration | 30-45 DTE target |
| `optionCategory` | STANDARD or WEEKLY | STANDARD (monthlies are more liquid) |

### 4.6 Sandbox Limitations

Document these during testing:

| Limitation | Impact | Workaround |
|-----------|--------|------------|
| Data may be static/delayed | Quotes might not match real market | Use for flow testing, not data validation |
| Limited order types | Some complex orders may not work in sandbox | Test in paper trading mode instead |
| Account data is synthetic | Balances and positions are simulated | Expected — this is for testing the API flow |
| Options chains may be incomplete | Not all expirations/strikes may be available | Production will have full data |
| Rate limits same as production | 2 req/sec market, 4 req/sec account | Build throttling into workflows from the start |

---

## 5. Power E-Trade Paper Trading Activation (~15 min)

### 5.1 Enable Paper Trading

1. Log in to Power E-Trade: https://us.etrade.com/etx/pxy/login
2. Click on **Trading** in the main navigation
3. Look for **Paper Trading** toggle or link — in Power E-Trade, this is typically:
   - Click the **account selector** dropdown (top of trading page)
   - Select **Paper Trading Account** (or "Virtual Account")
   - If you don't see this option, check: **Menu** > **Trading** > **Paper Trading**
4. If paper trading is not immediately available, call E-Trade at **1-800-387-2331** and request paper trading activation. It is a free feature but may need to be enabled by support.

**Alternative path:** Some users access paper trading through:
- Power E-Trade > **Markets** tab > **Paper Trading** section
- Or via the URL: `https://us.etrade.com/etx/pxy/paper-trading`

### 5.2 Configure Starting Capital

1. Once in paper trading mode, look for **Settings** or **Reset Account**
2. Set starting balance to **$100,000** (matches your planned real capital)
3. Confirm margin is enabled in the paper account settings

**Pitfall:** Paper trading accounts sometimes default to $1M in capital. Make sure you set it to $100K to get realistic position sizing feedback.

### 5.3 Set Up Options Chain Views with Greeks

1. In Power E-Trade, navigate to **Trading** > **Options**
2. Enter a symbol (e.g., AAPL) to load the options chain
3. Click the **gear/settings icon** on the options chain display
4. Enable these columns:
   - **Delta** (critical for your 0.20-0.25 target)
   - **Theta** (daily time decay)
   - **IV** (implied volatility for each strike)
   - **Volume** (liquidity filter)
   - **Open Interest** (liquidity filter)
   - **Bid/Ask** (spread check)
5. Set default chain view to **Puts only** (for CSP scanning)
6. Set default expiration filter to **30-45 DTE**
7. Save as default view

### 5.4 Place a Test Paper Trade

Verify the full pipeline by placing one test CSP:

1. **Select:** AAPL or SPY
2. **Find:** A put with delta ~0.20, 30-45 DTE
3. **Action:** Sell to Open, 1 contract
4. **Order type:** Limit order at the bid (or mid-price)
5. **Duration:** Day order
6. **Review** the order preview — check that:
   - Maximum risk is displayed correctly
   - Cash secured amount matches (strike price x 100)
   - Commission shows $0.65
7. **Submit** the paper trade
8. **Verify:**
   - Order appears in Order Status
   - When filled, position appears in Portfolio
   - P&L tracking is active

**Success criteria:** You see the open short put in your paper portfolio with Greeks (delta, theta) displayed.

---

## 6. n8n Credential Setup (~30 min)

n8n does not natively support OAuth 1.0a. You have two options:

### Option A: n8n Code Node with Manual OAuth Signing (Recommended)

This is simpler and keeps everything inside n8n. Use a Code node to handle OAuth 1.0a signing, then make HTTP requests.

**Step 1: Store credentials in n8n**

1. In n8n, go to **Credentials** > **Create New**
2. Choose **Generic Credential Type** or **Header Auth** (we will not actually use this for auth — it is just for secure storage)
3. Create a credential named "E-Trade API" with these fields stored as header values:
   - `consumer_key`: your sandbox consumer key
   - `consumer_secret`: your sandbox consumer secret
   - `access_token`: your current access token (update daily)
   - `access_token_secret`: your current access token secret (update daily)

**Note on daily tokens:** Since E-Trade tokens expire at midnight ET, you will need to update the access token and secret daily. Options:
- **Manual update:** Run the Python auth script each morning, paste new tokens into n8n credentials
- **Semi-automated:** Build an n8n workflow that triggers you via Telegram to complete the browser auth step, then stores the resulting tokens

**Step 2: Code node for OAuth 1.0a signing**

Create a new workflow with this Code node as the first step:

```javascript
// n8n Code Node: E-Trade OAuth 1.0a Signed Request
// This node signs requests using OAuth 1.0a HMAC-SHA1

const crypto = require('crypto');

// ── Configuration ──────────────────────────────────────────
// Pull from n8n credentials or hardcode for testing
const config = {
  consumerKey: 'YOUR_SANDBOX_KEY',
  consumerSecret: 'YOUR_SANDBOX_SECRET',
  accessToken: 'YOUR_ACCESS_TOKEN',       // Update daily
  accessTokenSecret: 'YOUR_ACCESS_TOKEN_SECRET', // Update daily
  baseUrl: 'https://apisb.etrade.com',
};

// ── Request Details ────────────────────────────────────────
// Change these per endpoint
const method = 'GET';
const endpoint = '/v1/accounts/list.json';
const queryParams = {}; // Add query params as needed

// ── OAuth 1.0a Signature Generation ───────────────────────
function percentEncode(str) {
  return encodeURIComponent(str)
    .replace(/!/g, '%21')
    .replace(/\*/g, '%2A')
    .replace(/'/g, '%27')
    .replace(/\(/g, '%28')
    .replace(/\)/g, '%29');
}

function generateNonce() {
  return crypto.randomBytes(16).toString('hex');
}

function generateTimestamp() {
  return Math.floor(Date.now() / 1000).toString();
}

function generateSignature(method, url, params, consumerSecret, tokenSecret) {
  // Sort and encode parameters
  const sortedParams = Object.keys(params)
    .sort()
    .map(key => `${percentEncode(key)}=${percentEncode(params[key])}`)
    .join('&');

  // Create base string
  const baseString = [
    method.toUpperCase(),
    percentEncode(url),
    percentEncode(sortedParams),
  ].join('&');

  // Create signing key
  const signingKey = `${percentEncode(consumerSecret)}&${percentEncode(tokenSecret)}`;

  // Generate HMAC-SHA1
  return crypto
    .createHmac('sha1', signingKey)
    .update(baseString)
    .digest('base64');
}

// ── Build the signed request ──────────────────────────────
const timestamp = generateTimestamp();
const nonce = generateNonce();
const url = `${config.baseUrl}${endpoint}`;

const oauthParams = {
  oauth_consumer_key: config.consumerKey,
  oauth_token: config.accessToken,
  oauth_signature_method: 'HMAC-SHA1',
  oauth_timestamp: timestamp,
  oauth_nonce: nonce,
  oauth_version: '1.0',
};

// Merge OAuth params with query params for signature
const allParams = { ...oauthParams, ...queryParams };

const signature = generateSignature(
  method,
  url,
  allParams,
  config.consumerSecret,
  config.accessTokenSecret
);

oauthParams.oauth_signature = signature;

// Build Authorization header
const authHeader =
  'OAuth ' +
  Object.keys(oauthParams)
    .sort()
    .map(key => `${percentEncode(key)}="${percentEncode(oauthParams[key])}"`)
    .join(', ');

// Build full URL with query params
const queryString = Object.keys(queryParams)
  .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(queryParams[key])}`)
  .join('&');
const fullUrl = queryString ? `${url}?${queryString}` : url;

// Return for HTTP Request node
return [
  {
    json: {
      url: fullUrl,
      method: method,
      headers: {
        Authorization: authHeader,
        'Content-Type': 'application/json',
      },
    },
  },
];
```

**Step 3: Connect to HTTP Request node**

1. Add an **HTTP Request** node after the Code node
2. Configure it:
   - **Method:** `{{ $json.method }}`
   - **URL:** `{{ $json.url }}`
   - **Headers:** Set `Authorization` = `{{ $json.headers.Authorization }}`
   - **Response Format:** JSON
3. Test the workflow — you should get the account list response

**Step 4: Create reusable sub-workflows**

Build one sub-workflow per endpoint:
- `etrade-accounts-list` — no params needed
- `etrade-account-balance` — param: `accountIdKey`
- `etrade-portfolio` — param: `accountIdKey`
- `etrade-quote` — param: `symbols` (comma-separated)
- `etrade-optionchain` — params: `symbol`, `expiryYear`, `expiryMonth`, `expiryDay`, etc.

Each sub-workflow uses the same Code node pattern, just with different endpoint/params.

### Option B: Lightweight Proxy Service

If you prefer a cleaner separation, run a small Express.js server that handles OAuth signing and exposes simple REST endpoints to n8n:

```javascript
// etrade-proxy.js — Run with: node etrade-proxy.js
const express = require('express');
const crypto = require('crypto');
const https = require('https');

const app = express();
const PORT = 3010;

// Store tokens (updated daily via /auth endpoint)
let tokens = {
  consumerKey: process.env.ETRADE_SANDBOX_KEY,
  consumerSecret: process.env.ETRADE_SANDBOX_SECRET,
  accessToken: '',
  accessTokenSecret: '',
};

// OAuth signing logic (same as Code node above)
function signRequest(method, url, params) {
  // ... (same signing logic as Option A)
}

// Proxy endpoint: GET /api/accounts
app.get('/api/accounts', async (req, res) => {
  const result = await makeSignedRequest('GET', '/v1/accounts/list.json', {});
  res.json(result);
});

// Proxy endpoint: GET /api/balance/:accountIdKey
app.get('/api/balance/:id', async (req, res) => {
  const result = await makeSignedRequest('GET',
    `/v1/accounts/${req.params.id}/balance.json`,
    { instType: 'BROKERAGE', realTimeNAV: 'true' }
  );
  res.json(result);
});

// Add more endpoints as needed...

app.listen(PORT, () => console.log(`E-Trade proxy running on port ${PORT}`));
```

Then in n8n, use a simple HTTP Request node pointing to `http://localhost:3010/api/accounts`. No OAuth signing needed in n8n itself.

**Tradeoff:** Option B is cleaner for n8n but requires running another service. Option A keeps everything self-contained in n8n.

### Test from n8n

Regardless of which option you chose:

1. Build a test workflow: **Manual Trigger** > **Code Node (or HTTP to proxy)** > **Debug output**
2. Run it
3. Verify you see the account list response in the output
4. If successful, you have a working n8n-to-E-Trade connection

---

## 7. Troubleshooting Checklist

### Common Issues and Fixes

| Issue | Symptom | Fix |
|-------|---------|-----|
| Token expired | 401 on all API calls | Re-authenticate. Tokens die at midnight ET. |
| Wrong base URL | 401 or connection refused | Sandbox: `apisb.etrade.com`. Production: `api.etrade.com`. Do not mix keys and URLs. |
| Missing `.json` suffix | XML response or 406 error | Append `.json` to all endpoints (e.g., `/v1/accounts/list.json`) |
| Missing `instType` param | 400 on balance endpoint | Add `?instType=BROKERAGE&realTimeNAV=true` to balance requests |
| Signature invalid | 401 with oauth_problem=signature_invalid | Check clock sync, nonce uniqueness, URL encoding. Each request needs a fresh timestamp and nonce. |
| Rate limited | 429 response | Back off. Market data: 2/sec. Account data: 4/sec. Add delays between n8n workflow steps. |
| Sandbox returns stale data | Quotes don't match real market | Expected. Sandbox data may be static. Validate flow, not data. |
| n8n Code node fails | "crypto not found" or similar | Use `require('crypto')` — it is a Node.js built-in, should work in n8n Code nodes |
| Paper trading not showing | No paper account in account dropdown | Call E-Trade support (1-800-387-2331) to enable paper trading feature |
| Options Level 3 denied | Can only trade Level 1-2 | Call options desk, explain your experience and strategy. Reapply after 30 days if needed. |

### Daily Token Re-Authentication Reminder

Set up a recurring reminder to re-authenticate each trading day morning:

**Option 1: n8n Cron + Telegram**
- Create an n8n workflow triggered at 8:00 AM ET on weekdays
- Send a Telegram message: "E-Trade tokens expired. Run auth script before market open."
- Include a link/shortcut to run the `etrade_auth.py` script

**Option 2: Calendar Event**
- Create a recurring Google Calendar event: "E-Trade Re-Auth" at 8:00 AM ET, weekdays only

**Future automation (Phase 2):** Build a semi-automated flow where n8n handles Steps 1 and 3 automatically, and sends you the Step 2 authorization URL via Telegram. You click the link, log in, enter the verifier code into a Telegram bot, and n8n completes the token exchange.

### Rate Limit Management

| Strategy | Implementation |
|----------|---------------|
| Add delays between API calls | In n8n, add a **Wait** node (500ms) between HTTP Request nodes |
| Batch quote requests | Use multi-symbol endpoint: `/v1/market/quote/AAPL,MSFT,GOOGL.json` instead of 3 separate calls |
| Cache where possible | Store quotes in a Google Sheet and only refresh every 5 minutes, not on every workflow trigger |
| Monitor usage | Log API call counts in a Google Sheet to spot if you are approaching limits |
| Use webhooks over polling | Where E-Trade supports it, prefer event-driven triggers over polling |

---

## Quick Reference Card

```
E-TRADE API — QUICK REFERENCE
==============================

URLS
  Sandbox:    https://apisb.etrade.com
  Production: https://api.etrade.com
  Developer:  https://developer.etrade.com
  Auth:       https://us.etrade.com/e/t/etws/authorize
  Support:    1-800-387-2331

AUTH FLOW (Daily)
  1. POST /oauth/request_token → get request token
  2. Browser → authorize → get verifier code
  3. POST /oauth/access_token → get access token
  Tokens expire: midnight ET

KEY ENDPOINTS
  GET /v1/accounts/list.json
  GET /v1/accounts/{idKey}/balance.json?instType=BROKERAGE
  GET /v1/accounts/{idKey}/portfolio.json
  GET /v1/market/quote/{symbols}.json
  GET /v1/market/optionchains.json?symbol=AAPL&chainType=PUT

RATE LIMITS
  Market data: 2 req/sec
  Account data: 4 req/sec

COMMON GOTCHAS
  - Always use .json suffix on endpoints
  - Always pass instType=BROKERAGE on balance calls
  - Use accountIdKey (not accountId) in URLs
  - Tokens cannot be refreshed — must re-auth daily
  - Sandbox keys ≠ production keys
```

---

*This guide is a companion to Trading Infrastructure Setup v1.0 and Paper Trading Launch Plan v1.0. Update the trading-infrastructure-setup.md checklist as tasks are completed.*
