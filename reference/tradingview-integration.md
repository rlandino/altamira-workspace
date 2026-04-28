# TradingView Desktop App → Altamira Dashboard Integration

This guide wires the **TradingView desktop app** to the **Altamira Dashboard
(Next.js, :3001)** via a local FastAPI webhook bridge.

## How "connecting" to TradingView actually works

The TradingView desktop app is a Chromium wrapper around the TradingView web
app. There is no public REST/WebSocket API for end users. The only programmatic
hook is the **Webhook URL** field on an alert: when the alert fires, the
TradingView servers (not your desktop) POST a JSON payload to that URL.

So the integration is:

```
[TradingView desktop app] -- creates alert with webhook URL -->
  [TradingView servers] -- HTTPS POST on alert fire -->
    [ngrok / cloudflared tunnel] -- HTTP -->
      [tradingview_webhook_api.py on :8002 — this workspace] -- writes -->
        outputs/tradingview-alerts.jsonl
                                                   ^
                                                   |
                          [Altamira Dashboard :3001] -- polls / SWR -->
```

The dashboard reads from `localhost:8002` directly; it never talks to
TradingView. Webhook alerts require **TradingView Pro+** or higher.

---

## 1. Start the webhook bridge

```bash
# from workspace root
pip install fastapi uvicorn  # if not already installed
python -m uvicorn scripts.tradingview_webhook_api:app --host 0.0.0.0 --port 8002
```

Health check:

```bash
curl http://localhost:8002/api/tradingview/health
```

Optional: set a shared secret so random internet traffic can't spam you.

```bash
export TRADINGVIEW_WEBHOOK_SECRET="pick-a-long-random-string"
python -m uvicorn scripts.tradingview_webhook_api:app --host 0.0.0.0 --port 8002
```

When set, every alert payload must include `"secret": "..."` matching the env
var, otherwise it's rejected with 401.

Smoke test (mimics what TradingView will send):

```bash
curl -X POST http://localhost:8002/api/tradingview/webhook \
  -H 'Content-Type: application/json' \
  -d '{"ticker":"SPY","action":"buy","price":585.42,"strategy":"RSI cross"}'

curl http://localhost:8002/api/tradingview/alerts
```

---

## 2. Expose the webhook to TradingView's servers

TradingView's servers must be able to reach the URL you put in the alert.
`localhost:8002` won't work. Pick one tunnel:

### ngrok (fastest)

```bash
ngrok http 8002
# copy the https URL it prints, e.g. https://abc123.ngrok-free.app
```

Your webhook URL is then:
`https://abc123.ngrok-free.app/api/tradingview/webhook`

### Cloudflare Tunnel (free, stable subdomain)

```bash
cloudflared tunnel --url http://localhost:8002
```

Use the `https://*.trycloudflare.com` URL it prints.

---

## 3. Configure the alert in the TradingView desktop app

1. Open the desktop app and load a chart.
2. Right-click the chart → **Add alert** (or press `Alt+A`).
3. In the alert dialog, open the **Notifications** tab.
4. Tick **Webhook URL** and paste the tunnel URL from step 2:
   `https://abc123.ngrok-free.app/api/tradingview/webhook`
5. In the **Message** field, paste a JSON template the bridge can parse:

   ```json
   {
     "secret": "pick-a-long-random-string",
     "ticker": "{{ticker}}",
     "action": "{{strategy.order.action}}",
     "price": {{close}},
     "time": "{{timenow}}",
     "strategy": "{{strategy.order.id}}",
     "message": "{{strategy.order.alert_message}}"
   }
   ```

   Drop the `secret` field if you didn't set `TRADINGVIEW_WEBHOOK_SECRET`.
   TradingView placeholders like `{{ticker}}` and `{{close}}` are substituted
   server-side at fire time.

6. Save the alert. When it fires, you'll see a new line in
   `outputs/tradingview-alerts.jsonl` and the alert will appear in
   `GET /api/tradingview/alerts`.

---

## 4. Wire the Altamira Dashboard

The dashboard repo lives on Windows at:
`C:\Users\rland\OneDrive\Desktop\Claude Code Skills Factory\OpenStock-clone`

