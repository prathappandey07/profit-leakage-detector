"""Core engine for the Small Business Profit Leakage Detector.

Pipeline: load -> clean -> compute -> summarise -> diagnose.
Uses only pandas / numpy so it is easy to explain in the presentation.
"""
import pandas as pd

# Leak as % of gross sales -> risk label
RISK_BANDS = [(10, "High Risk"), (4, "Medium Risk"), (0, "Low Risk")]


# ----------------------------------------------------------------- 1. LOAD + CLEAN
def load_and_clean(sales_path="sales.csv", exp_path="expenses.csv"):
    sales = pd.read_csv(sales_path)
    exp = pd.read_csv(exp_path)

    report = {"rows_before": len(sales)}
    report["blank_cells"] = int(sales.isna().sum().sum())

    # fix types
    sales["date"] = pd.to_datetime(sales["date"], errors="coerce")
    exp["date"] = pd.to_datetime(exp["date"], errors="coerce")
    for col in ["qty", "list_price", "discount_pct", "unit_cost"]:
        sales[col] = pd.to_numeric(sales[col], errors="coerce")

    # duplicates
    report["duplicates_removed"] = int(sales.duplicated().sum())
    sales = sales.drop_duplicates()

    # drop rows missing identifiers, fill numeric blanks
    sales = sales.dropna(subset=["date", "product"])
    sales["qty"] = sales["qty"].fillna(sales["qty"].median())
    sales["discount_pct"] = sales["discount_pct"].fillna(sales["discount_pct"].median())
    exp = exp.dropna(subset=["date", "category", "amount"])

    report["rows_after"] = len(sales)

    # derived money columns
    sales["month"] = sales["date"].dt.to_period("M").astype(str)
    exp["month"] = exp["date"].dt.to_period("M").astype(str)
    sales["gross_sales"] = sales["qty"] * sales["list_price"]
    sales["discount_amt"] = sales["gross_sales"] * sales["discount_pct"]
    sales["revenue"] = sales["gross_sales"] - sales["discount_amt"]
    sales["cogs"] = sales["qty"] * sales["unit_cost"]
    sales["gross_profit"] = sales["revenue"] - sales["cogs"]
    return sales, exp, report


# ----------------------------------------------------------------- 2. SUMMARIES
def monthly_summary(sales, exp):
    s = sales.groupby("month").agg(
        gross_sales=("gross_sales", "sum"),
        discounts=("discount_amt", "sum"),
        revenue=("revenue", "sum"),
        cogs=("cogs", "sum"),
    )
    e = exp.pivot_table(index="month", columns="category", values="amount", aggfunc="sum").fillna(0)
    m = s.join(e)
    m["total_expenses"] = e.sum(axis=1)
    m["net_profit"] = m["revenue"] - m["cogs"] - m["total_expenses"]
    m["net_margin_pct"] = 100 * m["net_profit"] / m["revenue"]
    m["discount_rate_pct"] = 100 * m["discounts"] / m["gross_sales"]
    return m


def _month_slice(sales, exp, month):
    if month in (None, "All"):
        return sales, exp
    return sales[sales["month"] == month], exp[exp["month"] == month]


# ----------------------------------------------------------------- 3. WATERFALL
def waterfall_items(sales, exp, month=None):
    """Gross sales -> minus each leak -> net profit."""
    s, e = _month_slice(sales, exp, month)
    items = [("Gross Sales", s["gross_sales"].sum()),
             ("Discounts", -s["discount_amt"].sum()),
             ("Cost of Goods", -s["cogs"].sum())]
    by_cat = e.groupby("category")["amount"].sum().sort_values(ascending=False)
    items += [(c, -v) for c, v in by_cat.items()]
    net = sum(v for _, v in items)
    items.append(("Net Profit", net))
    return items


# ----------------------------------------------------------------- 4. LEAKAGE SCORE
def _risk(pct):
    for threshold, label in RISK_BANDS:
        if pct >= threshold:
            return label
    return "Low Risk"


