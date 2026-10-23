"""Generate the SIMULATED dataset for the B2B pricing & margin project.

Everything here is made up for practice. Costs and prices are rough, illustrative
numbers, not real OEM, distributor, or allwhere data.

Writes CSVs to data/: regions, categories, sku_master, price_book, orders.
"""
import math
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path(__file__).parent / "data"
OUT.mkdir(exist_ok=True)
rng = np.random.default_rng(42)

# ---------------------------------------------------------------- assumptions
regions = pd.DataFrame(
    [
        # region, currency, fx (local per USD), duty, fx buffer, freight laptop/monitor/accessory (USD per unit)
        ("US", "USD", 1.00, 0.00, 0.00, 18, 25, 6),
        ("UK", "GBP", 0.79, 0.00, 0.02, 42, 55, 12),
        ("DE", "EUR", 0.92, 0.00, 0.02, 38, 50, 11),
        ("CA", "CAD", 1.37, 0.00, 0.02, 30, 40, 9),
        ("IN", "INR", 83.50, 0.11, 0.02, 55, 70, 15),
    ],
    columns=["region", "currency", "fx_book", "duty_pct", "fx_buffer_pct",
             "freight_laptop", "freight_monitor", "freight_accessory"],
)

categories = pd.DataFrame(
    # list headroom = room for normal negotiation built into the list price
    [("Laptop", 0.12, 0.08, 0.03), ("Monitor", 0.18, 0.12, 0.04), ("Accessory", 0.32, 0.22, 0.05)],
    columns=["category", "target_margin", "floor_margin", "list_headroom_pct"],
)

# sku, oem, model, category, tier, lifecycle, vendor cost USD, base OEM rebate, demand weight
skus = [
    ("L01", "Apple", "MacBook Air 13 M3 16GB/512GB", "Laptop", "Mainstream", "Active", 1180, 0.010, 18),
    ("L02", "Apple", "MacBook Pro 14 M3 Pro 18GB/512GB", "Laptop", "Premium", "Active", 1780, 0.010, 12),
    ("L03", "Apple", "MacBook Pro 16 M3 Max 36GB/1TB", "Laptop", "Premium", "Active", 2950, 0.010, 3),
    ("L04", "Dell", "Latitude 5450 i5/16GB/512GB", "Laptop", "Mainstream", "Active", 980, 0.030, 10),
    ("L05", "Dell", "Latitude 7450 i7/16GB/512GB", "Laptop", "Premium", "Active", 1320, 0.030, 6),
    ("L06", "Dell", "XPS 13 9340 Ultra 7/16GB/512GB", "Laptop", "Premium", "Active", 1150, 0.020, 9),
    ("L07", "Lenovo", "ThinkPad T14 Gen 5 i5/16GB/512GB", "Laptop", "Mainstream", "Active", 1010, 0.035, 12),
    ("L08", "Lenovo", "ThinkPad X1 Carbon Gen 12 i7/32GB/1TB", "Laptop", "Premium", "Active", 1520, 0.035, 10),
    ("L09", "Lenovo", "ThinkPad E14 Gen 6 i5/16GB/256GB", "Laptop", "Entry", "Active", 720, 0.020, 4),
    ("L10", "HP", "EliteBook 840 G11 Ultra 5/16GB/512GB", "Laptop", "Mainstream", "Active", 1180, 0.030, 7),
    ("L11", "HP", "ProBook 450 G10 i5/16GB/256GB", "Laptop", "Entry", "Active", 780, 0.020, 3),
    ("L12", "Microsoft", "Surface Laptop 6 Ultra 5/16GB/256GB", "Laptop", "Premium", "Active", 1250, 0.015, 3),
    ("L13", "Acer", "TravelMate P4 i5/16GB/512GB", "Laptop", "Mainstream", "Active", 890, 0.000, 0.3),
    ("L14", "ASUS", "ExpertBook B5 i5/16GB/512GB", "Laptop", "Mainstream", "Active", 940, 0.000, 0.3),
    ("L15", "Dell", "Latitude 5440 i5/16GB/512GB (prev. gen)", "Laptop", "Mainstream", "EOL", 900, 0.030, 4),
    ("M01", "Dell", "P2425H 24in FHD", "Monitor", "24in", "Active", 165, 0.020, 30),
    ("M02", "Dell", "U2724D 27in QHD", "Monitor", "27in", "Active", 340, 0.020, 25),
    ("M03", "LG", "27UP850-W 27in 4K", "Monitor", "27in", "Active", 330, 0.010, 10),
    ("M04", "Lenovo", "ThinkVision T27h-30 27in QHD", "Monitor", "27in", "Active", 270, 0.020, 15),
    ("M05", "HP", "E24 G5 24in FHD", "Monitor", "24in", "Active", 160, 0.020, 15),
    ("M06", "Samsung", "ViewFinity S6 27in QHD", "Monitor", "27in", "Active", 290, 0.000, 0.6),
    ("A01", "Dell", "WD22TB4 Thunderbolt Dock", "Accessory", "Dock", "Active", 215, 0.020, 20),
    ("A02", "CalDigit", "TS4 Thunderbolt Dock", "Accessory", "Dock", "Active", 300, 0.000, 1.5),
    ("A03", "Logitech", "MX Keys S Keyboard", "Accessory", "Keyboard", "Active", 80, 0.000, 15),
    ("A04", "Logitech", "MX Master 3S Mouse", "Accessory", "Mouse", "Active", 70, 0.000, 18),
    ("A05", "Apple", "Magic Keyboard with Touch ID", "Accessory", "Keyboard", "Active", 115, 0.000, 8),
    ("A06", "Jabra", "Evolve2 65 Headset", "Accessory", "Headset", "Active", 165, 0.010, 14),
    ("A07", "Poly", "Voyager 4320 Headset", "Accessory", "Headset", "Active", 120, 0.000, 1),
    ("A08", "Generic", "15in Laptop Backpack", "Accessory", "Bag", "Active", 28, 0.000, 10),
    ("A09", "Anker", "100W USB-C Charger", "Accessory", "Power", "Active", 38, 0.000, 8),
]
sku_master = pd.DataFrame(
    skus, columns=["sku", "oem", "model", "category", "tier", "lifecycle",
                   "vendor_cost_usd", "base_rebate_pct", "demand_weight"])