Add an API proxy so the browser doesn't hit a different origin (matches the
existing `market_data_api` proxy pattern).

### `app/api/tradingview/alerts/route.ts`

```ts
import { NextRequest, NextResponse } from "next/server";

const BRIDGE = process.env.TRADINGVIEW_BRIDGE_URL ?? "http://localhost:8002";

export async function GET(req: NextRequest) {
  const url = new URL(req.url);
  const qs = url.search; // forward ?limit=&symbol=
  const r = await fetch(`${BRIDGE}/api/tradingview/alerts${qs}`, {
    cache: "no-store",
  });
  return NextResponse.json(await r.json(), { status: r.status });
}
```

### `app/components/TradingViewAlerts.tsx`

```tsx
"use client";
import useSWR from "swr";

type Alert = {
  received_at: string;
  symbol?: string;
  ticker?: string;
  action?: string;
  price?: number;
  strategy?: string;
  payload?: Record<string, unknown>;
};

const fetcher = (u: string) => fetch(u).then((r) => r.json());

export default function TradingViewAlerts({ symbol }: { symbol?: string }) {
  const qs = symbol ? `?symbol=${symbol}&limit=20` : `?limit=20`;
  const { data, error } = useSWR<{ alerts: Alert[] }>(
    `/api/tradingview/alerts${qs}`,
    fetcher,
    { refreshInterval: 5000 },
  );

  if (error) return <div>Failed to load TradingView alerts</div>;
  if (!data) return <div>Loading…</div>;

  return (
    <div className="rounded border p-4">
      <h3 className="text-sm font-semibold mb-2">TradingView Alerts</h3>
      {data.alerts.length === 0 && <div className="text-xs text-gray-500">No alerts yet.</div>}
      <ul className="space-y-1 text-xs">
        {data.alerts.map((a, i) => (
          <li key={i} className="flex justify-between gap-3">
            <span className="font-mono">{a.received_at.replace("T", " ").replace("+00:00", "Z")}</span>
            <span className="font-bold">{a.symbol ?? a.ticker ?? "—"}</span>
            <span className={a.action === "buy" ? "text-green-600" : a.action === "sell" ? "text-red-600" : ""}>
              {a.action ?? ""}
            </span>
            <span>{a.price ?? ""}</span>
            <span className="text-gray-500 truncate max-w-[12rem]">{a.strategy ?? ""}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

Drop `<TradingViewAlerts />` into any dashboard page (or `<TradingViewAlerts symbol="SPY" />`
for a per-ticker panel).

If the dashboard runs on Windows and the bridge runs in WSL/Linux on the same
machine, `http://localhost:8002` works from Windows because WSL2 forwards
localhost. If you run them on separate hosts, set
`TRADINGVIEW_BRIDGE_URL=http://<lan-ip>:8002` in the dashboard's `.env.local`.

---

## 5. Operate

| Task | Command |
|------|---------|
| Start bridge | `python -m uvicorn scripts.tradingview_webhook_api:app --host 0.0.0.0 --port 8002` |
| Tail alert log | `tail -f outputs/tradingview-alerts.jsonl` |
| List recent alerts | `curl http://localhost:8002/api/tradingview/alerts?limit=20` |
| Latest alert for SPY | `curl 'http://localhost:8002/api/tradingview/alerts/latest?symbol=SPY'` |
| Clear log | `curl -X DELETE 'http://localhost:8002/api/tradingview/alerts?confirm=yes'` |
| Health | `curl http://localhost:8002/api/tradingview/health` |

---

## Troubleshooting

- **TradingView shows "Webhook URL test failed"** — the alert dialog only does a
  simple GET probe; the bridge is POST-only. This is expected. The real test
  is firing the alert (or a manual `curl POST`).
- **No alerts arriving** — check the ngrok/cloudflared dashboard for inbound
  requests. If you see them but nothing in `outputs/tradingview-alerts.jsonl`,
  inspect the bridge logs for 401 (secret mismatch) or 4xx.
- **TradingView account level** — Webhook URLs require Pro+; on Basic the
  field is disabled.
- **Rate limiting** — TV will retry failed deliveries a few times then give
  up. Make sure the tunnel is up before saving the alert.
