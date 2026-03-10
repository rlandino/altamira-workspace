"""Parse Massive options JSON and output metrics for options-scan report."""
import json
import sys
from datetime import datetime
from pathlib import Path

def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(r'C:\Users\rland\.cursor\projects\x-Claude-altamira-workspace\agent-tools\58c040bf-029a-48cb-bbfe-7869fff34a84.txt')
    raw = path.read_text()
    data = json.loads(raw)
    results = data.get('results', [])
    today = datetime(2026, 3, 2).date()

    def parse_date(s):
        return datetime.strptime(s[:10], '%Y-%m-%d').date() if s else None

    def dte(exp):
        if not exp: return 999
        d = parse_date(exp)
        return (d - today).days

    chain = []
    for r in results:
        exp = r.get('details', {}).get('expiration_date')
        dt = dte(exp)
        if dt < 20 or dt > 60:
            continue
        q = r.get('last_quote') or {}
        bid = q.get('bid') or 0
        ask = q.get('ask') or 0
        if bid <= 0 and ask <= 0:
            continue
        mid = (bid + ask) / 2 if (bid + ask) > 0 else 0
        oi = r.get('open_interest') or 0
        vol = (r.get('day') or {}).get('volume') or 0
        chain.append({
            'type': (r.get('details') or {}).get('contract_type', ''),
            'exp': exp, 'dte': dt, 'strike': (r.get('details') or {}).get('strike_price'),
            'bid': bid, 'ask': ask, 'mid': mid, 'oi': oi, 'vol': vol,
            'delta': (r.get('greeks') or {}).get('delta'), 'gamma': (r.get('greeks') or {}).get('gamma'),
            'iv': r.get('implied_volatility'), 'underlying_price': (r.get('underlying_asset') or {}).get('price') or 1007.77
        })

    calls = [c for c in chain if c['type'] == 'call']
    puts = [c for c in chain if c['type'] == 'put']
    liquid = [c for c in chain if c['oi'] >= 50 and c['bid'] >= 0.05]
    liquid_puts = [c for c in liquid if c['type'] == 'put']

    put_vol = sum(p['vol'] for p in puts)
    call_vol = sum(c['vol'] for c in calls)
    put_oi = sum(p['oi'] for p in puts)
    call_oi = sum(c['oi'] for c in calls)
    vol_pc = put_vol / call_vol if call_vol else 0
    oi_pc = put_oi / call_oi if call_oi else 0

    uoa_count = sum(1 for c in chain if c['vol'] > 2 * c['oi'] and c['oi'] > 0)

    put_25 = [p for p in puts if p.get('delta') and -0.35 <= p['delta'] <= -0.15]
    call_25 = [c for c in calls if c.get('delta') and 0.15 <= c.get('delta', 0) <= 0.35]
    put_iv_25 = put_25[0]['iv'] if put_25 and put_25[0].get('iv') else None
    call_iv_25 = call_25[0]['iv'] if call_25 and call_25[0].get('iv') else None
    skew = (put_iv_25 / call_iv_25) if (put_iv_25 and call_iv_25 and call_iv_25 > 0) else None

    spot = 1007.77
    gex_list = []
    for c in chain:
        g = c.get('gamma') or 0
        oi = c.get('oi') or 0
        gex_list.append({'strike': c['strike'], 'gex': g * oi * 100 * (spot ** 2)})
    total_gex = sum(x['gex'] for x in gex_list)
    max_gex = max(gex_list, key=lambda x: abs(x['gex'])) if gex_list else None

    csp_candidates = [c for c in liquid_puts if 30 <= c['dte'] <= 45 and c.get('delta') and 0.15 <= c['delta'] <= 0.35]
    csp_candidates.sort(key=lambda x: -(x.get('mid') or 0))

    out = {
        'chain_count': len(chain),
        'calls': len(calls), 'puts': len(puts),
        'vol_pc': round(vol_pc, 3) if vol_pc else None,
        'oi_pc': round(oi_pc, 3) if oi_pc else None,
        'uoa_count': uoa_count,
        'skew': round(skew, 3) if skew else None,
        'total_gex_billions': round(total_gex / 1e9, 4) if total_gex else 0,
        'max_gex_strike': max_gex['strike'] if max_gex else None,
        'csp_candidates': [{'strike': c['strike'], 'exp': c['exp'], 'dte': c['dte'], 'mid': round(c.get('mid') or 0, 2), 'delta': round(c.get('delta') or 0, 3), 'iv': c.get('iv')} for c in csp_candidates[:5]]
    }
    print(json.dumps(out, indent=2))

if __name__ == '__main__':
    main()
