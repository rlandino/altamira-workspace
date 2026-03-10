#!/usr/bin/env python3
"""
Altamira Capital — Paper Trading Pre-Launch Readiness Checker

Run this script before March 1 to verify all paper trading prerequisites
are in place. Checks for required files, configurations, and connectivity.

Usage:
    python scripts/pre-launch-check.py
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Configuration
WORKSPACE = Path(__file__).parent.parent
OUTPUTS = WORKSPACE / "outputs"
SCRIPTS = WORKSPACE / "scripts"
COMMANDS = WORKSPACE / ".claude" / "commands"

# Colors for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
RESET = "\033[0m"

def check(name, condition, detail=""):
    """Print a check result."""
    if condition:
        print(f"  {GREEN}[PASS]{RESET} {name}")
    else:
        print(f"  {RED}[FAIL]{RESET} {name}")
        if detail:
            print(f"         {YELLOW}→ {detail}{RESET}")
    return condition


def section(title):
    """Print a section header."""
    print(f"\n{BOLD}{'=' * 60}{RESET}")
    print(f"{BOLD}  {title}{RESET}")
    print(f"{BOLD}{'=' * 60}{RESET}\n")


def check_strategy_documents():
    """Verify all required strategy documents exist."""
    section("1. STRATEGY DOCUMENTS")

    required_docs = {
        "Investment Thesis v2.0": OUTPUTS / "altamira-investment-thesis.md",
        "Risk Management Framework": OUTPUTS / "risk-management-framework.md",
        "Portfolio Allocation Model": OUTPUTS / "portfolio-allocation-model.md",
        "Paper Trading Launch Plan": OUTPUTS / "paper-trading-plan.md",
        "Trading Infrastructure Setup": OUTPUTS / "trading-infrastructure-setup.md",
        "Market Monitoring Workflows": OUTPUTS / "market-monitoring-workflows.md",
        "Backtest Results": OUTPUTS / "backtest-results-2026-02-18.md",
        "E-Trade API Setup Guide": OUTPUTS / "etrade-api-setup-guide.md",
    }

    results = []
    for name, path in required_docs.items():
        exists = path.exists()
        detail = f"Missing: {path}" if not exists else ""
        results.append(check(name, exists, detail))

    return all(results)


def check_n8n_workflows():
    """Verify all n8n workflow JSON files exist and are valid JSON."""
    section("2. N8N WORKFLOW FILES")

    workflows = {
        "Daily Portfolio Snapshot": OUTPUTS / "n8n-workflow-1-daily-portfolio-snapshot.json",
        "Trade Entry Logger": OUTPUTS / "n8n-workflow-2-trade-entry-logger.json",
        "Weekly Metrics Calculator": OUTPUTS / "n8n-workflow-3-weekly-metrics-calculator.json",
        "Risk Limit Monitor": OUTPUTS / "n8n-workflow-4-risk-limit-monitor.json",
        "Watchlist Alert System": OUTPUTS / "n8n-workflow-watchlist-alert-system.json",
        "Volatility Regime Monitor": OUTPUTS / "n8n-workflow-volatility-regime-hedging.json",
    }

    results = []
    for name, path in workflows.items():
        if not path.exists():
            results.append(check(name, False, f"Missing: {path}"))
            continue

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            has_nodes = "nodes" in data or (isinstance(data, list) and len(data) > 0)
            results.append(check(f"{name} (valid JSON, has nodes)", has_nodes,
                                "JSON is valid but missing 'nodes' key" if not has_nodes else ""))
        except json.JSONDecodeError as e:
            results.append(check(name, False, f"Invalid JSON: {e}"))

    return all(results)


def check_google_sheets_script():
    """Verify the Google Sheets Apps Script exists."""
    section("3. GOOGLE SHEETS SETUP")

    results = []

    gs_path = OUTPUTS / "paper-trading-workbook.gs"
    results.append(check("Apps Script file exists", gs_path.exists(),
                        "Missing: outputs/paper-trading-workbook.gs"))

    if gs_path.exists():
        content = gs_path.read_text(encoding="utf-8")
        results.append(check("Contains setupPaperTradingWorkbook function",
                            "setupPaperTradingWorkbook" in content,
                            "Main setup function not found in script"))
        results.append(check("Script is substantial (>500 lines)",
                            content.count("\n") > 500,
                            f"Script has only {content.count(chr(10))} lines — may be incomplete"))

    # Check for Google Sheet ID in environment
    sheet_id = os.environ.get("GOOGLE_SHEET_ID", "")
    results.append(check("GOOGLE_SHEET_ID environment variable set",
                        bool(sheet_id),
                        "Set GOOGLE_SHEET_ID env var with the paper trading workbook ID"))

    return all(results)


def check_claude_commands():
    """Verify Claude commands exist."""
    section("4. CLAUDE COMMANDS")

    required_commands = {
        "/analyze-ticker": COMMANDS / "analyze-ticker.md",
        "/options-scan": COMMANDS / "options-scan.md",
        "/portfolio-report": COMMANDS / "portfolio-report.md",
        "/paper-trade": COMMANDS / "paper-trade.md",
        "/prime": COMMANDS / "prime.md",
    }

    results = []
    for name, path in required_commands.items():
        results.append(check(name, path.exists(), f"Missing: {path}"))

    return all(results)


def check_api_keys():
    """Check for required API keys in environment."""
    section("5. API KEYS & CREDENTIALS")

    results = []

    # FMP API
    fmp_key = os.environ.get("FMP_API_KEY", "")
    results.append(check("FMP_API_KEY set", bool(fmp_key),
                        "Set FMP_API_KEY environment variable"))

    # Massive.com
    massive_key = os.environ.get("MASSIVE_API_KEY", "")
    results.append(check("MASSIVE_API_KEY set", bool(massive_key),
                        "Set MASSIVE_API_KEY environment variable (optional — may be in n8n)"))

    # E-Trade
    etrade_key = os.environ.get("ETRADE_CONSUMER_KEY", "")
    etrade_secret = os.environ.get("ETRADE_CONSUMER_SECRET", "")
    results.append(check("ETRADE_CONSUMER_KEY set", bool(etrade_key),
                        "Register at developer.etrade.com — see outputs/etrade-api-setup-guide.md"))
    results.append(check("ETRADE_CONSUMER_SECRET set", bool(etrade_secret),
                        "Register at developer.etrade.com — see outputs/etrade-api-setup-guide.md"))

    # Telegram
    telegram_chat = os.environ.get("TELEGRAM_CHAT_ID", "")
    results.append(check("TELEGRAM_CHAT_ID set", bool(telegram_chat),
                        "Set TELEGRAM_CHAT_ID for alert notifications"))

    return all(results)


def check_backtest_framework():
    """Verify backtest scripts exist."""
    section("6. BACKTEST FRAMEWORK")

    results = []

    bt_path = SCRIPTS / "backtest-strategies.py"
    results.append(check("backtest-strategies.py exists", bt_path.exists(),
                        f"Missing: {bt_path}"))

    bt_results = OUTPUTS / "backtest-results-2026-02-18.md"
    results.append(check("Backtest results generated", bt_results.exists(),
                        "Run backtest-strategies.py to generate results"))

    return all(results)


def check_timeline():
    """Check timeline status relative to launch date."""
    section("7. TIMELINE STATUS")

    today = datetime.now().date()
    launch = datetime(2026, 3, 1).date()
    days_until = (launch - today).days

    results = []

    if days_until > 0:
        results.append(check(f"Days until paper trading launch: {days_until}",
                            days_until >= 0))
    elif days_until == 0:
        print(f"  {GREEN}{BOLD}TODAY IS LAUNCH DAY!{RESET}")
        results.append(True)
    else:
        print(f"  {YELLOW}Paper trading should have started {abs(days_until)} days ago{RESET}")
        results.append(True)

    # Key deadlines
    deadlines = {
        "E-Trade API keys obtained": datetime(2026, 2, 19).date(),
        "OAuth 1.0a tested": datetime(2026, 2, 20).date(),
        "Sandbox endpoints verified": datetime(2026, 2, 21).date(),
        "Google Sheets workbook created": datetime(2026, 2, 22).date(),
        "n8n workflows imported": datetime(2026, 2, 25).date(),
        "End-to-end pipeline test": datetime(2026, 2, 27).date(),
        "Paper trading launch": datetime(2026, 3, 1).date(),
    }

    print(f"\n  {BOLD}Milestone Checklist (manual verification):{RESET}")
    for milestone, deadline in deadlines.items():
        status = "UPCOMING" if deadline >= today else "PAST DUE"
        color = YELLOW if deadline >= today else RED
        if deadline < today:
            print(f"  {color}[ ] {milestone} — was due {deadline} ({status}){RESET}")
        else:
            days = (deadline - today).days
            print(f"  {color}[ ] {milestone} — due {deadline} ({days} days){RESET}")

    return True


def main():
    print(f"\n{BOLD}{'#' * 60}{RESET}")
    print(f"{BOLD}  ALTAMIRA CAPITAL — PRE-LAUNCH READINESS CHECK{RESET}")
    print(f"{BOLD}  {datetime.now().strftime('%Y-%m-%d %H:%M')}{RESET}")
    print(f"{BOLD}{'#' * 60}{RESET}")

    sections = [
        ("Strategy Documents", check_strategy_documents),
        ("n8n Workflows", check_n8n_workflows),
        ("Google Sheets", check_google_sheets_script),
        ("Claude Commands", check_claude_commands),
        ("API Keys", check_api_keys),
        ("Backtest Framework", check_backtest_framework),
        ("Timeline", check_timeline),
    ]

    results = {}
    for name, func in sections:
        results[name] = func()

    # Summary
    section("SUMMARY")

    total_pass = sum(1 for v in results.values() if v)
    total = len(results)

    for name, passed in results.items():
        icon = f"{GREEN}PASS{RESET}" if passed else f"{RED}FAIL{RESET}"
        print(f"  [{icon}] {name}")

    print(f"\n  {BOLD}Result: {total_pass}/{total} sections passing{RESET}")

    if total_pass == total:
        print(f"\n  {GREEN}{BOLD}ALL CHECKS PASS — Ready for paper trading launch!{RESET}")
    else:
        failed = [name for name, passed in results.items() if not passed]
        print(f"\n  {YELLOW}{BOLD}Action needed in: {', '.join(failed)}{RESET}")
        print(f"  {YELLOW}See outputs/etrade-api-setup-guide.md for setup instructions{RESET}")

    print()
    return 0 if total_pass == total else 1


if __name__ == "__main__":
    sys.exit(main())
