#!/usr/bin/env python3
"""Build earnings calendar table from FMP calendar + quote data (temp)."""
import json
import sys
from pathlib import Path
from datetime import datetime

def main():
    cal_path = Path(r'C:\Users\rland\.cursor\projects\x-Claude-altamira-workspace\agent-tools\1dc1a328-8e17-4424-9485-8fab0d03ce89.txt')
    quote_path = Path(r'C:\Users\rland\.cursor\projects\x-Claude-altamira-workspace\agent-tools\016f93af-e916-491d-ad64-918c98891092.txt')
    cal = json.loads(cal_path.read_text(encoding='utf-8'))
    quotes = json.loads(quote_path.read_text(encoding='utf-8'))
    info = {q['symbol']: {'name': q['name'], 'marketCap': q.get('marketCap') or 0} for q in quotes}

    def fmt_mcap(m):
        if m is None or m == 0:
            return '—'
        if m >= 1e12:
            return f'{m/1e12:.2f}T'
        if m >= 1e9:
            return f'{m/1e9:.2f}B'
        if m >= 1e6:
            return f'{m/1e6:.2f}M'
        return str(m)

    def fmt_qe(d):
        if not d:
            return '—'
        try:
            dt = datetime.strptime(d[:10], '%Y-%m-%d')
            return dt.strftime('%b/%Y')
        except Exception:
            return d[:7] if d else '—'

    rows = [r for r in cal if '.' not in r.get('symbol', '') and len(r.get('symbol', '')) <= 5]
    rows.sort(key=lambda r: (r.get('date', ''), r.get('symbol', '')))
    max_rows = 55
    out = []
    for r in rows:
        if len(out) >= max_rows:
            break
        sym = r['symbol']
        if sym not in info:
            continue
        date = r.get('date', '')[:10]
        mmdd = date[5:7] + '/' + date[8:10] if len(date) >= 10 else date
        time = r.get('time') or '—'
        qe = fmt_qe(r.get('fiscalDateEnding'))
        name = (info[sym]['name'] or '—')[:40]
        mcap = fmt_mcap(info[sym]['marketCap'])
        out.append((sym, name, mmdd, time, qe, mcap))

    print('| Ticker | Company | Date | Time | Quarter Ending | Market Cap |')
    print('|--------|---------|------|------|----------------|------------|')
    for sym, name, mmdd, time, qe, mcap in out:
        print(f'| {sym} | {name} | {mmdd} | {time} | {qe} | {mcap} |')

if __name__ == '__main__':
    main()
