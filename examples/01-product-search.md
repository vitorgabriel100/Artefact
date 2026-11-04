# Find available acoustic guitars below BRL 1,000.

Mode: offline (deterministic).
Session: guest.

**Customer**

Show available acoustic guitars under BRL 1000.

**Assistant**

- Tagima Memphis AC-39 Nylon Natural: BRL 429.90 — available
- Rozini RC-104 Nylon Estudante: BRL 459.90 — available
- Shelby SN-100 Folk Aço Preto: BRL 549.00 — available
- Giannini GF-1R Aço Folk Sunburst: BRL 579.90 — available
- Yamaha C40 Nylon Natural: BRL 599.90 — available
Source: supplied product snapshot. Prices do not reserve stock.

**Tools called during this turn**

- `search_products({"category": "Violões", "limit": 5, "max_price": 999.99, "payment": "table"})`

## Evidence

products.csv, categories.csv and promotions.csv

The search excludes unavailable products and applies a strict upper price bound. The chat displays up to five matches.
