"""Run the full analysis from the command line and save charts as PNGs.

Usage:  python run_analysis.py
Outputs: console report + output/*.png (use these as screenshots in your report/PPT)
"""
import os
import pandas as pd
import analysis as a
import charts as c

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 30)
os.makedirs("output", exist_ok=True)

sales, exp, report = a.load_and_clean()
monthly = a.monthly_summary(sales, exp)
latest = monthly.index[-1]

print("=== DATA CLEANING REPORT ===")
for k, v in report.items():
    print(f"{k}: {v}")

print("\n=== MONTHLY SUMMARY ===")
print(monthly[["gross_sales", "discounts", "revenue", "cogs", "total_expenses",
               "net_profit", "net_margin_pct", "discount_rate_pct"]].round(1))

print(f"\n=== LEAKAGE SCORE ({latest}) ===")
leak = a.leakage_table(sales, exp, latest)
print(leak)

print(f"\n=== PRODUCT MARGINS ({latest}) ===")
pm = a.product_margins(sales, latest)
print(pm[["margin_pct", "status"]])

print("\n=== AUTO INSIGHTS ===")
for line in a.generate_insights(monthly, sales, exp):
    print("-", line)

print("\n=== WHAT-IF: cut discounts 30% and wastage 50% ===")
w = a.what_if(sales, exp, latest, discount_cut_pct=30, wastage_cut_pct=50)
print(f"Profit now Rs {w['base_profit']:,.0f} -> Rs {w['new_profit']:,.0f} (gain Rs {w['gain']:,.0f})")

c.waterfall(a.waterfall_items(sales, exp, latest), f"Where did the money go? ({latest})").savefig("output/1_waterfall.png", dpi=150)
c.monthly_trend(monthly).savefig("output/2_trend.png", dpi=150)
c.leakage_bar(leak).savefig("output/3_leakage_score.png", dpi=150)
c.product_margin_bar(pm).savefig("output/4_product_margins.png", dpi=150)
print("\nCharts saved in output/")
