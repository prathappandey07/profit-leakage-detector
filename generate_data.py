"""Generate sample sales and expense data for 'Sai Fresh Mart' (Aug-Oct 2026).

The data is deliberately built with realistic leaks so the detector has
something to find:
  * discounts creep up every month (6% -> 10% -> 16%)
  * wastage (spoiled milk / bread) rises sharply in October
  * a few products are priced too close to cost, so discounts make them loss-making
  * a few blank cells and one duplicated row, to show data cleaning
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)

# product, category, list_price, unit_cost, avg daily qty
PRODUCTS = [
    ("Basmati Rice 5kg", "Grocery", 470, 300, 6),
    ("Sunflower Oil 1L", "Grocery", 160, 105, 12),
    ("Sugar 1kg", "Grocery", 48, 45, 25),       # priced too close to cost -> loss after discount
    ("Toor Dal 1kg", "Grocery", 150, 95, 10),
    ("Milk 1L", "Dairy", 60, 38, 40),
    ("Curd 500g", "Dairy", 40, 24, 18),
    ("Bread", "Bakery", 40, 22, 22),
    ("Biscuits Pack", "Snacks", 10, 5.5, 60),
    ("Egg Tray (30)", "Dairy", 158, 146, 8),     # priced too close to cost -> loss after discount
    ("Soap Bar", "Personal Care", 45, 22, 20),
]

# month -> average discount rate (creeps up every month)
DISC = {8: 0.04, 9: 0.07, 10: 0.11}

rows = []
for day in pd.date_range("2026-08-01", "2026-10-31"):
    for name, cat, lp, uc, avg_qty in PRODUCTS:
        if rng.random() < 0.08:          # product not sold that day
            continue
        qty = max(1, int(rng.normal(avg_qty, avg_qty * 0.25)))
        disc = max(0.0, rng.normal(DISC[day.month], 0.03))
        # Basmati rice and soap get no extra discount in the first month
        rows.append([day.date(), name, cat, qty, lp, round(disc, 3), uc])

sales = pd.DataFrame(
    rows,
    columns=["date", "product", "category", "qty", "list_price", "discount_pct", "unit_cost"],
)

# messy-data realism: blanks + one duplicate row
sales.loc[sales.sample(6, random_state=1).index, "discount_pct"] = np.nan
sales.loc[sales.sample(4, random_state=2).index, "qty"] = np.nan
sales = pd.concat([sales, sales.iloc[[10]]], ignore_index=True)

# ---------- expenses ----------
exp_rows = []
monthly = {
    8: {"Rent": 18000, "Salaries": 30000, "Electricity": 6500, "Transport": 9000,
        "Packaging": 3500, "Marketing": 4000},
    9: {"Rent": 18000, "Salaries": 30000, "Electricity": 7000, "Transport": 9500,
        "Packaging": 3800, "Marketing": 5000},
    10: {"Rent": 18000, "Salaries": 30000, "Electricity": 7800, "Transport": 10500,
         "Packaging": 4200, "Marketing": 5500},
}
for m, items in monthly.items():
    for cat, amt in items.items():
        exp_rows.append([f"2026-{m:02d}-01", cat, amt, "monthly"])

# wastage logged weekly (spoiled/expired stock written off)
wastage_per_week = {8: 1500, 9: 1900, 10: 3000}
for d in pd.date_range("2026-08-03", "2026-10-31", freq="7D"):
    amt = int(rng.normal(wastage_per_week[d.month], 250))
    exp_rows.append([d.date().isoformat(), "Wastage", amt, "weekly write-off"])

expenses = pd.DataFrame(exp_rows, columns=["date", "category", "amount", "note"])

sales.to_csv("sales.csv", index=False)
expenses.to_csv("expenses.csv", index=False)
print(f"sales.csv: {len(sales)} rows | expenses.csv: {len(expenses)} rows")
