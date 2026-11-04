# Resolve a product reference and handle an unsupported accessory.

Mode: offline (deterministic).
Session: guest.

**Customer**

How much is the Takamine GD20?

**Assistant**

- Takamine GD20 Dreadnought Natural: BRL 2199.00 — available
Source: supplied product snapshot. Prices do not reserve stock.

**Tools called during this turn**

- `get_product({"payment": "table", "product_id": 95})`

**Customer**

Is that one available?

**Assistant**

- Takamine GD20 Dreadnought Natural: BRL 2199.00 — available
Source: supplied product snapshot. Prices do not reserve stock.

**Tools called during this turn**

- `get_product({"payment": "table", "product_id": 95})`

**Customer**

Do you sell cables?

**Assistant**

We specialize in musical instruments and do not sell cables, picks, replacement strings, cases, pedals or amplifiers. I can help you find an instrument. [Store policy, page 2]

**Tools called during this turn**

- `search_policies({"query": "accessories"})`

## Evidence

products.csv, promotions.csv and politicas_da_loja.pdf, page 2

The follow-up uses the selected model. The accessory question switches to the store policy on which items it sells.
