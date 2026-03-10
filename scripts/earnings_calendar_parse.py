import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
data = json.loads(path.read_text())
data.sort(key=lambda x: (x.get("date", ""), x.get("symbol", "")))
seen = set()
order = []
for r in data:
    s = r.get("symbol")
    if s and s not in seen:
        seen.add(s)
        order.append(s)
print("Total rows", len(data))
print("Unique symbols", len(order))
print("SYMBOLS", ",".join(order[:60]))
# First 40 rows for table
for r in data[:40]:
    print("ROW", r.get("date"), r.get("symbol"), r.get("time") or "-", r.get("fiscalDateEnding"))