# ---------------------------------------------------------------- price book
# Same math as the Price_Book sheet in Excel.
def freight(region_row, category):
    return region_row[f"freight_{category.lower()}"]

rows = []
for _, s in sku_master.iterrows():
    cat = categories.set_index("category").loc[s.category]
    for _, r in regions.iterrows():
        net = s.vendor_cost_usd * (1 - s.base_rebate_pct)
        landed = net * (1 + r.duty_pct) + freight(r, s.category)
        target_usd = landed / (1 - cat.target_margin)
        list_local = math.ceil(round(target_usd * (1 + cat.list_headroom_pct) * (1 + r.fx_buffer_pct) * r.fx_book / 5, 9)) * 5
        floor_local = landed / (1 - cat.floor_margin) * (1 + r.fx_buffer_pct) * r.fx_book
        rows.append((s.sku, r.region, landed, list_local, floor_local))
price_book = pd.DataFrame(rows, columns=["sku", "region", "book_landed_cost_usd",
                                         "list_price_local", "floor_price_local"])

# ---------------------------------------------------------------- customers
cust_regions = rng.choice(["US", "UK", "DE", "CA", "IN"], size=40, p=[0.5, 0.15, 0.15, 0.1, 0.1])
segments = np.array(["Enterprise"] * 8 + ["Mid-market"] * 14 + ["SMB"] * 18)
rng.shuffle(segments)
reps = [f"R0{i}" for i in range(1, 7)]
customers = pd.DataFrame({
    "customer_id": [f"C{i:03d}" for i in range(1, 41)],
    "segment": segments,
    "region": cust_regions,
    "rep": [reps[i % 6] for i in range(40)],
})
# Rep R04 owns most Enterprise accounts -> the over-discounting story.
ent = customers.index[customers.segment == "Enterprise"]
customers.loc[ent[:5], "rep"] = "R04"

# ---------------------------------------------------------------- FX paths (actual)
months = pd.period_range("2025-10", "2026-09", freq="M")
def fx_actual(region, m):
    noise = rng.normal(0, 1)
    if region == "US":
        return 1.0
    if region == "UK":   # GBP weakens from March 2026
        return 0.79 + 0.006 * max(0, m - 4) + 0.002 * noise
    if region == "DE":
        return 0.92 + 0.003 * max(0, m - 5) + 0.002 * noise
    if region == "CA":
        return 1.37 + 0.008 * noise
    return 83.5 + 0.15 * m + 0.2 * noise   # IN

