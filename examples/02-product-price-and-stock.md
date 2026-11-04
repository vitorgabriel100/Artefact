# Check a named instrument and its price when paying by PIX.

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

And with PIX?

**Assistant**

- Takamine GD20 Dreadnought Natural: BRL 2089.05 — available (regular BRL 2199.00; 5% pix discount)
Source: supplied product snapshot. Prices do not reserve stock.

**Tools called during this turn**

- `get_product({"payment": "pix", "product_id": 95})`

## Evidence

products.csv and promotions.csv

The second turn reuses the selected product ID. The pricing tool computes the discount and returns the exact amount in BRL.
