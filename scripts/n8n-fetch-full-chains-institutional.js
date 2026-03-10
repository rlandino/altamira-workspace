// ============================================================
// FETCH FULL CHAINS (INSTITUTIONAL)
// ============================================================
// Fetches both calls and puts (20-60 DTE) per cleared ticker
// for P/C ratio, UOA, IV skew, GEX. Uses Massive.com v3 API.
// ============================================================

const data = $('Filter Earnings Conflicts').first().json;
const cleared = data.cleared || [];

if (!cleared.length) {
  return [{ json: { fullChains: [], tickerSignals: {}, vix: data.vix, regime: data.regime, sizingPct: data.sizingPct, dateStr: data.dateStr } }];
}

const MASSIVE_API_KEY = 'kEnhZTIYm_UZZSfpSPuYQgsW_kG0vPHp';
const today = new Date();
const fromDate = new Date(today);
fromDate.setDate(fromDate.getDate() + 20);
const toDate = new Date(today);
toDate.setDate(toDate.getDate() + 60);
const fromStr = fromDate.toISOString().split('T')[0];
const toStr = toDate.toISOString().split('T')[0];

const fullChains = [];

for (const t of cleared) {
  let calls = [];
  let puts = [];
  try {
    const [callResp, putResp] = await Promise.all([
      fetch(`https://api.massive.com/v3/snapshot/options/${t.ticker}?contract_type=call&expiration_date.gte=${fromStr}&expiration_date.lte=${toStr}&limit=250`, {
        headers: { 'Authorization': `Bearer ${MASSIVE_API_KEY}`, 'Content-Type': 'application/json' },
        signal: AbortSignal.timeout(12000)
      }),
      fetch(`https://api.massive.com/v3/snapshot/options/${t.ticker}?contract_type=put&expiration_date.gte=${fromStr}&expiration_date.lte=${toStr}&limit=250`, {
        headers: { 'Authorization': `Bearer ${MASSIVE_API_KEY}`, 'Content-Type': 'application/json' },
        signal: AbortSignal.timeout(12000)
      })
    ]);
    if (callResp.ok) {
      const j = await callResp.json();
      calls = j.results || [];
    }
    if (putResp.ok) {
      const j = await putResp.json();
      puts = j.results || [];
    }
  } catch (e) {}
  fullChains.push({
    ticker: t.ticker,
    price: t.price,
    calls,
    puts
  });
}

return [{
  json: {
    fullChains,
    vix: data.vix,
    regime: data.regime,
    sizingPct: data.sizingPct,
    dateStr: data.dateStr,
    timestamp: data.timestamp
  }
}];