fx_by_month = {(reg, m): fx_actual(reg, m) for reg in regions.region for m in range(12)}

# Cost drift: OEM raised vendor cost 6% from April 2026 (month index 6), price book never updated.
COST_UP = {"L06": 0.06, "L10": 0.06}
# India: freight forwarder costs ~35% above the book assumption all year.
IN_FREIGHT_ACTUAL = {"Laptop": 75, "Monitor": 90, "Accessory": 20}

qty_range = {"SMB": (2, 10), "Mid-market": (5, 30), "Enterprise": (15, 80)}
disc_range = {"SMB": (0.0, 0.02), "Mid-market": (0.01, 0.045), "Enterprise": (0.02, 0.045)}

pb = price_book.set_index(["sku", "region"])
sm = sku_master.set_index("sku")
cat_tbl = categories.set_index("category")
reg_tbl = regions.set_index("region")

def pick(category, m):
    sub = sku_master[sku_master.category == category].copy()
    w = sub.demand_weight.values.astype(float)
    w[(sub.lifecycle == "EOL").values] *= 1.0 if m < 5 else 0.0   # EOL model stops selling
    return rng.choice(sub.sku.values, p=w / w.sum())

lines = []
order_no = 0
for m, period in enumerate(months):
    for _ in range(rng.poisson(70)):
        order_no += 1
        c = customers.iloc[rng.integers(0, 40)]
        day = int(rng.integers(1, period.days_in_month + 1))
        date = f"{period.year}-{period.month:02d}-{day:02d}"
        cats = ["Laptop"]
        if rng.random() < 0.55:
            cats.append("Monitor")
        if rng.random() < 0.70:
            cats.append("Accessory")
        base_qty = int(rng.integers(*qty_range[c.segment]))
        for ln, cat in enumerate(cats, start=1):
            sku = pick(cat, m)
            qty = base_qty if cat == "Laptop" else max(1, int(base_qty * rng.uniform(0.4, 1.2)))
            book = pb.loc[(sku, c.region)]
            disc = rng.uniform(*disc_range[c.segment])
            if c.rep == "R04" and rng.random() < 0.6:
                disc += rng.uniform(0.02, 0.05)       # over-discounting
            quoted = round(book.list_price_local * (1 - disc), 2)
            # Was a special-price approval logged? (only meaningful when the quote breaks the floor)
            breaks_floor = quoted < book.floor_price_local
            p_ok = 0.2 if c.rep == "R04" else 0.75
            approval = "Y" if (breaks_floor and rng.random() < p_ok) else "N"

            s = sm.loc[sku]
            r = reg_tbl.loc[c.region]
            vendor_actual = s.vendor_cost_usd * (1 + (COST_UP.get(sku, 0) if m >= 6 else 0))
            fr = IN_FREIGHT_ACTUAL[cat] if c.region == "IN" else r[f"freight_{cat.lower()}"]
            actual_landed = vendor_actual * (1 - s.base_rebate_pct) * (1 + r.duty_pct) + fr
            lines.append({
                "order_id": f"SO-{order_no:05d}", "line_no": ln, "order_date": date,
                "month": str(period), "customer_id": c.customer_id, "segment": c.segment,
                "rep": c.rep, "region": c.region, "sku": sku, "qty": qty,
                "list_price_local": book.list_price_local, "quoted_price_local": quoted,
                "approval_logged": approval, "fx_book": r.fx_book,
                "fx_actual": round(fx_by_month[(c.region, m)], 4),
                "book_landed_cost_usd": round(book.book_landed_cost_usd, 2),
                "actual_landed_cost_usd": round(actual_landed, 2),
            })

orders = pd.DataFrame(lines)

regions.to_csv(OUT / "regions.csv", index=False)
categories.to_csv(OUT / "categories.csv", index=False)
sku_master.drop(columns="demand_weight").to_csv(OUT / "sku_master.csv", index=False)
price_book.round(2).to_csv(OUT / "price_book.csv", index=False)
orders.to_csv(OUT / "orders.csv", index=False)
print(f"{len(orders):,} order lines, {orders.order_id.nunique():,} orders")