def leakage_table(sales, exp, month=None):
    """Each leak as a % of gross sales, ranked, with a risk label."""
    s, e = _month_slice(sales, exp, month)
    gross = s["gross_sales"].sum()
    leaks = {"Discounts": s["discount_amt"].sum()}
    for cat, val in e.groupby("category")["amount"].sum().items():
        leaks[cat] = val
    loss_products = s.groupby("product")["gross_profit"].sum()
    leaks["Underpriced products (net loss)"] = -loss_products[loss_products < 0].sum()

    t = pd.DataFrame({"amount": pd.Series(leaks)})
    t["pct_of_gross_sales"] = 100 * t["amount"] / gross
    t["risk"] = t["pct_of_gross_sales"].apply(_risk)
    return t.sort_values("amount", ascending=False).round(2)


# ----------------------------------------------------------------- 5. PRODUCTS
def product_margins(sales, month=None):
    s = sales if month in (None, "All") else sales[sales["month"] == month]
    p = s.groupby("product").agg(
        gross_sales=("gross_sales", "sum"), revenue=("revenue", "sum"),
        cogs=("cogs", "sum"), gross_profit=("gross_profit", "sum"))
    p["margin_pct"] = 100 * p["gross_profit"] / p["revenue"]
    p["status"] = p["margin_pct"].apply(
        lambda x: "LOSS-MAKING" if x < 0 else ("Thin margin" if x < 8 else "Healthy"))
    return p.sort_values("margin_pct").round(2)


# ----------------------------------------------------------------- 6. AUTO INSIGHTS
def generate_insights(monthly, sales, exp):
    """Plain-English findings written by the code itself."""
    out = []
    months = list(monthly.index)
    if len(months) < 2:
        return out
    prev, last = months[-2], months[-1]
    p, l = monthly.loc[prev], monthly.loc[last]

    if p["net_profit"] > 0 and l["net_profit"] < 0:
        out.append(f"ALERT: the shop slipped from a profit of Rs {p['net_profit']:,.0f} in {prev} "
                   f"to a LOSS of Rs {abs(l['net_profit']):,.0f} in {last}.")
    else:
        change = 100 * (l["net_profit"] - p["net_profit"]) / abs(p["net_profit"])
        direction = "fell" if change < 0 else "rose"
        out.append(f"Net profit {direction} {abs(change):.0f}% from {prev} (Rs {p['net_profit']:,.0f}) "
                   f"to {last} (Rs {l['net_profit']:,.0f}).")

    # which cost line grew most, measured as % of gross sales
    drivers = {"Discounts": (100 * p["discounts"] / p["gross_sales"],
                             100 * l["discounts"] / l["gross_sales"])}
    for cat in exp["category"].unique():
        drivers[cat] = (100 * p.get(cat, 0) / p["gross_sales"], 100 * l.get(cat, 0) / l["gross_sales"])
    ranked = sorted(drivers.items(), key=lambda kv: kv[1][1] - kv[1][0], reverse=True)
    for name, (a, b) in ranked[:2]:
        if b - a > 0.2:
            out.append(f"{name} rose from {a:.1f}% to {b:.1f}% of gross sales "
                       f"between {prev} and {last} (a {b - a:.1f}-point leak increase).")

    bad = product_margins(sales, last)
    loss = bad[bad["status"] == "LOSS-MAKING"]
    for name, r in loss.iterrows():
        out.append(f"{name} lost Rs {abs(r['gross_profit']):,.0f} in {last} "
                   f"(margin {r['margin_pct']:.1f}%): selling below cost after discounts.")
    return out


# ----------------------------------------------------------------- 7. WHAT-IF
def what_if(sales, exp, month=None, discount_cut_pct=0, wastage_cut_pct=0, price_rise_pct=0):
    """Profit if discounts / wastage fall by the given % and prices rise."""
    s, e = _month_slice(sales, exp, month)
    base = (s["revenue"].sum() - s["cogs"].sum() - e["amount"].sum())
    new_discount = s["discount_amt"].sum() * (1 - discount_cut_pct / 100)
    new_gross = s["gross_sales"].sum() * (1 + price_rise_pct / 100)
    new_revenue = new_gross - new_discount * (1 + price_rise_pct / 100)
    wastage = e.loc[e["category"] == "Wastage", "amount"].sum()
    new_exp = e["amount"].sum() - wastage * wastage_cut_pct / 100
    new = new_revenue - s["cogs"].sum() - new_exp
    return {"base_profit": base, "new_profit": new, "gain": new - base}
