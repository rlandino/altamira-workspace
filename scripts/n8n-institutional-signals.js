// ============================================================
// INSTITUTIONAL SIGNALS
// ============================================================
// Computes: P/C ratio (vol, OI, $), UOA, IV skew (25Δ), GEX,
// Net Sentiment (-100 to +100), Liquidity 1-10, Confidence adj,
// Regime-specific strategy. See reference/institutional-signals-spec.md
// ============================================================

const data = $('Fetch Full Chains (Institutional)').first().json;
const fullChains = data.fullChains || [];
const vix = data.vix ?? 20;
const regime = data.regime || 'NORMAL';

function norm(c, type) {
  const det = c.details || {};
  const g = c.greeks || {};
  const q = c.last_quote || {};
  const strike = det.strike_price ?? c.strike;
  const bid = q.bid ?? c.bid ?? 0;
  const ask = q.ask ?? c.ask ?? 0;
  const mid = (bid + ask) / 2 || 0;
  const vol = (c.day && c.day.volume) ?? c.volume ?? 0;
  const oi = c.open_interest ?? c.openInterest ?? 0;
  const iv = c.implied_volatility ?? c.impliedVolatility ?? null;
  const delta = g.delta ?? c.delta;
  const gamma = g.gamma ?? c.gamma ?? 0;
  return { type, strike, bid, ask, mid, volume: vol, openInterest: oi, iv, delta, gamma, expiration: det.expiration_date || c.expiration };
}

function calcDTE(exp) {
  if (!exp) return null;
  const e = new Date(exp);
  return Math.ceil((e - new Date()) / (1000 * 60 * 60 * 24));
}

const BLOCK_NOTIONAL = 100000;
const UOA_VOL_OI_RATIO = 2;

const tickerSignals = {};

for (const fc of fullChains) {
  const ticker = fc.ticker;
  const spot = fc.price || 1;
  const calls = (fc.calls || []).map(c => norm(c, 'call'));
  const puts = (fc.puts || []).map(c => norm(c, 'put'));

  const callVol = calls.reduce((s, c) => s + (c.volume || 0), 0);
  const putVol = puts.reduce((s, p) => s + (p.volume || 0), 0);
  const callOI = calls.reduce((s, c) => s + (c.openInterest || 0), 0);
  const putOI = puts.reduce((s, p) => s + (p.openInterest || 0), 0);
  const callDollar = calls.reduce((s, c) => s + (c.mid || 0) * 100 * (c.volume || 0), 0);
  const putDollar = puts.reduce((s, p) => s + (p.mid || 0) * 100 * (p.volume || 0), 0);

  const putCallRatioVol = callVol > 0 ? putVol / callVol : (putVol > 0 ? 2 : 1);
  const putCallRatioOI = callOI > 0 ? putOI / callOI : (putOI > 0 ? 2 : 1);
  const putCallRatioDollar = callDollar > 0 ? putDollar / callDollar : (putDollar > 0 ? 2 : 1);

  let unusualCount = 0;
  let largeBlocks = 0;
  const allContracts = [...calls, ...puts];
  for (const c of allContracts) {
    const vol = c.volume || 0;
    const oi = Math.max(c.openInterest || 0, 1);
    if (vol >= UOA_VOL_OI_RATIO * oi) unusualCount++;
    const notional = (c.mid || 0) * 100 * vol;
    if (notional >= BLOCK_NOTIONAL) largeBlocks++;
  }

  let putIV25 = null;
  let callIV25 = null;
  const puts25 = puts.filter(p => p.delta != null && Math.abs(p.delta + 0.25) < 0.05);
  const calls25 = calls.filter(c => c.delta != null && Math.abs(c.delta - 0.25) < 0.05);
  if (puts25.length) putIV25 = puts25.reduce((s, p) => s + (p.iv ?? 0), 0) / puts25.length;
  if (calls25.length) callIV25 = calls25.reduce((s, c) => s + (c.iv ?? 0), 0) / calls25.length;
  let ivSkew25 = null;
  if (putIV25 != null && callIV25 != null && callIV25 > 0) ivSkew25 = putIV25 / callIV25;

  let totalGEX = 0;
  let maxGEXStrike = null;
  let maxGEX = 0;
  for (const c of allContracts) {
    const gamma = c.gamma ?? 0;
    const oi = c.openInterest ?? 0;
    const gex = gamma * oi * 100 * (spot * spot) * (c.type === 'put' ? 1 : -1);
    totalGEX += gex;
    if (Math.abs(gex) > maxGEX) {
      maxGEX = Math.abs(gex);
      maxGEXStrike = c.strike;
    }
  }

  const sentimentFromPC = putCallRatioVol > 1.2 ? -30 : putCallRatioVol < 0.8 ? 30 : 0;
  const sentimentFromSkew = ivSkew25 != null && ivSkew25 > 1.2 ? -20 : ivSkew25 != null && ivSkew25 < 0.9 ? 15 : 0;
  const sentimentFromUOA = unusualCount > 5 ? -15 : 0;
  const netSentiment = Math.max(-100, Math.min(100, Math.round(sentimentFromPC + sentimentFromSkew + sentimentFromUOA)));

  const avgSpreadPct = allContracts.filter(c => c.mid > 0).length
    ? allContracts.filter(c => c.mid > 0).reduce((s, c) => s + (Math.abs(c.ask - c.bid) / c.mid) * 100, 0) / Math.max(1, allContracts.filter(c => c.mid > 0).length)
    : 10;
  const maxOI = Math.max(...allContracts.map(c => c.openInterest || 0), 1);
  const maxVol = Math.max(...allContracts.map(c => c.volume || 0), 0);
  let liquidityScore = 5;
  if (avgSpreadPct < 5 && maxOI >= 500 && maxVol >= 50) liquidityScore = 9;
  else if (avgSpreadPct < 8 && maxOI >= 100) liquidityScore = 7;
  else if (avgSpreadPct > 15 || maxOI < 50) liquidityScore = 3;
  else liquidityScore = 5;
  liquidityScore = Math.max(1, Math.min(10, liquidityScore));

  let confidenceAdjustment = 0;
  if (netSentiment > 20) confidenceAdjustment = 3;
  else if (netSentiment < -20) confidenceAdjustment = -3;
  if (unusualCount > 3) confidenceAdjustment -= 1;

  const regimeStrategies = {
    LOW: 'Naked CSP / covered calls OK.',
    NORMAL: 'CSP, bull put spreads, covered calls.',
    ELEVATED: 'Prefer defined-risk spreads; reduce size.',
    CRISIS: 'Spreads only; minimal size; avoid naked options.'
  };
  const regimeStrategy = regimeStrategies[regime] || regimeStrategies.NORMAL;

  tickerSignals[ticker] = {
    putCallRatioVol: Math.round(putCallRatioVol * 100) / 100,
    putCallRatioOI: Math.round(putCallRatioOI * 100) / 100,
    putCallRatioDollar: Math.round(putCallRatioDollar * 100) / 100,
    unusualActivityCount: unusualCount,
    largeBlocksCount: largeBlocks,
    ivSkew25: ivSkew25 != null ? Math.round(ivSkew25 * 1000) / 1000 : null,
    gex: Math.round(totalGEX),
    maxGammaStrike: maxGEXStrike,
    netSentiment,
    liquidityScore1_10: liquidityScore,
    confidenceAdjustment,
    regimeStrategy
  };
}

return [{
  json: {
    tickerSignals,
    vix,
    regime,
    sizingPct: data.sizingPct,
    dateStr: data.dateStr
  }
}];
