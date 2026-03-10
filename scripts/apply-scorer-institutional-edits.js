const fs = require('fs');
const path = require('path');
const workflowPath = path.join(__dirname, '..', 'outputs', 'n8n-workflow-csp-daily-scan.json');
const w = JSON.parse(fs.readFileSync(workflowPath, 'utf8'));
const scorer = w.nodes.find(n => n.name === 'CSP Opportunity Scorer');
let code = scorer.parameters.jsCode;

// 1. Add inst signals and vix mult
code = code.replace(
  "const data = $('Fetch Options Chains').first().json;\nconst chains = data.chains || [];",
  "const data = $('Fetch Options Chains').first().json;\nlet instSignals = null; try { instSignals = $('Institutional Signals').first().json; } catch(e) {}\nconst tickerSignals = instSignals && instSignals.tickerSignals ? instSignals.tickerSignals : {};\nconst vixConfidenceMult = data.regime === 'ELEVATED' ? 0.9 : data.regime === 'CRISIS' ? 0.75 : 1;\nconst chains = data.chains || [];"
);

// 2. Add sig, confAdj, vixAdjustedScore before allOpportunities.push
code = code.replace(
  "// Weighted composite\n    const compositeScore = (\n      returnScore * 0.40 +\n      ivScore * 0.30 +\n      liquidityScore * 0.20 +\n      trendScore * 0.10\n    );\n\n    allOpportunities.push({",
  "// Weighted composite\n    const compositeScore = (\n      returnScore * 0.40 +\n      ivScore * 0.30 +\n      liquidityScore * 0.20 +\n      trendScore * 0.10\n    );\n    const sig = tickerSignals[chain.ticker] || {};\n    const confAdj = sig.confidenceAdjustment ?? 0;\n    const vixAdjustedScore = (compositeScore + confAdj) * vixConfidenceMult;\n\n    allOpportunities.push({"
);

// 3. Add new fields to push object
code = code.replace(
  "stopLoss: Math.round(premium * 2.00 * 100) / 100,     // stop at 200% of credit\n      source: chain.source\n    });",
  "stopLoss: Math.round(premium * 2.00 * 100) / 100,     // stop at 200% of credit\n      source: chain.source,\n      confidenceAdjustment: confAdj,\n      vixAdjustedScore: Math.round(vixAdjustedScore * 100) / 100,\n      liquidityScore1_10: sig.liquidityScore1_10 ?? 5,\n      regimeStrategy: sig.regimeStrategy || '',\n      netSentiment: sig.netSentiment ?? null,\n      putCallRatioVol: sig.putCallRatioVol ?? null\n    });"
);

// 4. Sort by vixAdjustedScore
code = code.replace(
  "// --- SECTOR DIVERSIFICATION CHECK ---\n// Sort by score first\nallOpportunities.sort((a, b) => b.compositeScore - a.compositeScore);",
  "// --- SECTOR DIVERSIFICATION CHECK ---\n// Sort by VIX-adjusted score (includes institutional confidence)\nallOpportunities.sort((a, b) => (b.vixAdjustedScore ?? b.compositeScore) - (a.vixAdjustedScore ?? a.compositeScore));"
);

// 5. Add institutionalSummary before return
code = code.replace(
  "const cashPct = Math.round((cashAfterTrades / PORTFOLIO_VALUE) * 100);\n\nreturn [{\n  json: {\n    top3,\n    totalScanned: allOpportunities.length,\n    sectorCount,",
  "const cashPct = Math.round((cashAfterTrades / PORTFOLIO_VALUE) * 100);\nconst instTickers = Object.keys(tickerSignals);\nconst avgNetSentiment = instTickers.length ? Math.round(instTickers.reduce((s, k) => s + (tickerSignals[k].netSentiment ?? 0), 0) / instTickers.length) : null;\nconst institutionalSummary = { avgNetSentiment, regimeStrategy: instTickers.length && tickerSignals[instTickers[0]] ? tickerSignals[instTickers[0]].regimeStrategy : (data.regime === 'ELEVATED' ? 'Prefer defined-risk spreads; reduce size.' : data.regime === 'CRISIS' ? 'Spreads only; minimal size.' : 'CSP, bull put spreads, covered calls.') };\n\nreturn [{\n  json: {\n    top3,\n    totalScanned: allOpportunities.length,\n    institutionalSummary,\n    sectorCount,"
);

scorer.parameters.jsCode = code;

// Format Telegram: add institutional line and score line
const fmt = w.nodes.find(n => n.name === 'Format Telegram Alert');
let fmtCode = fmt.parameters.jsCode;
fmtCode = fmtCode.replace(
  "`Scanned: ${data.totalScanned} contracts across ${data.sectorCount ? Object.keys(data.sectorCount).length : 0} sectors`,\n  ''\n];",
  "`Scanned: ${data.totalScanned} contracts across ${data.sectorCount ? Object.keys(data.sectorCount).length : 0} sectors`,\n  (data.institutionalSummary ? `Institutional: Sentiment ${data.institutionalSummary.avgNetSentiment ?? 'N/A'} | ${data.institutionalSummary.regimeStrategy || ''}` : ''),\n  ''\n].filter(Boolean);"
);
fmtCode = fmtCode.replace(
  "lines.push(`  Score: ${o.compositeScore} (Ret:${o.returnScore} IV:${o.ivScore} Liq:${o.liquidityScore} Trend:${o.trendScore})`);",
  "lines.push(`  Score: ${o.compositeScore} (Adj:${o.vixAdjustedScore ?? o.compositeScore}) | Liq: ${o.liquidityScore1_10 ?? o.liquidityScore ?? '?'}/10`);"
);
fmt.parameters.jsCode = fmtCode;

fs.writeFileSync(workflowPath, JSON.stringify(w, null, 2));
console.log('Scorer and Format Telegram updated.');
